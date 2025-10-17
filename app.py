import pymongo
from pymongo.errors import ConnectionFailure
import os

try:
    client = pymongo.MongoClient(
        os.environ.get('MONGO_URI', "mongodb+srv://elvishyadav_opm:naman1811421@cluster0.uxuplor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"),
        serverSelectionTimeoutMS=5000
    )
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except ConnectionFailure:
    print("Failed to connect to MongoDB. Please check your connection string or network.")
    exit(1)

db = client["unacademy_db"]
educators_col = db["educators"]

try:
    # Create text indexes for search optimization
    educators_col.create_index([("first_name", pymongo.TEXT)])
    educators_col.create_index([("last_name", pymongo.TEXT)])
    educators_col.create_index([("courses.name", pymongo.TEXT)])
    educators_col.create_index([("batches.name", pymongo.TEXT)])
    print("Indexes created successfully!")
except Exception as e:
    print(f"Error creating indexes: {str(e)}")

client.close()
