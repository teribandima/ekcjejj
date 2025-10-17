from flask import Flask, jsonify
import pymongo
from pymongo.errors import ConnectionFailure
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# MongoDB connection
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

@app.route('/data', methods=['GET'])
def get_educators_data():
    try:
        educators = list(educators_col.find())
        
        for educator in educators:
            educator['_id'] = str(educator['_id'])
            if 'courses' in educator:
                for course in educator['courses']:
                    course['group_id'] = str(course.get('group_id', {}).get('$numberLong', ''))
                    course['msg_id'] = str(course.get('msg_id', {}).get('$numberInt', ''))
            if 'batches' in educator:
                for batch in educator['batches']:
                    batch['group_id'] = str(batch.get('group_id', {}).get('$numberLong', ''))
                    batch['msg_id'] = str(batch.get('msg_id', {}).get('$numberInt', ''))
        
        return jsonify({
            'status': 'success',
            'data': educators,
            'count': len(educators)
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching data: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Route not found'
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
