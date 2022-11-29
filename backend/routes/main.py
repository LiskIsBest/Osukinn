from flask import Blueprint, render_template, session, request, redirect
from flask.typing import ResponseReturnValue

import requests
from requests.sessions import Session

from threading import Thread,local
from queue import Queue

main = Blueprint("main",__name__)

""" route for home page """
@main.route('/', methods=["GET"])
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
@main.route('/update', methods=["GET"])
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