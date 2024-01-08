import os
import sys

import yaml
import httpx
import pandas as pd
from fastapi import Depends, HTTPException
from starlette import status

from auth.auth import HTTPKeyCredentials
from sqlalchemy.orm import joinedload
from dotenv import load_dotenv
from httpx import HTTPStatusError
from collections import defaultdict
from db.models import Pilot, Process, Asset


async def authenticate_pilot(db, key: HTTPKeyCredentials):
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    with db:
        pilot = await db.query(Pilot).filter_by(key == key)
        if pilot is not None:
            return {pilot: pilot}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )


async def fetch_external_data(pilot='AGRICOLA', dtwin='UV', date_from=None, date_to=None, offset=0, limit=100):
    print("Fetcg external!!!!!!!!!!!!!!!!!!!!!")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(base_dir, '.env'))
    sys.path.append(base_dir)
    base_url = os.environ['HISTORICAL_URL']
    dt_uname = os.environ['DT_UNAME']
    dt_pwd = os.environ['DT_PWD']
    tail_url = "/features/synchronization/inbox/messages/getTimeseriesAll?timeout=30"
    url = f"{base_url}{pilot}:{dtwin}{tail_url}"
    print(url)
    body = {
        "$from": date_from,
        "$to": date_to,
        "$offset": offset,
        "$limit": limit
    }

    print(url)
    print(body)
    print(dt_uname, dt_pwd)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, auth=(dt_uname, dt_pwd))
            response.raise_for_status()
            print(response)
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Error calling external API")


async def load_data(path=None, index=None, is_date=False, real=False):
    if path is not None:
        try:
            df = pd.read_csv(path)
            if index is not None and index in df.columns:
                if is_date:
                    df[index] = pd.to_datetime(df[index])
                    df = df.sort_values(by=[index])
                df = df.set_index(index)
            return df
        except:
            raise BaseException('No data in path: ', path)
    elif real is False:
        try:
            return await fetch_external_data()
        except HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e}"}
        except httpx.RequestError as e:
            return {"error": f"Request error occurred: {e}"}
        except Exception as e:
            # Handle other unforeseen errors.
            return {"error": f"An error occurred: {e}"}


async def get_processes(db, pilot="basf"):
    pilot = pilot.lower()
    with db:
        processes = db.query(Process). \
            join(Process.pilot). \
            outerjoin(Process.assets). \
            options(joinedload(Process.assets)). \
            filter(Pilot.name == pilot). \
            all()

        # Convert to a JSON-serializable format
        processes_json = []
        for process in processes:
            process_data = {
                "id": process.id,
                "name": process.name,
                "pilot_id": process.pilot_id,
                "assets": [
                    {
                        "id": asset.id,
                        "name": asset.name,
                        "process_id": asset.process_id
                    } for asset in process.assets
                ]
            }
            processes_json.append(process_data)

        # assets = db.query(Asset).options(joinedload(Asset.process)).join(Process, Asset.process_id == Process.id).join(Pilot, Process.pilot_id == Pilot.id).filter(Pilot.name == pilot).all()

    # with Session(engine) as session:
    #     q = session.query(Portfolio).options(joinedload(Portfolio.stocks).joinedload(PortfolioStock.stock))
    #     for portfolio in q.all():
    #         print(f"Listing associated stocks for portfolio {portfolio.id}")
    #         for assoc in portfolio.stocks:
    #             print(f"    Buy in {assoc.buy_in}, count {assoc.count} and stock id {assoc.stock.id}")

    print(processes_json)
    # Group assets by process
    # grouped_assets = defaultdict(list)
    # print(grouped_assets)
    # # for asset in assets:
    # #     grouped_assets[asset.process_id].append(asset)

    return {"assets": processes_json}


def plot_anomaly(ts, anomaly_pred=None, anomaly_true=None, file_name='file'):
    import plotly.graph_objects as go
    fig = go.Figure()
    yhat = go.Scatter(
        x=ts.index,
        y=ts,
        mode='lines', name=ts.name)
    fig.add_trace(yhat)
    if anomaly_pred is not None:
        status = go.Scatter(
            x=anomaly_pred.index,
            y=ts.loc[anomaly_pred.index],
            mode='markers', name=anomaly_pred.name,
            marker={'color': 'red', 'size': 10, 'symbol': 'star', 'line_width': 0})
        fig.add_trace(status)
    if anomaly_true is not None:
        status = go.Scatter(
            x=anomaly_true.index,
            y=ts.loc[anomaly_true.index],
            mode='markers', name=anomaly_true.name,
            marker={'color': 'yellow', 'size': 10, 'symbol': 'star-open', 'line_width': 2})
        fig.add_trace(status)
    fig.show()


def plot_anomaly_window(ts, anomaly_pred=None, file_name='file', window='1h'):
    fig = go.Figure()
    yhat = go.Scatter(
        x=ts.index,
        y=ts,
        mode='lines', name=ts.name)
    fig.add_trace(yhat)
    if anomaly_pred is not None:
        for i in anomaly_pred.index:
            fig.add_vrect(x0=i - pd.Timedelta(window), x1=i, line_width=0, fillcolor="red", opacity=0.2)
    fig.show()


def get_path(get=True):
    yaml_file_path = os.getcwd() + "/vars.yml"
    with open(yaml_file_path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    if "path" in data:
        return data["path"]
