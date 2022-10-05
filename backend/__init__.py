from flask import Flask, redirect, render_template, request, session
from flask_pymongo import PyMongo
from .extenstions import osuApi

def create_app(config_object="backend.config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    @app.template_filter('commafy')
    def commafy(value):
        if value == 9_999_999_999:
            return "No rank"
        else:
            return format(int(value), ',d')

    mongo = PyMongo(app)

    import datetime

    def makeUser(api: object, username: str) -> dict:
        if username == "":
            username = "None"
        else:
            try:
                api.user(username).username
            except ValueError:
                username = "None"
        user_id = api.user(username).id
        getRank = lambda mode, username: 9_999_999_999 if (api.user(username,mode=mode).rankHistory == None) else api.user(username,mode=mode).rankHistory.data[-1]
        return {"_id": user_id, 
                "username": api.user(user_id).username,
                "osu_rank": getRank(username=username,mode="osu"), 
                "mania_rank": getRank(username=username,mode="mania"),
                "taiko_rank": getRank(username=username,mode="taiko"),
                "fruits_rank": getRank(username=username,mode="fruits"),
                "avatar_url": api.user(username).avatar_url,
                "last_time_refreshed": datetime.datetime.now().replace(microsecond=0)
                }

    @app.route("/testUpdate/<username>")
    def updateUser(username):
        with mongo.db.users as user_database:
            request_username = "None" if username == "" else username
            user_id = osuApi.user(request_username).id
            PyMongo.UpdateOne({"_id":user_id},{ "$set" :makeUser(api=osuApi,username=user_id)})
    
    @app.route("/testRetrieve/<mode>/<username>",methods=["GET"])
    def getUser(mode: string, username):
        user_database = mongo.db.users
        
        request_mode = "mania" if mode == None else mode
        request_username = "None" if username == "" else username
        user_id: int = 0
        user_data: dict = {}
        
        try:
            user_id = osuApi.user(request_username).id
        except:
            # id for None user
            user_id = 1516945
    
        if user_database.find_one({"_id":user_id}) != None:
            user_data =user_database.find_one({"_id":user_id})
        else:
            user_data = makeUser(api=osuApi,username=osuApi.user(user_id).username)
            user_database.insert_one(user_data)
        
        data_requested: dict = {}
            
        if request_mode != "all"
            data_requested = {
                "_id":user_data["_id"],
                f"{request_mode}_rank":user_data[f"{request_mode}_rank"],
                "avatar_url": user_data["avatar_url"],
                "last_time_refreshed": user_data["last_time_refreshed"]
            }
        else:
            data_requested = user_data
        
        return data_requested
    
    @app.route('/', methods=["GET"])
    def users():
        user_database = mongo.db.users
        session["userlist"] = []
        request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
        request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
        username_list = request_string.split(',') if request.args.get("usernames") != None else ["None"]
        username_list=list(map(lambda name: name.strip(),username_list))

        session["request_mode"] = request_mode
        session["request_string"] = request_string

        userList =[]
        for username in username_list:
            try:
                userList.append(osuApi.user(username).id)
            except:
                # id for None user
                userList.append(1516945)
        
        for index, user_id in enumerate(userList):
            if user_database.find_one({"_id":user_id}) != None:
                userList[index]=user_database.find_one({"_id":user_id})
            else:
                userList[index]=makeUser(api=osuApi,username=osuApi.user(user_id).username)
                user_database.insert_one(userList[index])
        
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

    @app.route('/update', methods=["GET"])
    def update():
        user_database = mongo.db.users
        
        request_mode = session["request_mode"]
        request_string = session["request_string"]
        
        userList = session["userlist"]
        
        db_requests = [
            (PyMongo.UpdateOne({"_id":user["_id"]},{ "$set" :makeUser(api=osuApi,username=user["username"])})) for user in userList
        ]
        
        try:
            user_database.bulk_write(db_requests, ordered=False)
        except PyMongo.BulkWriteError as bwe:
            print(bwe.details)

        session.pop("userlist", None)
        session.pop("request_mode", None)
        session.pop("request_string", None)
        session.modified = True

        return redirect(f"/?mode={request_mode}&usernames={request_string}")

    return app
