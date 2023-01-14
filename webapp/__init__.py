from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiohttp
import asyncio

import os

from .routes import api

def commafy(value)->str:
    if value == 9_999_999_999:
        return "No rank"
    else:
        # ex: 123456 -> 123,456
        return format(int(value), ',d')

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
temp_abs_file_path = os.path.join(script_dir, "templates/")

app = FastAPI()

app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")
templates = Jinja2Templates(directory=temp_abs_file_path)
templates.env.filters["commafy"] = commafy

app.include_router(api.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, usernames: str = "None,", mode: str = "all"):

    # grab mode and user list from url parameters
    # request_mode = "all" if mode == None else mode
    # request_string = "None," if usernames == None else usernames
    
    # makes list of usernames
    username_list = usernames.split(',')
    username_list=list(map(lambda name: name.strip(),username_list)) # remove leading/trailing spaces

    userData_list = []

    async def userData():

        async with aiohttp.ClientSession() as session:
            for username in username_list:
                user_url = f"{Request.base_url}users/{username}"
                async with session.get(user_url) as resp:
                    user = resp.text()
                    userData_list.append(user)
    asyncio.run(userData())

    return templates.TemplateResponse("index.html", {
        "request": request,
        "usernames" : usernames,
        "mode" : mode,
        "userData_list" : userData_list
    })

@app.get("/update", response_class=RedirectResponse)
async def update(usernames: str = "None,", mode: str = "all"):
    
    username_list = usernames.split(',')
    username_list=list(map(lambda name: name.strip(),username_list)) # remove leading/trailing spaces

    async def updates():

        async with aiohttp.ClientSession() as session:
            for username in username_list:
                user_url = f"{Request.base_url}users/{username}"
                async with session.put(user_url) as resp:
                    assert resp.status == status.HTTP_200_OK
    asyncio.run(updates())

    return RedirectResponse(url=f"{Request.base_url}?usernames={usernames}&mode={mode}",status_code=status.HTTP_301_MOVED_PERMANENTLY)