from flask import Flask

from .routes import main, site_api

""" Flask app initialization """
app = Flask(__name__)
app.config.from_object("backend.config")

""" commafy jinja filter: adds commas to numbers """
@app.template_filter('commafy')
def commafy(value)->str:
    if value == 9_999_999_999:
        return "No rank"
    else:
        # ex: 123456 -> 123,456
        return format(int(value), ',d')

app.register_blueprint(main.main, url_prefix="/")
app.register_blueprint(site_api.api,url_prefix="/users/")
