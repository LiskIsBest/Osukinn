from flask import Flask, request
from .views import osuStats
from .extenstions import mongo

def create_app(config_object="website.config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    mongo.init_app(app)

    from .views import osuStats
    
    @app.context_processor
    def modeGrabber():
        mode = str(request.args.get("mode"))
        print(mode)
        return mode
    
    @app.template_filter('commafy')
    def commafy(value):
        if value == 9_999_999_999:
            return "No rank"
        else:
            return format(int(value), ',d')
    
    app.register_blueprint(osuStats.views)

    return app