import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mongo = PyMongo()

def init_db(app):
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the environment variables")
    
    app.config["MONGO_URI"] = mongo_uri
    mongo.init_app(app)
