# coding: utf-8
import newspaper
from dateutil import parser
from db import db
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy

FEED_URLS = {
        'flowingdata': 'https://flowingdata.com/feed',
        'reddit': 'https://www.reddit.com/r/python/.rss',
        'redditr': 'https://www.reddit.com/r/Rlanguage/.rss',
        'redditml': 'https://www.reddit.com/r/machinelearning/.rss',
        'kdnuggets': 'https://www.kdnuggets.com/feed',
        'kaggle': 'http://blog.kaggle.com/feed',
        'datacamp': 'https://www.datacamp.com/community/rss.xml',
        'dataschool': 'https://www.dataschool.io/rss/',
        'dataquest': 'https://www.dataquest.io/blog/rss/',
        'yhat': 'http://blog.yhat.com/rss.xml',
        'data36': 'https://data36.com/feed/',
        'simplystatistics': 'https://simplystatistics.org/index.xml',
        }


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

    @classmethod
    def ten_of_each(cls):
        ten_articles_per_feed = [ArticleModel.query.order_by(
            cls.parsed_date.desc()).filter_by(feed=feed).limit(10).all()
                for feed in FEED_URLS.keys()]
        all_articles = sum(ten_articles_per_feed, [])
        sorted_articles = sorted(all_articles, key=lambda x: x.parsed_date, reverse=True)
        return sorted_articles

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "({}) {}: {}".format(self.parsed_date, self.feed, self.title)
