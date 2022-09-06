from flask import Flask
from .extenstions import mongo

def create_app(config_object="backend.config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    mongo.init_app(app)

    from .views import main_route
    
    @app.template_filter('commafy')
    def commafy(value):
        if value == 9_999_999_999:
            return "No rank"
        else:
            return format(int(value), ',d')
    
    app.register_blueprint(main_route.app)

    return app