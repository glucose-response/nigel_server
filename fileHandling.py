from io import BytesIO
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# Checks that it is the right type of files
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'xlsx', 'xls','csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Convert from the Excel Data into MongoDB
def process_data(file_data, db, sheet_names):
    xls = pd.ExcelFile(BytesIO(file_data))

    for sheet_name in sheet_names:
        df = pd.read_excel(xls, sheet_name)

        # Check if 'NigelID' and 'Timestamp' are present in the DataFrame
        if 'NigelID' in df.columns and 'Timestamp' in df.columns:
            # Convert 'Timestamp' to datetime object
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])

            # Group data by 'NigelID' and day
            grouped_data = df.groupby(['NigelID', df['Timestamp'].dt.date]).apply(lambda group: group.to_dict(orient='records')).to_dict()

            for (NigelID, day), entries in grouped_data.items():
                # Find the existing document with the given 'NigelID'
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
            # If 'NigelID' or 'Timestamp' is not present, insert each row as a separate document
            data_dict = df.to_dict(orient='records')
            collection = db[sheet_name]
            collection.insert_many(data_dict)

# Convert from MongoDB to Excel
def retrieve_data(db, sheet_name, output_excel_path):
        # Retrieve data from MongoDB
    data = list(db[sheet_name].find())

    # Flatten the data to create a list of dictionaries
    flattened_data = []
    for entry in data:
        nigel_id = entry.get('NigelID')
        entries = entry.get('entries', {})

        for date, records in entries.items():
            for record in records:
                flattened_data.append({'NigelID': nigel_id, 'Date': date, **record})

    # Convert the flattened data to a DataFrame
    df = pd.DataFrame(flattened_data)

    # Save the DataFrame to Excel
    df.to_excel(output_excel_path, index=False)

    return 'Data exported to Excel successfully'

    # # Query MongoDB to retrieve the data
    # cursor = db[sheet_name].find()

    # # Convert the cursor data to a list of dictionaries
    # data_list = list(cursor)

    # # If the data_list is empty, return or handle it accordingly
    # if not data_list:
    #     return 'No data found in MongoDB for the specified sheet.'

    # # Create a DataFrame from the list of dictionaries
    # df = pd.json_normalize(data_list, sep='_')

    # # Write the DataFrame to an Excel file
    # df.to_excel(output_excel_path, index=False)

    # return f'Data exported to {output_excel_path} successfully.'
      