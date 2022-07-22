from json import load
from flask import Flask


def create_app(*,key,config,flApp):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = key
    app.config['FLASK_ENV'] = config
    app.config['FLASK_APP'] = flApp

    from .views import views

    app.register_blueprint(views, url_prefix="/")

    return app