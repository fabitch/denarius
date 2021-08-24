from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DataSource(Base):
    name = Column(String)


class ObjectType(Base):
    name = Column(String)