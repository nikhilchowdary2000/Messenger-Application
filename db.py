from pymongo import MongoClient
db_connection = MongoClient("mongodb://localhost:27017")
db = db_connection.Facebook
users_collection = db["users"]
messages_collection = db["messages"]
