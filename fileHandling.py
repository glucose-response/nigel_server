from io import BytesIO
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# Checks that it is the right type of files
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'xlsx', 'xls','csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Convert from the Excel Data into MongoDB
# Reference 2 - taken from ChatGPT (links to the '/upload_data in app.py)
def process_data(file_data, db, sheet_names):
    xls = pd.ExcelFile(BytesIO(file_data))

    for sheet_name in sheet_names:
        df = pd.read_excel(xls, sheet_name)

        # Check if 'NigelID' and 'Timestamp' are present in the DataFrame
        if 'NigelID' in df.columns and 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
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
# end of reference 2


# Convert data from MongoDB database to Excel
# Reference 5: taken from ChatGPT
def retrieve_data(db, sheet_names, output_excel_path):

    with pd.ExcelWriter(output_excel_path, engine = 'xlsxwriter') as writer:
        # Flatten the data to create a list of dictionaries
        for sheet_name in sheet_names:
            # Retrieve data from MongoDB for the current collection (sheet)
            data = list(db[sheet_name].find())

            flattened_data = []
            for entry in data:
                nigel_id = entry.get('NigelID')
                if 'entries' in entry:
                    entries = entry.get('entries', {})

                    for date, records in entries.items():
                        for record in records:
                            flattened_data.append({'NigelID': nigel_id, 'Date': date, **record})

                else:
                    flattened_data.append(entry)
            # Convert the flattened data to a DataFrame
            df = pd.DataFrame(flattened_data)

            # Save the DataFrame to Excel
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return 'Data exported to Excel successfully'


      