from api import ask, logs
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI()

app.include_router(ask.router)
app.include_router(logs.router)
