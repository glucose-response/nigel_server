import os
from dotenv import load_dotenv
from bson import json_util
from fileHandling import *
import pandas as pd
import json
import io

# Reference 1 - How to connect to the MongoDB taken from https://flask-pymongo.readthedocs.io/en/latest/
from flask import Flask, jsonify, request, send_file
from pymongo import MongoClient

app = Flask(__name__)
load_dotenv()
MONGODB_URI =  os.environ["MONGODB_URI"]
client = MongoClient(MONGODB_URI) 
# End of Reference 1

# Defining the database and collections
db = client.Nigel
profiles = db.Profiles
db_sweat= db.Sweat_Ms
db_blood = db.Blood_Ms


# Main page - test the app works
@app.route("/")
def index():
    return "Hello this is the main page"
  
# Test that routing works
@app.route("/testing")
def testing():
    return "Hello this is a test"

#-----PUT Requests------------------------

# Add a new baby profile to the Profiles collection
@app.route('/addBaby', methods=["PUT"])
def add_baby():

    try: 
        data = request.get_json()

        nigel_id = data.get("NigelID")
        existing_profile = profiles.find_one({"NigelID":nigel_id})

        # Checks if the NigelID already exists in Profiles
        if existing_profile:
            return jsonify({"error": f"A profile with NigelID {nigel_id} already exists"}), 400
        
        # If not a new baby profile is created
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

# Sends the uploaded excel file with data to the MongoDB database
# Reference 2 - taken from CHATGPT
@app.route('/upload_data', methods=['PUT'])
def upload_data():
    try:
        file = request.files['file']

        # Checks whether the file has been successfully received
        if file and allowed_file(file.filename):
            file_data = file.read()

            # Debugging: Print the content of file_data
            # print("File Data:", file_data)

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
# end of reference 2

#-----GET Requests-----------------------
    
# Locate a certain baby depending on the NigelID provided
@app.route('/findbaby', methods = ['GET'])
def get_baby_info():
    nigelID = request.args.get('NigelID')
    print(nigelID)

    baby = profiles.find_one({'NigelID': int(nigelID)})

    if baby:
        # Baby found, return the information as JSON
        serialized_baby_list = json_util.dumps(baby)

        return jsonify({"baby_info": serialized_baby_list})

    else:
        # Baby not found, return an error message
        return jsonify({'error': 'Baby not found'}), 404

# Gets all the profiles in the Profiles collection
@app.route("/profiles", methods = ["GET"])
def baby_profiles():

    try:
        baby_list = list(profiles.find())
        all_babies = []

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

# Gets all the sweat measurements from the Sweat_Ms collection
@app.route("/getSweats", methods = ["GET"])
def baby_sweats():

    try:
        sweat_list = list(db_sweat.find())
        all_sweats = []

        for sweat in sweat_list:
            formatted_sweat = {
                    "NigelID": sweat.get("NigelID",""), # Get 'NigID' or default to an empty string
                    "entries": sweat.get("entries",0) # Get the entries objects
                    } 

            all_sweats.append(formatted_sweat)

        return jsonify({"sweat_list": all_sweats }), 201
    
    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching all the sweat measurements: {str(e)}"}), 500
    
# Gets all the blood measurements from the Blood_Ms collection
@app.route("/getBlood", methods = ["GET"])
def baby_blood():

    try:
        blood_list = list(db_blood.find())
        all_blood = []

        for blood in blood_list:
            formatted_blood = {
                    "NigelID": blood.get("NigelID",""), # Get 'NigID' or default to an empty string
                    "entries": blood.get("entries",0)} # Get the entries objects
            
            all_blood.append(formatted_blood)
        return jsonify({"blood_list": all_blood}), 201
    
    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching the blood measurements: {str(e)}"}), 500

# Gets all the blood measurements, sweat measurements and profiles on the MongoDB database
@app.route("/bsp", methods = ["GET"])
def bsp():
    try:
        blood_list = list(db_blood.find())
        sweat_list = list(db_sweat.find())
        profile_list = list(profiles.find())

        all_blood = []
        all_sweat = []
        all_profiles = []

        for blood in blood_list:
            formatted_blood = {
                    "NigelID": blood.get("NigelID",""), # Get 'NigID' or default to an empty string
                    "entries": blood.get("entries",0)} # Get the entries objects
            all_blood.append(formatted_blood)

        for sweat in sweat_list:
            formatted_sweat = {
                    "NigelID": sweat.get("NigelID",""), # Get 'NigID' or default to an empty string
                    "entries": sweat.get("entries",0)} # Get the entries objects
            all_sweat.append(formatted_sweat)

        for profile in profile_list:
            formatted_profiles = {
                    "ObjectId": str(profile["_id"]), #Assuming "_id" is an ObjectId
                    "NigelID": profile.get("NigelID",""), # Get 'NigID' or default to an empty string
                    "birthday": profile.get("birthday",0), # Get "Date of Birth" or default to 0
                    "birthWeight": profile.get("birthWeight",0),
                    "gestationalAge": profile.get("gestationalAge",0), # Get gestational age or default to 0
                    "notes": profile.get("notes","")
                }
            all_profiles.append(formatted_profiles)
        
        return jsonify({"blood_list": all_blood},{"sweat_list": all_sweat},{"profiles_list":all_profiles}), 201
    
    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching the blood measurements: {str(e)}"}), 500

# Sends the upload_template.xlsx to the app
@app.route('/download_template',methods = ['GET'])
def download_template():
    excel_template = "upload_template.xlsx"
    return send_file(excel_template, as_attachment= True)

# Downloads all data to a local desktop
# Reference 3 - taken from ChatGPT 
@app.route('/download_all_data_local')
def download_all_data_local():
    try: 
        db_collections = db.list_collection_names()
        file_name = 'all_data.xlsx'
        all_data = retrieve_data(db,db_collections, file_name)
        if 'successfully' in all_data:
                # Set the path where you want to save the file on the local desktop
                local_path = "/Users/tianpan/Documents/all_data.xlsx"

                # Move the file to the local path
                os.rename('all_data.xlsx', local_path)

                # Send the file as a response
                return send_file(local_path, as_attachment=True)

        return all_data, 500

    except Exception as e:
        # Handle exceptions
        return f'Error: {str(e)}', 500
# end of reference 3

#This downloads all the data into an excel file and sends it to the app
@app.route('/download_all_data', methods = ['GET'])
def download_all_data():
    try: 
        db_collections = db.list_collection_names()
        file_name = 'all_data.xlsx'

        # Create an in-memory buffer to store the Excel file
        output_excel_buffer = io.BytesIO()
 
        all_data = retrieve_data(db,db_collections, output_excel_buffer)
        if 'successfully' in all_data:
            # Set the buffer position to the beginning before sending
            output_excel_buffer.seek(0)
            return send_file(output_excel_buffer, as_attachment=True, download_name=file_name)

        return all_data, 500

    except Exception as e:
        return f'Error: {str(e)}', 500

# Getting one collection from mongoDB database and converts into an excel file which saves on the local desktop
@app.route('/export_data_as_excel', methods=['GET'])
def export_excel():
    try:
        collection = request.args.get('collection')
        fetched_data = retrieve_data(db, [collection], 'output_data.xlsx')

        # Check if the export was successful
        if 'successfully' in fetched_data:
            # Set the path where you want to save the file on the local desktop
            local_path = "/Users/tianpan/Documents/output_data.xlsx"

            # Move the file to the local path
            os.rename('output_data.xlsx', local_path)

            # Send the file as a response
            return send_file(local_path, as_attachment=True)

        return fetched_data, 500

    except Exception as e:
        return f'Error: {str(e)}', 500

# Sends data from MongoDB to the app in json form 
# Reference 4: taken from ChatGPT
@app.route('/export_data_as_json', methods = ['GET'])
def export_json():
    
    # Query parameters
    collection = request.args.get('collection')
    nigelID = request.args.get('NigelID')
    print(collection, nigelID)

    # If all the babies data is need
    if nigelID == "all":
        data = list(db[collection].find())

    # For a specific baby
    else:
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
# end of reference 4

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)