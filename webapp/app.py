import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# import webapp.routes.api_router as api_router
from .routes import api

script_dir = os.path.dirname(__file__)
frontendAbsolutePath = os.path.join(script_dir, "../frontend/dist")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.include_router(api_router.router, prefix="/users")
app.include_router(api, prefix="/users")

app.mount("", StaticFiles(directory=frontendAbsolutePath, html=True), name="frontend")


@app.get('/')
def frontend():
   return RedirectResponse(url='frontend')