import os

from dotenv import load_dotenv
load_dotenv()

# secret key
SECRET_KEY = os.environ.get("SECURE_KEY")

# MongoDB connection url
MONGO_URI = os.environ.get("MONGO_URI")

TZ = os.environ.get("TZ")

# Flask settings
FLASK_ENV=os.environ.get("FLASK_ENV")
FLASK_APP=os.environ.get("FLASK_APP")