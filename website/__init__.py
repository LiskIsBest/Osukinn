from flask import Flask

from .routes import main, rest_api

def create_app(config_object="website.config") -> None:

    """ Flask app initialization """
    app = Flask(__name__)
    app.config.from_object(config_object)

    """ commafy jinja filter: adds commas to numbers """
    @app.template_filter('commafy')
    def commafy(value)->str:
        if value == 9_999_999_999:
            return "No rank"
        else:
            # ex: 123456 -> 123,456
            return format(int(value), ',d')

    app.register_blueprint(main.main, url_prefix="/")
    app.register_blueprint(rest_api.api,url_prefix="/users/")

    return app
