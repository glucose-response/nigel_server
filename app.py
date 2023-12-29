# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/ 
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson import ObjectId, json_util
import logging
import sys

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR) 

load_dotenv()
MONGODB_URI =  os.environ["MONGODB_URI"] 
client = MongoClient(MONGODB_URI) 
db = client.Nigel
profiles = db.Profiles

@app.route("/")
def index():
    return "Hello this is the main page"

# Add a new baby
@app.route('/addBaby', methods=["PUT"])
def add_baby():

    app.logger.info('Info: Visiting the root page')

    # logging.info(f"Received POST request: {request.json}")

    try: 
        data = request.get_json()
        baby_id = profiles.insert_one(data).inserted_id

        result = {
            "id": str(baby_id),
            "NigID": data.get("NigID"),
            "DoB": data.get("DoB"),
            "group": data.get("group"),
        }

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)