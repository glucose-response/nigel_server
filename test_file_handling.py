import os
from dotenv import load_dotenv
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
load_dotenv()
MONGODB_URI =  os.environ["MONGODB_URI"] 
client = MongoClient(MONGODB_URI) 
db = client['Nigel']

file_path = "/Users/tianpan/Documents/Fake_data1.xlsx"
xls = pd.ExcelFile(file_path)

for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name)
    print(sheet_name)
    print(df)

    # Check if 'nigelID' and 'Timestamp' are present in the DataFrame
    if 'NigelID' in df.columns and 'Timestamp' in df.columns:
        # Convert 'Timestamp' to datetime object
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # Group data by 'nigelID' and day
        grouped_data = df.groupby(['NigelID', df['Timestamp'].dt.date]).apply(lambda group: group.to_dict(orient='records')).to_dict()

        for (NigelID, day), entries in grouped_data.items():
            # Find the existing document with the given 'nigelID'
            existing_document = db[sheet_name].find_one({'NigelID': NigelID})

            # If there is an existing document, update it
            if existing_document:
                existing_entries = existing_document.get('entries', {})

                # Create or update the entries for the specific day
                existing_entries[day.strftime('%Y-%m-%d')] = entries

                new_data = {'entries': existing_entries}
                db[sheet_name].update_one({'_id': existing_document['_id']}, {'$set': new_data}, upsert=True)
            else:
                # If no existing document, insert a new document
                db[sheet_name].insert_one({'NigelID': NigelID, 'entries': {day.strftime('%Y-%m-%d'): entries}})
    else:
        # If 'nigelID' or 'Timestamp' is not present, insert each row as a separate document
        data_dict = df.to_dict(orient='records')
        collection = db[sheet_name]
        collection.insert_many(data_dict)
