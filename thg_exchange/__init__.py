import os
import flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = flask.Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# Enable CORS for React frontend
CORS(app, resources={
    r"/graphql": {"origins": ["http://localhost:3000", "http://frontend:3000"]},
    r"/api/*": {"origins": ["http://localhost:3000", "http://frontend:3000"]}
}, supports_credentials=True)

# Use the URI from .env. If it contains a database, get_default_database() uses it.
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/thg_exchange_db")
client = MongoClient(mongo_uri)

try:
    db = client.get_default_database()
    if db is None:
        db = client["thg_exchange_db"]
except Exception:
    db = client["thg_exchange_db"]
