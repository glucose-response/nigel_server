# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/ 
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson import json_util
import logging
import sys
from fileHandling import *

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR) 

# Defining the environment of where the database are
load_dotenv()
MONGODB_URI =  os.environ["MONGODB_URI"] 
client = MongoClient(MONGODB_URI) 
db = client.Nigel
profiles = db.Profiles
db_sweat= db.Sweat_Ms
db_blood = db.Blood_Ms

# Configuration for file upload
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return "Hello this is the main page"

# Add a new baby profile to the Profiles database
@app.route('/addBaby', methods=["PUT"])
def add_baby():

    try: 
        data = request.get_json()
        baby_id = profiles.insert_one(data).inserted_id

        result = {
            "id": str(baby_id),
            "NigID": data.get("id"),
            "DoB": data.get("birthDate"),
            "Weight": data.get("weight"),
            "GestationalAge": data.get("gestationalAge"),
            "group": data.get("group"),
        }

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
# Add glucose data to the database
# If there is no data for that specific baby, it creates a new document in MongoDB
# Else, find the NiGID in the table 
    
# @app.route('/addGlucose', methods=["PUT"])
# def add_sweat_measurements():
#     try: 
#         data = request.get_json()
#         glucose_id = profiles.insert_one(data).inserted_id
#         #change this so it gives me the correct result by converting the strings into integers and date types

#         result = {
#             "id": str(baby_id),
#             "NigID": data.get("NigID"),
#             "DoB": data.get("DoB"),
#             "group": data.get("group"),
#         }

#         return jsonify(result), 201

#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500

#If there is a json file and it specifies the NigID of the baby you want to look at, 
#then this will return everything in the profile database
    
#Need to fix this
@app.route('/findbaby', methods = ['GET'])
def get_baby_info():
    nigID = request.get_json['NigID']

    # Find the baby by ID in the MongoDB collection
    baby = profiles.find_one({'NigID': nigID})

    if baby:
        # Baby found, return the information as JSON
        return jsonify({'baby_info': baby})
    else:
        # Baby not found, return an error message
        return jsonify({'error': 'Baby not found'}), 404


# This prints out all the profiles that are on the MongoDB database
@app.route("/profiles")
def baby_profiles():

    try:
        baby_list = list(profiles.find())
        serialized_baby_list = json_util.dumps(baby_list)

        return jsonify({"profiles": serialized_baby_list})

    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching profiles: {str(e)}"}), 500


@app.route("/testing")
def testing():
    return "Hello this is a test"


@app.route('/upload_data', methods=['POST'])
def upload_data():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the Excel file (parse and save to MongoDB)
            process_data(file_path, "your_mongodb_connection_string", "your_database_name", "your_collection_name")

            return jsonify({'message': 'File uploaded successfully'}), 200
        else:
            return jsonify({'error': 'Invalid file format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)