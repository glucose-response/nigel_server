import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# Checks that it is the right type of files
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Convert from the Excel Data into MongoDB
def process_data(excel_file_path, mongo_connection_string, db_name, collection_name):
    # Step 1: Read Excel Data
    df = pd.read_excel(excel_file_path)

    # Step 2: Convert DataFrame to List of Dictionaries (JSON-like)
    data_list = df.to_dict(orient='records')

    # Step 3: Update Data in MongoDB
    client = MongoClient(mongo_connection_string)
    db = client[db_name]
    collection = db[collection_name]

    for data in data_list:
        baby_id = data.get("BabyID")
        existing_record = collection.find_one({"BabyID": baby_id})

        if existing_record:
            # If the BabyID exists, update the GlucoseLevels array
            new_data = {"Date": datetime.strptime(data.get("Date"), "%Y-%m-%d %I:%M %p"), "GlucoseLevel": data.get("GlucoseLevel")}
            collection.update_one({"BabyID": baby_id}, {"$push": {"GlucoseLevels": new_data}})
        else:
            # If the BabyID doesn't exist, insert a new document
            collection.insert_one(data)
