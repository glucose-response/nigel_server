# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/ 
from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo import MongoClient

app = Flask(__name__)
# # Load config from .env file
# load_dotenv()
# app.config['MONGO_URI'] = os.environ['MONGODB_URI']
# mongo = PyMongo(app)

# # app.config['MONGO_URI'] = "mongodb+srv://Tpan:476PaZI6ygSnwFCm@nigel.zqqhrjd.mongodb.net/?retryWrites=true&w=majority"
# # mongo = PyMongo(app)
# print(f"Mongo: {mongo}")
# print(f"DB: {mongo.db}")

@app.route("/")
def index():
    return "Hello this is the main page"

# @app.route("/profiles")
# def baby_profiles():
#     try:
#         # Fetch all documents from the 'BabyProfiles' collection
#         babies = mongo.Nigel.BabyProfiles.find({})

#         # Convert MongoDB cursor to a list for easy printing
#         baby_list = list(babies)

#         # Print each document
#         for baby in baby_list:
#             print(baby)

#         return jsonify({'profiles': baby_list})
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return jsonify({'error': f'An error occurred while fetching profiles: {str(e)}'})

@app.route("/testing")
def testing():
    return "Hello this is a test"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)