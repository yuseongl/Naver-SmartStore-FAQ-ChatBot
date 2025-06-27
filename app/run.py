from api import ask, logs
from containers import Container
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

container = Container()
container.wire(modules=["api.ask", "api.logs"])
app = FastAPI()

app.container = container

app.include_router(ask.router)
app.include_router(logs.router)
