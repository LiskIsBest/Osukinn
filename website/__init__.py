from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__+".config")
    CORS(app)
    from . import osuStats
    
    @app.template_filter('commafy')
    def commafy(value):
        if value == "No rank":
            return "No rank"
        else:
            return format(int(value), ',d')
    
    app.register_blueprint(osuStats.views)

    return app