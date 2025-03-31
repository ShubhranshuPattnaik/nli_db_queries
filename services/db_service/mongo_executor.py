# from pymongo import MongoClient
# from config.config import Config
# import json

# class MongoExecutor:
#     def __init__(self):
#         self.client = MongoClient(Config.MONGODB["host"], Config.MONGODB["port"])
#         self.db = self.client[Config.MONGODB["database"]]

#     def execute_query(self, query):
#         try:
#             collection_name = query.split(".find(")[0].split("db.")[1]
#             collection = self.db[collection_name]
#             query_json = query.split("find(")[1][:-1]
#             query_dict = json.loads(query_json.replace("'", '"'))
#             results = collection.find(query_dict)
#             return list(results)
#         except Exception as e:
#             return {"error": str(e)}

# mongo_executor = MongoExecutor()
