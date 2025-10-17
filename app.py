from flask import Flask, jsonify, request, Response
import pymongo
from pymongo.errors import ConnectionFailure
from bson.errors import InvalidId
from bson import ObjectId
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# MongoDB connection
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

@app.route('/data', methods=['GET'])
def get_educators_ids():
    try:
        # Pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))  # Default limit to 50 to reduce load
        skip = (page - 1) * limit
        
        # Fetch only _id fields
        cursor = educators_col.find({}, {'_id': 1}).skip(skip).limit(limit)
        ids = [str(doc['_id']) for doc in cursor]
        
        # Stream the response
        def generate_ids_stream():
            yield '{\n'
            yield '"status": "success",\n'
            yield f'"count": {len(ids)},\n'
            yield '"total": ' + str(educators_col.count_documents({})) + ',\n'
            yield '"page": ' + str(page) + ',\n'
            yield '"limit": ' + str(limit) + ',\n'
            yield '"data": [\n'
            first = True
            for id_str in ids:
                if not first:
                    yield ',\n'
                yield f'"{id_str}"'
                first = False
            yield '\n]\n'
            yield '}\n'

        return Response(generate_ids_stream(), mimetype='application/json')
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching IDs: {str(e)}'
        }), 500

@app.route('/data_id=<object_id>', methods=['GET'])
def get_educator_by_id(object_id):
    try:
        # Validate and convert object_id to ObjectId
        try:
            oid = ObjectId(object_id)
        except InvalidId:
            return jsonify({
                'status': 'error',
                'message': 'Invalid ObjectId format'
            }), 400
        
        # Fetch the educator document
        educator = educators_col.find_one({'_id': oid})
        if not educator:
            return jsonify({
                'status': 'error',
                'message': f'Educator with ID {object_id} not found'
            }), 404
        
        # Convert _id to string for JSON serialization, keep rest as raw
        educator['_id'] = str(educator['_id'])
        
        return jsonify({
            'status': 'success',
            'data': educator
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching educator data: {str(e)}'
        }), 500

@app.route('/search=<keyword>', methods=['GET'])
def search_educators(keyword):
    try:
        # Pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))  # Default limit to 50
        skip = (page - 1) * limit
        
        # Case-insensitive regex for keyword
        regex = {'$regex': keyword, '$options': 'i'}
        
        # Query to match keyword in educator fields or nested courses/batches
        query = {
            '$or': [
                {'first_name': regex},
                {'last_name': regex},
                {'username': regex},
                {'courses.name': regex},
                {'batches.name': regex}
            ]
        }
        
        # Fetch matching documents
        cursor = educators_col.find(query).skip(skip).limit(limit)
        educators = list(cursor)
        
        # Convert _id to string, keep rest as raw
        for educator in educators:
            educator['_id'] = str(educator['_id'])
        
        # Stream the response
        def generate_search_stream():
            yield '{\n'
            yield '"status": "success",\n'
            yield f'"count": {len(educators)},\n'
            yield '"total": ' + str(educators_col.count_documents(query)) + ',\n'
            yield '"page": ' + str(page) + ',\n'
            yield '"limit": ' + str(limit) + ',\n'
            yield '"data": [\n'
            first = True
            for educator in educators:
                if not first:
                    yield ',\n'
                yield json.dumps(educator, ensure_ascii=False)
                first = False
            yield '\n]\n'
            yield '}\n'

        return Response(generate_search_stream(), mimetype='application/json')
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error searching educators: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Route not found'
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
