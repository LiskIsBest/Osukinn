from flask import Flask, redirect, render_template, request, session
from flask_pymongo import PyMongo
from flask_restful import Resource, Api

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

osuApi = OssapiV2(CLIENT_ID, CLIENT_SECRET,REDIRECT_URL)

def create_app(config_object="backend.config") -> None:

    """ Flask app initialization """
    app = Flask(__name__)
    app.config.from_object(config_object)
    api = Api(app=app)

    mongo = PyMongo()

    """ Commafy jinja filter: adds commas to numbers """
    @app.template_filter('commafy')
    def commafy(value)->str:
        if value == 9_999_999_999:
            return "No rank"
        else:
            return format(int(value), ',d')

    """ Returns User data in dictionary """
    def makeUser(username: str) -> dict:
        osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)
        if username == "":
            username = "None"
        else:
            try:
                osuApi.user(username).username
            except ValueError:
                username = "None"
        user_id = osuApi.user(username).id
        getRank = lambda mode, username: 9_999_999_999 if (osuApi.user(username,mode=mode).rankHistory == None) else osuApi.user(username,mode=mode).rankHistory.data[-1]
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
        def get(self,username):
            mongo.init_app(app)
            user_database = mongo.db.users
            request_username: str = "None" if username == "" else username
            try:
                user_id = osuApi.user(request_username).id
            except:
                # id for None user
                user_id = 1516945

            if user_database.find_one({"_id":user_id}) != None:
                user_data =user_database.find_one({"_id":user_id})
            else:
                user_data = makeUser(username=osuApi.user(user_id).username)
                user_database.insert_one(user_data)

            # data_to_return = json.dumps(user_data, indent=4)

            return user_data

        def put(self,username):
            mongo.init_app(app)
            user_database = mongo.db.users
            request_username = "None" if username == "" else username
            user_id = osuApi.user(request_username).id
            user_database.update_one({"_id":user_id},{ "$set" :makeUser(username=user_id)})

    # """ Flask_restful: update user data """
    # class UserUpdate(Resource):
    #     def get(self,username):
    #         mongo.init_app(app)
    #         user_database = mongo.db.users
    #         request_username = "None" if username == "" else username
    #         user_id = osuApi.user(request_username).id
    #         user_database.update_one({"_id":user_id},{ "$set" :makeUser(username=user_id)})

    # @app.route("/update/string:<username>")
    # def updateUser(username: str)->None:
    #     # with MongoClient() as mongo:
    #     user_database = mongo.db.users
    #     request_username = "None" if username == "" else username
    #     user_id = osuApi.user(request_username).id
    #     user_database.update_one({"_id":user_id},{ "$set" :makeUser(api=osuApi,username=user_id)})
    
    # @app.route("/retrieve/<string:username>",methods=["GET","POST"])
    # def getUser(username: str)->dict:
    #     user_database = mongo.db.users
        
    #     request_username: str = "None" if username == "" else username
    #     user_id: int = 0
    #     user_data: dict = {}
        
    #     try:
    #         user_id = osuApi.user(request_username).id
    #     except:
    #         # id for None user
    #         user_id = 1516945
    #     if user_database.find_one({"_id":user_id}) != None:
    #         user_data =user_database.find_one({"_id":user_id})
    #     else:
    #         user_data = makeUser(api=osuApi,username=osuApi.user(user_id).username)
    #         user_database.insert_one(user_data)
        
    #     return user_data
    #     # return {"_id": 1, 
    #     #         "username": "Bob",
    #     #         "osu_rank": 12, 
    #     #         "mania_rank": 12,
    #     #         "taiko_rank": 12,
    #     #         "fruits_rank": 12,
    #     #         "avatar_url": "https://www.copahost.com/blog/wp-content/uploads/2019/07/imgsize2.png",
    #     #         "last_time_refreshed": datetime.datetime.now().replace(microsecond=0)
    #     #         }
    
    """ route for home page """
    @app.route('/', methods=["GET"])
    def users():
        session["userlist"] = []
        request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
        request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
        username_list = request_string.split(',') if request.args.get("usernames") != None else ["None"]
        username_list=list(map(lambda name: name.strip(),username_list))

        session["request_mode"] = request_mode
        session["request_string"] = request_string

        # request_params=[{"mode":request_mode, "username": username} for username in username_list]

        userList =[]

        url_list = [f"{request.url_root}users/{username}" for username in username_list]
        q = Queue(maxsize=0)            #Use a queue to store all URLs
        for url in url_list:
            q.put(url)
        thread_local = local()          #The thread_local will hold a Session object

        def get_session() -> Session:
            if not hasattr(thread_local,'session'):
                thread_local.session = requests.Session() # Create a new Session if not exists
            return thread_local.session

        def get_user_data() -> None:
            session = get_session()
            while True:
                url = q.get()
                with session.get(url) as response:
                    userList.append(response.json())
                q.task_done()          # tell the queue, this url downloading work is done

        def get_all_data(urls) -> None:
            thread_num = len(username_list)
            if thread_num > 10:
                thread_num=10
            for i in range(thread_num):
                t_worker = Thread(target=get_user_data)
                t_worker.start()
            q.join()

        get_all_data(urls=url_list)
        
        def keyRank(user):
            return user[f"{request_mode}_rank"]
        
        if request_mode != "all" and len(userList) > 1:
            userList.sort(reverse=False,key=keyRank)
            session["best_user"]=userList[0]
        else:
            session["best_user"]="debug"

        session["userlist"] = userList
        session.modified = True
    
        return render_template("index.html")

    """ route for update """
    @app.route('/update', methods=["GET"])
    def update():
        request_mode = session["request_mode"]
        request_string = session["request_string"]
        user_list = session["userlist"]
        username_list = [user["username"] for user in user_list]

        # db_requests = [
        #     (PyMongo.UpdateOne({"_id":user["_id"]},{ "$set" :makeUser(api=osuApi,username=user["username"])})) for user in userList
        # ]
        
        # try:
        #     user_database.bulk_write(db_requests, ordered=False)
        # except PyMongo.BulkWriteError as bwe:
        #     print(bwe.details)

        url_list = [f"{request.url_root}users/{username}" for username in username_list]
        q = Queue(maxsize=0)            #Use a queue to store all URLs
        for url in url_list:
            q.put(url)
        thread_local = local()          #The thread_local will hold a Session object

        def get_session() -> Session:
            if not hasattr(thread_local,'session'):
                thread_local.session = requests.Session() # Create a new Session if not exists
            return thread_local.session

        def update_user_data() -> None:
            session = get_session()
            while True:
                url = q.get()
                with session.put(url) as response: pass
                q.task_done()          # tell the queue, this url downloading work is done

        def update_all_users(urls) -> None:
            thread_num = len(username_list)
            if thread_num > 10:
                thread_num=10
            for i in range(thread_num):
                t_worker = Thread(target=update_user_data)
                t_worker.start()
            q.join()

        update_all_users(url_list)

        session.pop("userlist", None)
        session.pop("request_mode", None)
        session.pop("request_string", None)
        session.modified = True

        return redirect(f"/?mode={request_mode}&usernames={request_string}")

    api.add_resource(UserData,"/users/<string:username>")
    # api.add_resource(UserUpdate,"/update/<string:username>")

    return app
