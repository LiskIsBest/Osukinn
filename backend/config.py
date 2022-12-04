import os

from dotenv import load_dotenv
load_dotenv()

# secret key
SECRET_KEY = os.environ.get("SECRET_KEY")

# timezone
TZ = os.environ.get("TZ")

# Flask settings
FLASK_DEBUG=os.environ.get("FLASK_DEBUG")
FLASK_APP=os.environ.get("FLASK_APP")