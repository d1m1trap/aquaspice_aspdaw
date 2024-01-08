# build a schema using pydantic
from pydantic import BaseModel
from typing import Union


class AssetBase(BaseModel):
    name: str
    description: Union[str, None] = None
    process_id: int


class AssetCreate(AssetBase):
    pass


class Asset(AssetBase):
    id: int
    name: str
    description: Union[str, None] = None
    process_id: int


class ProcessBase(BaseModel):
    name: str
    description: Union[str, None] = None
    location: str
    pilot_id: int


class ProcessCreate(ProcessBase):
    pass


class Process(ProcessBase):
    id: int

    class Config:
        orm_mode = True


class PilotBase(BaseModel):
    name: str
    description: Union[str, None] = None
    location: str
    pilot_id: int


class PilotCreate(PilotBase):
    pass


class Pilot(PilotBase):
    id: int
    key: str

    class Config:
        orm_mode = True
