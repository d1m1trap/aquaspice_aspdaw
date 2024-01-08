from pydantic import BaseModel


class HistoricalBodyData(BaseModel):
    date_from: str
    date_to: str
    experiments: bool = None

