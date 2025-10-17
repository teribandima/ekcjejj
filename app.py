import pymongo
import json
from pymongo.errors import ConnectionFailure

try:
    client = pymongo.MongoClient(
        "mongodb+srv://elvishyadav_opm:naman1811421@cluster0.uxuplor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
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
    # Fetch all documents from the educators collection
    educators = list(educators_col.find())
    
    # Convert to JSON with proper handling of MongoDB types
    def convert_to_jsonable(data):
        if isinstance(data, dict):
            return {k: convert_to_jsonable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_to_jsonable(item) for item in data]
        elif isinstance(data, pymongo.collection.ObjectId):
            return str(data)
        else:
            return data

    json_data = convert_to_jsonable(educators)
    
    # Print JSON with proper formatting
    print(json.dumps(json_data, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"Error fetching data: {str(e)}")

client.close()
