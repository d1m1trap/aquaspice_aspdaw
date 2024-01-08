from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base


class Variable(Base):
    __tablename__ = 'variable'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    unit = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    asset_id = Column(Integer, ForeignKey('asset.id'))

    asset = relationship('Asset', back_populates="variables")


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    process_id = Column(Integer, ForeignKey('process.id'))

    process = relationship('Process', back_populates="assets")
    variables = relationship('Variable', back_populates="asset")


class Process(Base):
    __tablename__ = 'process'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    pilot_id = Column(Integer, ForeignKey('pilot.id'))

    pilot = relationship('Pilot', back_populates="processes")
    assets = relationship('Asset', back_populates="process")


class Pilot(Base):
    __tablename__ = 'pilot'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    key = Column(String, unique=True, nullable=True)

    processes = relationship('Process', back_populates="pilot")
