from threading import Thread,local
from queue import Queue

from flask import Blueprint, request, redirect, send_from_directory
from flask.typing import ResponseReturnValue
import requests
from requests.sessions import Session

main = Blueprint("main",__name__)

@main.route("/")
def base():
    return send_from_directory("../frontend", "index.html")

@main.route("/<path:path>")
def home(path):
    return send_from_directory("../frontend", path)

""" route for update """
@main.route('/update', methods=["GET"])
def update() -> ResponseReturnValue:

    # grab mode and user list from url parameters
    request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
    request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
    
    # makes list of usernames
    username_list = request_string.split(',') if request.args.get("usernames") != None else ["None"]
    username_list=list(map(lambda name: name.strip(),username_list)) # remove leading/trailing spaces

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

    # go back to home page
    return redirect(f"/?mode={request_mode}&usernames={request_string}")