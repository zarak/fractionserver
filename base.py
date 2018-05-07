# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgres://test:test123@localhost:5432/test')
Session = sessionmaker(bind=engine)

Base = declarative_base()
