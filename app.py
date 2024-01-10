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
import json

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
  
# Test that routing works
@app.route("/testing")
def testing():
    return "Hello this is a test"

# Add a new baby profile to the Profiles database
@app.route('/addBaby', methods=["PUT"])
def add_baby():

    try: 
        data = request.get_json()

        if 'NigelID' not in data:
            return jsonify({"error": "Missing 'id' in the request data"}),400

        nigel_id = data.get("NigelID")

        existing_profile = profiles.find_one({"NigelID":nigel_id})
        if existing_profile:
            return jsonify({"error": f"A profile with NigelID {nigel_id} already exists"}), 400
        
        else:
            baby_id = profiles.insert_one(data).inserted_id

            result = {
                "id": str(baby_id),
                "NigelID": data.get("NigelID"),
                "DoB": data.get("DateOfBirth"),
                "Weight": data.get("BirthWeight"),
                "GestationalAge": data.get("GestationalAge"),
                "Notes": data.get("Notes"),
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
@app.route("/profiles", methods = ["GET"])
def baby_profiles():

    try:
        baby_list = list(profiles.find())

        all_babies = []

        #Construct a custom JSON format
        for baby in baby_list:
            formatted_babies = {
                    "ObjectId": str(baby["_id"]), #Assuming "_id" is an ObjectId
                    "NigelID": baby.get("NigelID",""), # Get 'NigID' or default to an empty string
                    "birthday": baby.get("birthday",0), # Get "Date of Birth" or default to 0
                    "birthWeight": baby.get("birthWeight",0),
                    "gestationalAge": baby.get("gestationalAge",0), # Get gestational age or default to 0
                    "notes": baby.get("notes","")
                }
            
            all_babies.append(formatted_babies)
    
        return jsonify({"profiles": all_babies}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching profiles: {str(e)}"}), 500

# Upload the data from an excel spreadsheet - make sure that there are no repeats of clinican's
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

# This sends a copy of the upload template to the app
@app.route('/download_template',methods = ['GET'])
def download_template():
    excel_template = "upload_template.xlsx"
    return send_file(excel_template, as_attachment= True)

@app.route('/download_all_data')
def download_all_data():
    try: 
        db_collections = db.list_collection_names()
        file_name = 'all_data.xlsx'
        all_data = get_all_data(db,db_collections, file_name)
        if 'successfully' in all_data:
                # Set the path where you want to save the file on the local desktop
                local_path = "/Users/tianpan/Documents/all_data.xlsx"

                # Move the file to the local path
                os.rename('all_data.xlsx', local_path)

                # Send the file as a response
                return send_file(local_path, as_attachment=True)

            # Handle error case
        return all_data, 500

    except Exception as e:
        # Handle exceptions
        return f'Error: {str(e)}', 500

# Getting the data from mongoDB and convert into an excel file - just for Sweat_Ms
@app.route('/export_data_as_excel', methods=['GET'])
def export_excel():
    try:
        # Call the function to retrieve and export data
        collection = request.args.get('collection')

        fetched_data = retrieve_data(db, collection, 'output_data.xlsx')

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

    data = list(db[collection].find(myquery))
    print("Retrieved data:", data)

    for entry in data:
        entry.pop('_id')  # Remove the '_id' field

    # Convert the data to JSON format
    json_data = json.dumps(data, default=json_util.default)

    # Replace double backslashes with a single backslash
    json_data_without_backslashes = json_data.replace("\\", "")

    return jsonify({collection + " for " + nigelID: json.loads(json_data_without_backslashes)}), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)