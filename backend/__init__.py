from flask import Flask
from flask_cors import CORS

from .routes import main, site_api

""" Flask app initialization """
app = Flask(__name__)
app.config.from_object("backend.config")
CORS(app)

app.register_blueprint(main.main, url_prefix="/")
app.register_blueprint(site_api.api,url_prefix="/users/")
