import asyncio
import threading

import sys
from random import randrange
from subprocess import Popen
from uuid import UUID, uuid4

import pandas as pd
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
import guild.ipy as guild
import json
import os
import yaml

from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters, cookie
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.sessions import SessionMiddleware

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from broker_pubsub import run_sub, received_messages, run_pub, connect_mqtt
from db.db import get_db
from helpers import get_processes, fetch_external_data
from auth.auth import SessionData
from validators.bodies import HistoricalBodyData
from threading import Thread

# Dummy database of API keys for demonstration
API_KEYS = {
    "123456": "agricola",
    "abcdef": "basf"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
sys.path.append(BASE_DIR)
db_uri = 'postgresql://dawroot:w0rkb3nch@localhost:5432/daw'
print(db_uri)

# sessions
cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="some_key_here",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
            self,
            *,
            identifier: str,
            auto_error: bool,
            backend: InMemoryBackend[UUID, SessionData],
            auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=db_uri)
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

app.mount("/daw/static", StaticFiles(directory="static"), name="static")

origins = [
    "*"
]

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup_event():
    thread = Thread(target=run_sub)
    thread.daemon = True
    thread.start()

async def start_mqtt_client():
    mqtt_client = connect_mqtt()
    await mqtt_client.run_forever()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_mqtt_client())

yaml_file_path = os.getcwd() + "/vars.yml"
with open(yaml_file_path, "r") as yaml_file:
    data = yaml.safe_load(yaml_file)
if "path" in data and data["path"] != os.getcwd():
    data["path"] = os.getcwd()
    with open(yaml_file_path, "w") as yaml_file:
        yaml.dump(data, yaml_file, default_style='"')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ML routes
@app.get("/runs")
async def runs():
    return guild.runs()


@app.get("/compare")
async def compare():
    return json.loads(guild.runs().compare().to_json())


@app.post("/train")
async def train(body: dict):
    # os.system("")
    args = ['guild', 'run', body['name']]
    for flag in body['flags']:
        args.append(flag + "=" + str(body['flags'][flag]))
    args.append('-y')
    Popen(args)
    print(args)
    return {"success": True}


@app.get("/pipelines")
async def pipelines():
    # os.system("")
    path = os.getcwd() + "/guild.yml"
    pipelines = []
    with open(path, 'r') as file:
        docs = yaml.safe_load_all(file)
        for doc in docs:
            for p in doc.keys():
                if doc[p]["visible"] == True:
                    pipelines.append({
                        "name": p,
                        "flags": doc[p]["flags"] if "flags" in doc[p] else None
                    })

    return {"pipelines": pipelines}


@app.get('/logs')
async def get_logs(id):
    runs = guild.runs()
    runs = pd.DataFrame(runs)
    run = runs[runs.run == id]
    if len(run) == 0:
        return []
    run = run.iloc[0].to_dict()
    files = os.listdir(os.path.join(run['run'].run.path, ".guild"))
    lines = []
    for file in files:
        if file == 'output':
            output = os.path.join(run['run'].run.path, ".guild", file)
            count = 0
            with open(output) as f:
                for line in f:
                    count += 1
                    lines.append(line.strip())
    return lines


# DAW routes

async def get_api_key(request: Request):
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key not found")
    # You can add additional validation for the API key here if needed
    return api_key


async def get_current_pilot(request: Request):
    return "Agricola"


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Protected route
# @app.get("/profile", response_model=Pilot)
# async def get_user_profile(current_pilot: Pilot = Depends(get_current_pilot)):
#     return current_pilot


@app.get("/daw/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "active_page": "home"})


@app.get("/daw/data", response_class=HTMLResponse)
async def data_page(request: Request):
    stuff = {"request": request, "active_page": "data"}
    try:
        if request.app.state.session_data:
            stuff["session_data"] = request.app.state.session_data
        print(stuff)
    except AttributeError:
        pass
    return templates.TemplateResponse("data.html", stuff)


@app.get("/daw/experiments", response_class=HTMLResponse)
async def experiments_page(request: Request):
    return templates.TemplateResponse("experiments.html", {"request": request, "active_page": "experiments"})


@app.get("/daw/models", response_class=HTMLResponse)
async def models_page(request: Request):
    return templates.TemplateResponse("models.html", {"request": request, "active_page": "models"})


@app.get("/daw/algorithms", response_class=HTMLResponse)
async def algorithms_page(request: Request):
    return templates.TemplateResponse("algorithms.html", {"request": request, "active_page": "algorithms"})


@app.get("/daw/monitoring", response_class=HTMLResponse)
async def monitoring_page(request: Request):
    return templates.TemplateResponse("monitoring.html", {"request": request, "active_page": "monitoring"})


@app.get("/get_processes")
async def get_h_data(db: Session = Depends(get_db), pilot: str = Depends(get_current_pilot)):
    return await get_processes(db, pilot)


# @app.post("/get-drawer-values/process")
# async def get_d_process(value: SessionData):
#     app.state.process = value
#     return {"received": value}
#
#

@app.post("/get-drawer-values", status_code=200)
async def get_d_values(data: SessionData, response: Response):
    session = uuid4()
    sdata = SessionData(pilot="Agricola", process=data.process, asset=data.asset)
    await backend.create(session, sdata)
    cookie.attach_to_response(response, session)
    app.state.session_data = sdata
    return {"data": data}


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.post("/get_historical", status_code=200)
async def get_h_data(body: HistoricalBodyData):
    print("get_historical!!")
    from datetime import datetime
    print(body.date_from)
    dt_f = datetime.strptime(body.date_from, "%Y-%m-%d %H:%M")
    output_dt_f = dt_f.isoformat()
    print(dt_f, output_dt_f)
    print(body.date_to)
    dt_t = datetime.strptime(body.date_to, "%Y-%m-%d %H:%M")
    output_dt_t = dt_t.isoformat()
    h_response = await fetch_external_data(date_from=output_dt_f, date_to=output_dt_t)
    print(h_response)
    json_data = {attr['attrName']: attr['values'] for attr in h_response['attributes']}

    # Creating the DataFrame
    df = pd.DataFrame(json_data, index=h_response['index'])
    app.state.df = df
    app.state.statistics = df.describe()
    print(df)
    print(app.state.statistics)
    return h_response


@app.get("/download-csv-data", status_code=200)
async def download_csv():
    try:
        df = app.state.df
        print(df)
        print("The df", df)
        clientf_name = "data_export.csv"
        fname = randrange(0, 10000, 4)
        fpath = f'data{os.sep}files{os.sep}downloads{os.sep}{fname}.csv'
        print(fpath)
        base = os.getcwd()
        file_location = f'{base}{os.sep}{fpath}'
        print(file_location)
        df.to_csv(file_location, index_label="datetime")
        return FileResponse(file_location, media_type='application/octet-stream', filename=clientf_name)
    except AttributeError as e:
        print("AttributeError")
        return {"error": e}
    except Exception as err:
        print("Exception")
        return {"error": err}


async def start_broker(type, topic=None, msg=None):
    if type == "pub":
        run_pub(msg)
    elif type == "sub":
        run_sub()


@app.get("/get-real-data", status_code=200)
async def get_data():  # add topic
    await start_broker(start_broker("sub"))
    return {"messages": received_messages}


@app.get("/publish-data", status_code=200)
async def publish_data(topic: str = None, message: str="Test data plain text"):
    try:
        message ="Test data plain text"
        await start_broker("pub", msg="Test data plain text")
        return {"message": "Data published successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
