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
        
        # Case-insensitive regex pattern
        regex_pattern = {'$regex': keyword, '$options': 'i'}
        
        # Aggregation pipeline for accurate nested search
        pipeline = [
            # Match top-level fields
            {
                '$match': {
                    '$or': [
                        {'first_name': regex_pattern},
                        {'last_name': regex_pattern},
                        {'username': regex_pattern}
                    ]
                }
            },
            # Add flag for courses match
            {
                '$addFields': {
                    'has_matching_course': {
                        '$gt': [
                            {
                                '$size': {
                                    '$filter': {
                                        'input': '$courses',
                                        'cond': {'$regexMatch': {'input': '$$this.name', 'regex': keyword, 'options': 'i'}}
                                    }
                                }
                            },
                            0
                        ]
                    }
                }
            },
            # Add flag for batches match
            {
                '$addFields': {
                    'has_matching_batch': {
                        '$gt': [
                            {
                                '$size': {
                                    '$filter': {
                                        'input': '$batches',
                                        'cond': {'$regexMatch': {'input': '$$this.name', 'regex': keyword, 'options': 'i'}}
                                    }
                                }
                            },
                            0
                        ]
                    }
                }
            },
            # Final match: include if top-level match OR nested match
            {
                '$match': {
                    '$or': [
                        {'first_name': regex_pattern},
                        {'last_name': regex_pattern},
                        {'username': regex_pattern},
                        {'has_matching_course': True},
                        {'has_matching_batch': True}
                    ]
                }
            },
            # Project to remove temp fields
            {
                '$project': {
                    'has_matching_course': 0,
                    'has_matching_batch': 0
                }
            },
            # Skip and limit for pagination
            {'$skip': skip},
            {'$limit': limit}
        ]
        
        # Run aggregation
        cursor = educators_col.aggregate(pipeline)
        educators = list(cursor)
        
        # Convert _id to string, keep rest as raw
        for educator in educators:
            educator['_id'] = str(educator['_id'])
        
        # Get total count (separate aggregation for count)
        count_pipeline = pipeline[:-2]  # Remove skip/limit for count
        count_pipeline.append({'$count': 'total'})
        total_result = list(educators_col.aggregate(count_pipeline))
        total = total_result[0]['total'] if total_result else 0
        
        # Stream the response
        def generate_search_stream():
            yield '{\n'
            yield '"status": "success",\n'
            yield f'"count": {len(educators)},\n'
            yield f'"total": {total},\n'
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
