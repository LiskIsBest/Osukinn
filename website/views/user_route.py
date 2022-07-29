from flask import Blueprint, redirect, render_template, request

from ..extenstions import mongo

r_users = Blueprint('user_route', __name__)
