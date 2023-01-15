import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import webapp.routes.api_router as api_router

script_dir = os.path.dirname(__file__)
frontendAbsolutePath = os.path.join(script_dir, "../frontend/dist")

app = FastAPI()

app.mount("", StaticFiles(directory=frontendAbsolutePath, html=True), name="frontend")

app.include_router(api_router.router, prefix="/users")

@app.get('/')
async def frontend():
   return RedirectResponse(url='frontend')