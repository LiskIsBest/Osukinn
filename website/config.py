import os

from dotenv import load_dotenv
load_dotenv()

# secret key
SECRET_KEY = os.environ.get("SECRET_KEY")

# MongoDB connection url
MONGO_URI = os.environ.get("MONGO_URI")

# Flask settings
FLASK_ENV=os.environ.get("FLASK_ENV")
FLASK_APP=os.environ.get("FLASK_APP")