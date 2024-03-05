from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Boolean

DB_NAME = "sqlite:///main.db"
engine = create_engine(DB_NAME)


class Base(DeclarativeBase):
    pass


class History(Base):
    __tablename__ = "History"
    id = Column(Integer, primary_key=True)
    ordr = Column(String)


class Addresses(Base):
    __tablename__ = "Addresses"
    id = Column(Integer, primary_key=True)
    address = Column(String)


class AdminInfo(Base):
    __tablename__ = "AdminInfo"
    telegram_id = Column(Integer, primary_key=True)
    address_id = Column(Integer, ForeignKey("Addresses.id"))


class Items(Base):
    __tablename__ = "Items"
    id = Column(Integer, primary_key=True)
    top = Column(Integer)
    name = Column(String)
    price = Column(Integer)


class Orders(Base):
    __tablename__ = "Orders"
    ord_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    ordr = Column(String)
    address_id = Column(Integer, ForeignKey("Addresses.id"))
    is_complete = Column(Boolean)
