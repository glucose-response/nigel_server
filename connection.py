import os
import datetime

from dotenv import load_dotenv
from pymongo import MongoClient #This initiates the connection with the database

# This is an example of how to add a new baby to the mongodb database
load_dotenv()
MONGODB_URI =  os.environ["MONGODB_URI"] 
client = MongoClient(MONGODB_URI) 
db = client.Nigel
baby_profiles = db.Profiles

#Adding the baby into the mongodb database
new_baby = {
    "NigID": 123,
    "Gestational Age": 29,
    "Date of Birth": datetime.datetime(2023,11,30),
}

result = baby_profiles.insert_one(new_baby)

document_id = result.inserted_id
print(f"_id of inserted document: {document_id}")

client.close()