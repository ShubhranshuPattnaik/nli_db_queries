import re
import json
import json5
from bson import json_util
from pymongo import MongoClient, collection
from config.config import Config
from typing import Any, List, Tuple, Dict, Optional, Union


class MongoExecutor:
    def __init__(self) -> None:
        self.client: MongoClient = MongoClient(
            Config.MONGODB["host"],
            Config.MONGODB["port"],
        )
        self.max_preview_docs: int = 50

    def execute_query(
        self, query: str, db_name: str
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], int]:
        try:
            db = self.client[db_name]

            # # Remove JS-style comments
            # query = re.sub(r"//.*(?=\n|$)", "", query)
            # # Flatten newlines
            # query = query.replace("\n", " ").replace("\r", "").strip()

            # Support raw 'show collections' instruction
            if query.strip().lower() == "show collections":
                return self._execute_show_collections(db_name)

            raw_query: str = self._extract_mongo_query(query)

            cleaned_query: str = self._sanitize_mongo_query_safe(raw_query)

            query = cleaned_query

            print("📥 Received query:", query)

            try:
                match = re.match(
                    r"db\.([a-zA-Z0-9_]+)\.(.+)$", query.strip(), re.DOTALL
                )
                if not match:
                    raise Exception(
                        {
                            "error": "Invalid query format. Expected: db.collection.method(...) chain"
                        }
                    )

                collection_name = match.group(1)
                operation_chain = match.group(2)

            except:
                db_prefix_pattern = re.compile(
                    r"db\.(\w+)\.(\w+)\.(.+)$"
                )  # db.imdb_ijs.actors.find(...)
                db_concat_pattern = re.compile(
                    r"db\.([a-zA-Z0-9_]+)\((.*?)\)"
                )  # fallback pattern
                fallback_pattern = re.compile(
                    r"db\.(\w+)(\w+)\.(.+)$"
                )  # db.imdb_ijsactors.find(...)

                match = db_prefix_pattern.match(query.strip())
                if match:
                    db_prefix, collection_name, operation_chain = match.groups()
                elif fallback_pattern.match(query.strip()):
                    db_name_and_coll, operation_chain = fallback_pattern.match(
                        query.strip()
                    ).groups()
                    # Try to split db + collection by checking known db names
                    for known_db in self.client.list_database_names():
                        if db_name_and_coll.startswith(known_db):
                            db_prefix = known_db
                            collection_name = db_name_and_coll[len(known_db) :]
                            break
                    else:
                        return {
                            "error": f"Unable to resolve DB + collection from: {db_name_and_coll}"
                        }
                elif re.match(r"db\.([a-zA-Z0-9_]+)\.(.+)$", query.strip()):
                    match = re.match(
                        r"db\.([a-zA-Z0-9_]+)\.(.+)$", query.strip()
                    )
                    collection_name = match.group(1)
                    operation_chain = match.group(2)
                    db_prefix = db_name  # Use provided db_name
                else:
                    return {
                        "error": "Invalid query format. Expected: db.collection.method(...) chain"
                    }

            coll = db[collection_name]

            ops = self._parse_method_chain(operation_chain)
            if not ops:
                return {"error": "No operations found in the query."}

            method = ops[0][0]

            if method == "find":
                result = self._execute_find_chain(coll, ops)
            elif method == "aggregate":
                result = self._execute_aggregate(coll, ops[0][1])
            elif method in [
                "insertOne",
                "insertMany",
                "updateOne",
                "updateMany",
                "deleteOne",
                "deleteMany",
            ]:
                result = self._execute_simple_op(coll, method, ops[0][1])
            elif method == "countDocuments":
                result = self._execute_count_documents(coll, ops[0][1])
            elif method == "distinct":
                result = self._execute_distinct(coll, ops[0][1])
            else:
                return {"error": f"Unsupported root operation: {method}"}

            return json.loads(json_util.dumps(result))

        except Exception as e:
            return {"error": str(e)}

    def _execute_find_chain(
        self, coll: collection.Collection, ops: List[Tuple[str, List[Any]]]
    ) -> List[Dict[str, Any]]:
        cursor = None
        for method, args in ops:
            if method == "find":
                if len(args) == 0:
                    cursor = coll.find()
                elif len(args) == 1:
                    cursor = coll.find(args[0])
                elif len(args) == 2:
                    cursor = coll.find(args[0], args[1])
                else:
                    raise ValueError("find() supports up to 2 arguments")
            else:
                if not cursor:
                    raise ValueError(f"{method}() called before find()")
                if hasattr(cursor, method):
                    cursor = getattr(cursor, method)(*args)
                else:
                    raise ValueError(f"Unsupported method chained: {method}")

        if not any(m[0] == "limit" for m in ops):
            print("📉 No limit in find chain — lazy stream")
            return [doc for _, doc in zip(range(self.max_preview_docs), cursor)]
        else:
            return list(cursor)

    def _execute_aggregate(
        self, coll: collection.Collection, args: List[Any]
    ) -> List[Dict[str, Any]]:
        pipeline = (
            args[0]
            if isinstance(args, list)
            and len(args) == 1
            and isinstance(args[0], list)
            else args
        )
        if not isinstance(pipeline, list):
            raise ValueError("aggregate() expects a list as its argument")
        print("⏳ Running aggregation pipeline:", pipeline)
        has_limit: bool = any("$limit" in stage for stage in pipeline)
        cursor = coll.aggregate(pipeline)
        if has_limit:
            return list(cursor)
        else:
            print("📉 No $limit in aggregation — lazy stream")
            return [doc for _, doc in zip(range(self.max_preview_docs), cursor)]

    def _execute_simple_op(
        self, coll: collection.Collection, method: str, args: List[Any]
    ) -> Any:
        print(f"⚙️ Executing {method} with args:", args)
        if method == "insertOne":
            return {"inserted_id": str(coll.insert_one(args[0]).inserted_id)}
        elif method == "insertMany":
            return {
                "inserted_ids": [
                    str(_id) for _id in coll.insert_many(args[0]).inserted_ids
                ]
            }
        elif method == "updateOne":
            return coll.update_one(*args).raw_result
        elif method == "updateMany":
            return coll.update_many(*args).raw_result
        elif method == "deleteOne":
            return coll.delete_one(*args).raw_result
        elif method == "deleteMany":
            return coll.delete_many(*args).raw_result
        else:
            return {"error": f"Unsupported operation: {method}"}

    def _execute_count_documents(
        self, coll: collection.Collection, args: List[Any]
    ) -> int:
        print("🔢 Running countDocuments with args:", args)
        if len(args) != 1:
            raise ValueError("countDocuments() requires exactly 1 argument")
        return coll.count_documents(args[0])

    def _execute_distinct(
        self, coll: collection.Collection, args: List[Any]
    ) -> List[Any]:
        print("🧪 Running distinct with args:", args)
        if not args:
            raise ValueError(
                "distinct() requires at least 1 argument (field name)"
            )
        field = args[0]
        query = args[1] if len(args) > 1 else {}
        return coll.distinct(field, query)

    def _execute_show_collections(self, db_name: str) -> List[str]:
        """
        Returns a list of collections in the given database,
        simulating 'show collections' in mongosh.
        """
        db = self.client[db_name]
        return db.list_collection_names()

    def _parse_method_chain(self, chain: str) -> List[Tuple[str, List[Any]]]:
        """
        Parses Mongo-style method chains like:
        db.collection.aggregate([...]) or db.collection.find({...})
        using a bracket-balanced parser instead of regex.

        Returns:
            List of (method_name, [args]) tuples
        """
        parsed: List[Tuple[str, List[Any]]] = []

        i = 0
        while i < len(chain):
            # Match method name
            method_match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", chain[i:])
            if not method_match:
                break

            method = method_match.group(1)
            i += method_match.end()

            # Parse arguments with parenthesis balance
            start = i
            depth = 1
            while i < len(chain) and depth > 0:
                if chain[i] == "(":
                    depth += 1
                elif chain[i] == ")":
                    depth -= 1
                i += 1

            arg_str = chain[start : i - 1].strip()
            cleaned_args = self._normalize_quotes(arg_str)
            json_str = f"[{cleaned_args}]"
            try:
                args: List[Any] = json5.loads(json_str)
            except Exception as e:
                raise ValueError(
                    f"Failed to parse `{method}` args: {arg_str}  cleaned_args: {cleaned_args}  error:  {e}"
                )
            parsed.append((method, args))

            # Skip any dot after the method call for chaining
            if i < len(chain) and chain[i] == ".":
                i += 1

        return parsed

    def _normalize_quotes(self, s: str) -> str:
        """
        Converts single-quoted Mongo shell strings to valid Python-style double-quoted strings.
        Preserves things like $ and $$ variable references.
        """
        # Replace outer single quotes with double quotes
        s = re.sub(r"(?<!\")'(.*?)'(?!\")", r'"\1"', s)

        # Fix ISODate() → {"$date": "..."}
        s = re.sub(
            r'ISODate\(\s*"(\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}\.\d{3}Z"\s*\)',
            lambda m: f'"{m.group(1)}-{m.group(2)}-{m.group(3)}"',
            s,
        )

        # Fix bad $$ references like {"$$var"} → "$$var"
        s = re.sub(r'{\s*"(\$\$[a-zA-Z0-9_\.]+)"\s*}', r'"\1"', s)

        # Unescape $ symbols that may have been affected
        s = s.replace('\\"$', "$").replace('\\"$$', "$$")
        return s

    def _extract_mongo_query(self, llm_response: str) -> str | None:
        """
        Extracts the MongoDB query string from the LLM's response.
        Handles various formats (code block, inline, raw JSON).
        Returns only the query as a string (e.g., db.collection.aggregate([...])).
        """
        if not llm_response:
            return None

        # 1. Try to extract code from triple backtick blocks (```mongodb ... ```)
        code_block_match = re.search(
            r"```(?:\w+)?\s*\n([\s\S]+?)```", llm_response, re.IGNORECASE
        )
        if code_block_match:
            code = code_block_match.group(1).strip()
            return code

        # 2. Try to find the first line that starts with `db.` and ends with a valid structure
        db_query_match = re.search(
            r"(db\.\w+\.(?:aggregate|find|insertOne|updateOne|deleteOne)\s*\([\s\S]+)",
            llm_response,
        )
        if db_query_match:
            return db_query_match.group(1).strip()

        # 3. Try extracting a JSON-like aggregation pipeline list
        pipeline_match = re.search(r"\[\s*{[\s\S]+?}\s*]", llm_response)
        if pipeline_match:
            # Assume "db.<collection>.aggregate(...)" or fallback to "paper" as default collection
            return f"db.paper.aggregate({pipeline_match.group(0).strip()})"

        # 4. Fallback: Check if response *is* the query directly
        stripped = llm_response.strip()
        if stripped.startswith("db.") and ("(" in stripped and ")" in stripped):
            return stripped

        return None

    def _sanitize_mongo_query_safe(self, query: str) -> str:
        if not query:
            return query

        # TEMPORARILY protect regex patterns like /pattern/ or /pattern/i
        regex_patterns = re.findall(r"/[^/]+/[a-z]*", query)
        for i, pat in enumerate(regex_patterns):
            query = query.replace(pat, f"__REGEX_PLACEHOLDER_{i}__")

        # Remove JS-style and block comments
        query = re.sub(r"//.*(?=\n|$)", "", query)
        query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)

        # Unescape quotes, remove semicolons
        query = query.replace('\\"', '"').replace(";", "")

        # Flatten to one line, normalize spaces
        query = query.replace("\n", " ").replace("\r", " ")
        query = re.sub(r"\s+", " ", query).strip()

        # Reinsert regex safely
        for i, pat in enumerate(regex_patterns):
            query = query.replace(f"__REGEX_PLACEHOLDER_{i}__", pat)

        return query


mongo_executor = MongoExecutor()

# query1 = "db.movies_genres.countDocuments({'genre': 'Horror'})"

# query2 = "db.movies_genres.distinct('genre')"

# insert_query = "db.movies_genres.insertOne({'movie_id': 'tt_test_001', 'genre': 'Mystery'})"

# update_query = "db.movies_genres.updateOne({'movie_id': {'$regex': '^tt_test_'}}, {'$set': {'genre': 'Experimental'}})"

# find_query = "db.movies_genres.find({'genre': 'Experimental'})"

# rollback_update_query = "db.movies_genres.updateOne({'movie_id': 'tt_test_001'}, {'$set': {'genre': 'Mystery'}})"

# delete_query = "db.movies_genres.deleteOne({'movie_id': 'tt_test_001'})"

# query = 'db.movies.aggregate([\n    {\n        $lookup: {\n            from: "movies_directors",\n            localField: "id",\n            foreignField: "movie_id",\n            as: "directed_movies"\n        }\n    },\n    {\n        $unwind: "$directed_movies"\n    },\n    {\n        $lookup: {\n            from: "directors",\n            localField: "directed_movies.director_id",\n            foreignField: "id",\n            as: "director_info"\n        }\n    },\n    {\n        $match: { "director_info.first_name": "Christopher", "director_info.last_name": "Nolan" }\n    },\n    {\n        $lookup: {\n            from: "movies_genres",\n            localField: "_id",\n            foreignField: "movie_id",\n            as: "genres"\n        }\n    },\n    {\n        $unwind: "$genres"\n    },\n    {\n        $limit: 10\n    }\n])'

# result = mongo_executor.execute_query(query=query, db_name="imdb_ijs")

# # for doc in result:
# #     print(doc)

# print(f"{(result)} results returned.\n")
