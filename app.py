# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/ 
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson import ObjectId, json_util
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# # Load config from .env file
# load_dotenv()
# app.config['MONGO_URI'] = os.environ['MONGODB_URI']
# mongo = PyMongo(app)

# app.config['MONGO_URI'] = "mongodb+srv://tpan:ANLUYbfuddzznbgM@cluster0.ujgggjm.mongodb.net/?retryWrites=true&w=majority"
# mongo = PyMongo(app)
# print(f"Mongo: {mongo}")
# print(f"DB: {mongo.db}")

load_dotenv()
MONGODB_URI =  os.environ["MONGODB_URI"] 
client = MongoClient(MONGODB_URI) 
db = client.Nigel
profiles = db.Profiles

@app.route("/")
def index():
    return "Hello this is the main page"

# @app.route("/profiles")
# def baby_profiles():

#     try:

#         # print("db", mongo.Nigel)
#         # print("profiles", mongo.Nigel.Profiles)

#         # Fetch all documents from the 'BabyProfiles' collection
#         # babies = mongo.Nigel.Profiles

#         # Convert MongoDB cursor to a list for easy printing
#         baby_list = list(profiles.find())
#         print(baby_list)

#         serialized_baby_list = json_util.dumps(baby_list)
#         # Print each document
#         for baby in baby_list:
#             print(baby)

#         return jsonify({'profiles': serialized_baby_list})

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return jsonify({'error': f'An error occurred while fetching profiles: {str(e)}'})

# Add a new baby
@app.route('/addBaby', methods=['POST'])
def add_baby():
    data = request.get_json() 
    nigID = data["NigID"]   
    date_of_birth = data['DoB']
    group = data["Group"]

    # Insert into the database    
    baby_id = profiles.insert_one({'NigID':nigID,'DoB': date_of_birth, 'group': group}).inserted_id

    result = {'id': str(baby_id),
        'NigID':nigID,
        'DoB': date_of_birth, 
        'group': group
    }

    return jsonify(result), 201


@app.route("/testing")
def testing():
    return "Hello this is a test"

@app.route('/getname/<name>',methods = ['POST'])
def extract_name(name):
    return "your name is "+ name

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)