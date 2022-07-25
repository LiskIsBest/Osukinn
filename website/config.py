import os

from dotenv import load_dotenv
load_dotenv()

class ConfigClass(object):
    
    # secret key
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # MongoDB connection url
    MONGO_DB_URL = os.environ.get("MONGO_URI_SH")
    MONGO_SETTINGS = {
        'host':MONGO_DB_URL
    }
    
    # Flask settings
    FLASK_ENV=os.environ.get("FLASK_ENV")
    FLASK_APP=os.environ.get("FLASK_APP")