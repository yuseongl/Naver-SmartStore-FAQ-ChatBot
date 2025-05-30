from fastapi import FastAPI
from api import ask, logs
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(ask.router)
app.include_router(logs.router)