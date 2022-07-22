from flask import Flask
from dotenv import load_dotenv
import os
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY'),
        FLASK_ENV = os.environ.get('FLASK_ENV'),
        FLASK_APP = os.environ.get("FLASK_APP")
    )
    
    from . import osuStats
    app.register_blueprint(osuStats.views)

    return app