class InstructionLoader:
    def __init__(self):
        self.mongo_instructions = """
            🚫 STRICT CONSTRAINTS:
            - Use only the exact collection names provided in the schema. Do NOT pluralize, rename, guess, or hallucinate table names.
            - Do NOT make assumptions about foreign keys or implicit relationships unless they are explicitly defined in the schema.
            - Always verify that every field used in the query exists in the corresponding collection schema.
            - If the field or collection is not found, return an empty string "".
            - Field names and collection names are **case-sensitive** and must match exactly.


            ✅ MONGODB SYNTAX RULES:
            - Always use db.<collection> format.
            - Enclose all field names and string values in double quotes ("").
            - Return only plain MongoDB shell-style queries (no markdown, no comments, no explanations).
            - All output must have balanced braces and valid syntax.

            ✅ SUPPORTED OPERATIONS:

            1. 🔎 Basic Retrieval (find()):
            - Return all fields → db.collection.find({}, {})
            - Return specific fields → db.collection.find({}, { "field1": 1, "field2": 1, "_id": 0 })

            2. 🎯 Filtering (WHERE):
            - Equality: "field": "value"
            - Comparison: { "$gt": value }, { "$lt": value }, { "$gte": value }, { "$lte": value }
            - Date filtering use ISODate() unless schema defines date type explicitly.

            3. 📊 Aggregation (aggregate):
            - Use stages: $match, $group, $sum, $count, $project, $sort, $limit, $skip
            - Use $match as early as possible to reduce the size of intermediate results.
            - Always include _id in $group: e.g., { "_id": "$movie_id" }
            - Ensure logical accuracy of joins by matching fields like movie_id, director_id
            - Example: db.collection.aggregate([{ "$group": { "_id": "$movie_id", "count": { "$sum": 1 } } }])

            4. 🔁 Joins using $lookup:
            - Always use efficient joins with $lookup based on matching id fields.
            - Use $lookup **only** if fields from multiple collections are required to answer the query.
            - Before using $lookup, check if all requested fields are available in a single collection.
            - Do NOT use $lookup when all required fields are present in the current collection.
            - Avoid unnecessary $unwind unless filtering or projecting array elements.
            - Prefer $project to limit the output fields to only what is needed.
            - Use $unwind after $lookup if accessing nested fields.
            - Example:
            {
                "$lookup": {
                "from": "orders",
                "localField": "customer_id",
                "foreignField": "customer_id",
                "as": "orders"
                }
            }

            5. 🧾 Sorting and Pagination:
            - Apply limit, sort, and group only where appropriate.
            - Sort by field → .sort({ "field": 1 }) for ascending, -1 for descending
            - Limit results → .limit(n)
            - Skip results → .skip(n)

            6. ✍️ Data Modification:
            - Insert:
            - Use db.collection.insertOne({ ... }) for single document
            - Use db.collection.insertMany([{ ... }, { ... }]) for multiple documents
            - Only use field names that exist in the collection's schema
            - Do NOT create or insert fake values like "newId", "newBrandId", "newCategoryId", etc.
            - If a required field is not mentioned by the user, fill it with:
                - `null` for unknown values
                - `""` for missing text values
            - Do NOT include generated placeholder values, random IDs, or names unless explicitly provided
            - Example:
                Input: "Add a new product named Trek Speed with price 1500 and model year 2023"
                Output:
                db.products.insertOne({
                "product_id": null,
                "product_name": "Trek Speed",
                "list_price": 1500,
                "model_year": 2023,
                "brand_id": null,
                "category_id": null
                })
            - Update:
            - db.collection.updateOne({ filter }, { "$set": { field: value } })
            - db.collection.updateMany(...) for multiple documents
            - Delete:
            - db.collection.deleteOne({ filter })
            - db.collection.deleteMany(...) for multiple deletions
            - Return shell-like response (acknowledged, matchedCount, etc.)

            ✅ SCHEMA EXPLORATION:
            - If the user asks "What collections exist?" → return: db.getCollectionNames()
            - If the user asks for sample data, example records, or a preview from a collection:
            → return: db.<collection>.find({}).limit(5)
            - This should retrieve 5 sample rows (documents) from the collection.
            - Do NOT add any filters or projections — just return the top 5 documents using limit(5).

            ⚠️ Do not invent new fields from synonyms. Use them only to map user intent to existing fields in the current schema.
            """
