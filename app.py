# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/ 
from flask import Flask, jsonify, request, send_file
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson import json_util
import logging
import sys
from fileHandling import *
import pandas as pd

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
    
#Able to locate a certain baby depending on the nigelID wanted
@app.route('/findbaby', methods = ['GET'])
def get_baby_info():
    nigelID = request.args.get('NigelID')
    print(nigelID)

    # Find the baby by ID in the MongoDB collection
    baby = profiles.find_one({'NigelID': int(nigelID)})

    if baby:
        # Baby found, return the information as JSON
        serialized_baby_list = json_util.dumps(baby)

        return jsonify({"baby_info": serialized_baby_list})

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

# Upload the data from an excel spreadsheet
@app.route('/upload_data', methods=['PUT'])
def upload_data():
    try:
        file = request.files['file']

        # Checks whether the file has been successfully received
        if file and allowed_file(file.filename):
            file_data = file.read()

            # Debugging: Print the content of file_data
            print("File Data:", file_data)

            # Getting a list of sheet names
            xls = pd.ExcelFile(BytesIO(file_data))
            sheet_names = xls.sheet_names

            # Call the modified function to process and upload the data
            process_data(file_data, db, sheet_names)  # Assuming file_data is a valid Excel file

            return 'Data uploaded to MongoDB successfully'
        else:
            return 'No file provided or invalid file format', 400
    except Exception as e:
        print("Error:", str(e))
        return f'Error: {str(e)}', 400

# Getting the data from mongoDB and convert into an excel file - just for Sweat_Ms
@app.route('/export_data_as_excel/Sweat_Ms', methods=['GET'])
def export_excel():
    try:
        # Call the function to retrieve and export data
        
        fetched_data = retrieve_data(db, 'Sweat_Ms', 'output_data.xlsx')

        # Check if the export was successful
        if 'successfully' in fetched_data:
            # Set the path where you want to save the file on the local desktop
            local_path = "/Users/tianpan/Documents/output_data.xlsx"

            # Move the file to the local path
            os.rename('output_data.xlsx', local_path)

            # Send the file as a response
            return send_file(local_path, as_attachment=True)

        # Handle error case
        return fetched_data, 500

    except Exception as e:
        # Handle exceptions
        return f'Error: {str(e)}', 500

#Convert the data from the mongodb into json form
@app.route('/export_data_as_json', methods = ['GET'])
def export_json():
    # This is the query parameters from the android studio
    collection = request.args.get('collection')
    nigelID = request.args.get('NigelID')
    print(collection, nigelID)

    myquery = {'NigelID': int(nigelID)}

    data = db[collection].find(myquery)
    print("Retrieved data:", data)

    if data:
        serialised_data_list = json_util.dumps(data)
        return jsonify({collection + ' for ' + nigelID: serialised_data_list})
    else:
        # Baby not found, return an error message
        return jsonify({'error': 'Baby not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)