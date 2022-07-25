from flask import Flask
from .views import osuStats

from .config import ConfigClass

def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__+".ConfigClass")

    from .views import osuStats
    
    @app.template_filter('commafy')
    def commafy(value):
        if value == 9_999_999_999:
            return "No rank"
        else:
            return format(int(value), ',d')
    
    app.register_blueprint(osuStats.views)

    return app