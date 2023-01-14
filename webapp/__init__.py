from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import os

from .routes import api

script_dir = os.path.dirname(__file__)
staticAbsolutePath = os.path.join(script_dir, "static/")
templatesAbsolutePath = os.path.join(script_dir, "templates/")
frontendAbsolutePath = os.path.join(script_dir, "../frontend/dist")

app = FastAPI(docs_url=None,redoc_url=None)

app.mount("", StaticFiles(directory=frontendAbsolutePath, html=True), name="frontend")

app.include_router(api.router)

@app.get('/')
async def frontend():
   return RedirectResponse(url='frontend')