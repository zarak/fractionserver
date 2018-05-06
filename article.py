# coding=utf-8

from sqlalchemy import Column, String, Integer, Date

from base import Base

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    feed = Column(String(80))
    date = Column(String(500))
    parsed_date = Column(Date)
    url = Column(String(2000), unique=True)
    title = Column(String(1000))
    description = Column(String(3000))

    def __init__(self, feed, date, parsed_date, url, title, description):
        self.feed = feed
        self.date = date
        self.parsed_date = parsed_date
        self.url = url
        self.title = title
        self.description = description
