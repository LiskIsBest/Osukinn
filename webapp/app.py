import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import api

script_dir = os.path.dirname(__file__)
frontendAbsolutePath = os.path.join(script_dir, "../frontend/dist")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["GET","PUT"],
    allow_headers=["*"],
)
                   
app.include_router(api, prefix="/users")

app.mount("", StaticFiles(directory=frontendAbsolutePath, html=True), name="frontend")

@app.get('/')
def frontend() -> RedirectResponse:
	"""
	Renders "index.html" from the frontend/dist directory

	route: 0.0.0.0/

	parameters:
		None
	return:
		fastapi.responses.RedirectResponse
	"""
	return RedirectResponse(url='frontend')