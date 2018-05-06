# coding: utf-8
import newspaper
from dateutil import parser
from db import db
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class ArticleModel(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    feed = db.Column(db.String(80))
    date = db.Column(db.String(500))
    parsed_date = db.Column(db.DateTime)
    url = db.Column(db.String(2000), unique=True)
    title = db.Column(db.String(1000))
    description = db.Column(db.String(3000))

    def json(self):
        return {'feed': self.feed, 'date': str(self.date), 
                'parsed_date': str(self.parsed_date), 'url': self.url,
                'title': self.title, 'description': self.description}

    @classmethod
    def find_by_feed(cls, feed):
        return cls.query.filter_by(feed=feed).all()

    @classmethod
    def find_by_url(cls, url):
        return cls.query.filter_by(url=url).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def sort_by_date(cls):
        sorted_articles = cls.query.order_by(cls.parsed_date.desc()).all()
        return sorted_articles

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
