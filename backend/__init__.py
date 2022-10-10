from flask import Flask, redirect, render_template, request, session
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from flask.typing import ResponseReturnValue

import requests
from requests.sessions import Session

from threading import Thread,local
from queue import Queue

import datetime
import os

from dotenv import load_dotenv

from ossapi import *

load_dotenv()

CLIENT_ID: int = os.environ.get("CLIENT_ID")
CLIENT_SECRET: str = os.environ.get("CLIENT_SECRET")
REDIRECT_URL: str = os.environ.get("REDIRECT_URL")

def create_app(config_object="backend.config") -> None:

    """ Flask app initialization """
    app = Flask(__name__)
    app.config.from_object(config_object)
    api = Api(app=app)
    mongo = PyMongo()

    """ commafy jinja filter: adds commas to numbers """
    @app.template_filter('commafy')
    def commafy(value)->str:
        if value == 9_999_999_999:
            return "No rank"
        else:
            # ex: 123456 -> 123,456
            return format(int(value), ',d')

    """ Returns User data in dictionary """
    def makeUser(username: str) -> dict:

        # osu api connection
        osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)
        
        # Check if username is valid. if not set name to "None"
        if username == "":
            username = "None"
        else:
            try:
                osuApi.user(username).username
            except ValueError:
                username = "None"
        
        # pull user id
        user_id = osuApi.user(username).id

        # function to pull global rank for specified gamemode. 9_999_999_999 used as No rank found value
        getRank = lambda mode, username: 9_999_999_999 if (osuApi.user(username,mode=mode).rankHistory == None) else osuApi.user(username,mode=mode).rankHistory.data[-1]
        
        # dictionary matching MongoDB document layout
        return {"_id": user_id, 
                "username": osuApi.user(user_id).username,
                "osu_rank": getRank(username=username,mode="osu"), 
                "mania_rank": getRank(username=username,mode="mania"),
                "taiko_rank": getRank(username=username,mode="taiko"),
                "fruits_rank": getRank(username=username,mode="fruits"),
                "avatar_url": osuApi.user(username).avatar_url,
                "last_time_refreshed": str(datetime.datetime.now().replace(microsecond=0))
                }


    """ Flask_restful: get user data """
    class UserData(Resource):

        # osu api connection
        osuApi = OssapiV2(CLIENT_ID, CLIENT_SECRET,REDIRECT_URL)

        # get request for user data from database. insert new user document if not found
        def get(self,username) -> dict:
            mongo.init_app(app)
            user_database = mongo.db.users
            request_username: str = "None" if username == "" else username
            try:
                # check if user id exists
                user_id = self.osuApi.user(request_username).id
            except:
                # id for None user
                user_id = 1516945

            if user_database.find_one({"_id":user_id}) != None:
                user_data =user_database.find_one({"_id":user_id})
            else:
                user_data = makeUser(username=self.osuApi.user(user_id).username)
                user_database.insert_one(user_data)

            return user_data

        # put request to update a specified user document. using put request to keep requests in the same Class
        def put(self,username) -> None:
            mongo.init_app(app)
            user_database = mongo.db.users
            request_username = "None" if username == "" else username
            user_id = self.osuApi.user(request_username).id
            user_database.update_one({"_id":user_id},{ "$set" :makeUser(username=user_id)})


    """ route for home page """
    @app.route('/', methods=["GET"])
    def home() -> ResponseReturnValue:

        # create flask session value
        session["userlist"] = []
        
        # grab mode and user list from url parameters
        request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
        request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
        
        # makes list of usernames
        username_list = request_string.split(',') if request.args.get("usernames") != None else ["None"]
        username_list=list(map(lambda name: name.strip(),username_list)) # remove leading/trailing spaces

        # create flask session values
        session["request_mode"] = request_mode
        session["request_string"] = request_string

        # initialize empty user list
        userList =[]

        # urls for each user
        url_list = [f"{request.url_root}users/{username}" for username in username_list]
        q = Queue(maxsize=0) # use a queue to store all URLs
        for url in url_list:
            q.put(url)
        thread_local = local() # thread_local holds a Session object

        def get_session() -> Session:
            if not hasattr(thread_local,'session'):
                thread_local.session = requests.Session() # create a new Session if not exists
            return thread_local.session

        def get_user_data() -> None:
            session = get_session()
            while True: # execute the requests
                url = q.get()
                with session.get(url) as response:
                    userList.append(response.json())
                q.task_done() # tell the queue, this url is done

        def get_all_data(urls) -> None:

            # each task gets its own thread. max of 10
            thread_num = len(username_list)
            if thread_num > 10:
                thread_num=10
            for i in range(thread_num):
                t_worker = Thread(target=get_user_data)
                t_worker.start()
            q.join()

        get_all_data(urls=url_list)
        
        # function for sort key value
        def keyRank(user):
            return user[f"{request_mode}_rank"]
        
        # find best user based on selected mode. ignore if All mode is selected
        if request_mode != "all" and len(userList) > 1:
            userList.sort(reverse=False,key=keyRank)
            session["best_user"]=userList[0]
        else:
            session["best_user"]="debug"

        # update userList session value
        session["userlist"] = userList
        session.modified = True
    
        return render_template("index.html")


    """ route for update """
    @app.route('/update', methods=["GET"])
    def update() -> ResponseReturnValue:

        # pull values for redirect from flask session
        request_mode = session["request_mode"]
        request_string = session["request_string"]
        user_list = session["userlist"]

        # list of usernames
        username_list = [user["username"] for user in user_list]

        # urls for each user
        url_list = [f"{request.url_root}users/{username}" for username in username_list]
        q = Queue(maxsize=0) # use a queue to store all URLs
        for url in url_list:
            q.put(url)
        thread_local = local() # thread_local holds a Session object

        def get_session() -> Session:
            if not hasattr(thread_local,'session'):
                thread_local.session = requests.Session() # create a new Session if not exists
            return thread_local.session

        def update_user_data() -> None:
            session = get_session()
            while True: # execute the requests
                url = q.get()
                with session.put(url) as response: pass
                q.task_done() # tell the queue, this url is done

        def update_all_users(urls) -> None:

            # each task gets its own thread. max of 10
            thread_num = len(username_list)
            if thread_num > 10:
                thread_num=10
            for i in range(thread_num):
                t_worker = Thread(target=update_user_data)
                t_worker.start()
            q.join()

        update_all_users(url_list)

        # clear the session values
        session.pop("userlist", None)
        session.pop("request_mode", None)
        session.pop("request_string", None)
        session.modified = True

        # go back to home page
        return redirect(f"/?mode={request_mode}&usernames={request_string}")

    api.add_resource(UserData,"/users/<string:username>")

    return app
