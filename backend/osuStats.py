from flask import Blueprint, request
from flask_cors import CORS
from . import statGetter

views = Blueprint('osuStats', __name__)
CORS(views)

@views.route('/members')
def members():
    return {
        "user1":statGetter.OsuUser(request.args.get('username1')).osuJson,
        "user2":statGetter.OsuUser(request.args.get('username2')).osuJson,
        }
