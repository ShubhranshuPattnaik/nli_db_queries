import re
import ast
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

            # Remove JS-style comments
            query = re.sub(r"//.*(?=\n|$)", "", query)
            # Flatten newlines
            query = query.replace("\n", " ").replace("\r", "").strip()

            print("📥 Received query:", query)

            match = re.match(
                r"db\.([a-zA-Z0-9_]+)\.(.+)$", query.strip(), re.DOTALL
            )
            if not match:
                return {
                    "error": "Invalid query format. Expected: db.collection.method(...) chain"
                }

            collection_name = match.group(1)
            operation_chain = match.group(2)
            coll = db[collection_name]

            ops = self._parse_method_chain(operation_chain)
            if not ops:
                return {"error": "No operations found in the query."}

            method = ops[0][0]

            if method == "find":
                return self._execute_find_chain(coll, ops)
            elif method == "aggregate":
                return self._execute_aggregate(coll, ops[0][1])
            elif method in [
                "insertOne",
                "insertMany",
                "updateOne",
                "updateMany",
                "deleteOne",
                "deleteMany",
            ]:
                return self._execute_simple_op(coll, method, ops[0][1])
            elif method == "countDocuments":
                return self._execute_count_documents(coll, ops[0][1])
            elif method == "distinct":
                return self._execute_distinct(coll, ops[0][1])
            else:
                return {"error": f"Unsupported root operation: {method}"}

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

    def _parse_method_chain(self, chain: str) -> List[Tuple[str, List[Any]]]:
        """
        Parses chained Mongo-style calls like:
        db.movies.aggregate([{'$match': {'genre': 'Drama'}}])
        Even when using single quotes or shell-style formatting.
        Returns: [('aggregate', [list_of_dicts])]
        """
        pattern = r"([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)"
        matches = re.findall(pattern, chain, re.DOTALL)

        parsed: List[Tuple[str, List[Any]]] = []
        for method, arg_str in matches:
            cleaned_args = self._normalize_quotes(arg_str.strip())
            try:
                args: List[Any] = (
                    ast.literal_eval(f"[{cleaned_args}]")
                    if cleaned_args
                    else []
                )
            except Exception as e:
                raise ValueError(
                    f"Failed to parse `{method}` args: {arg_str}\n{e}"
                )
            parsed.append((method, args))
        return parsed

    def _normalize_quotes(self, s: str) -> str:
        """
        Converts single-quoted Mongo shell strings to valid Python-style double-quoted strings.
        Preserves things like $ and $$ variable references.
        """
        # Replace outer single quotes with double quotes
        s = re.sub(r"(?<!\")'(.*?)'(?!\")", r'"\1"', s)

        # Unescape $ symbols that may have been affected
        s = s.replace('\\"$', "$").replace('\\"$$', "$$")
        return s


mongo_executor = MongoExecutor()

# query1 = "db.movies_genres.countDocuments({'genre': 'Horror'})"

# query2 = "db.movies_genres.distinct('genre')"

# insert_query = "db.movies_genres.insertOne({'movie_id': 'tt_test_001', 'genre': 'Mystery'})"

# update_query = "db.movies_genres.updateOne({'movie_id': {'$regex': '^tt_test_'}}, {'$set': {'genre': 'Experimental'}})"

# find_query = "db.movies_genres.find({'genre': 'Experimental'})"

# rollback_update_query = "db.movies_genres.updateOne({'movie_id': 'tt_test_001'}, {'$set': {'genre': 'Mystery'}})"

# delete_query = "db.movies_genres.deleteOne({'movie_id': 'tt_test_001'})"

query = 'db.movies.aggregate([\n    {\n        $lookup: {\n            from: "movies_directors",\n            localField: "id",\n            foreignField: "movie_id",\n            as: "directed_movies"\n        }\n    },\n    {\n        $unwind: "$directed_movies"\n    },\n    {\n        $lookup: {\n            from: "directors",\n            localField: "directed_movies.director_id",\n            foreignField: "id",\n            as: "director_info"\n        }\n    },\n    {\n        $match: { "director_info.first_name": "Christopher", "director_info.last_name": "Nolan" }\n    },\n    {\n        $lookup: {\n            from: "movies_genres",\n            localField: "_id",\n            foreignField: "movie_id",\n            as: "genres"\n        }\n    },\n    {\n        $unwind: "$genres"\n    },\n    {\n        $limit: 10\n    }\n])'

result = mongo_executor.execute_query(query=query, db_name="imdb_ijs")

# for doc in result:
#     print(doc)

print(f"{(result)} results returned.\n")
