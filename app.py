from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
from models.article import ArticleModel
from resources.article import Article
from resources.article import ArticleList
from resources.article import FeedList
import json
import newspaper
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usr:pass@localhost:5432/sqlalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
CORS(app)
# feeds = {
        # 'flowingdata': 'https://flowingdata.com',
        # 'reddit': 'https://www.reddit.com/r/python',
        # 'kddnuggets': 'https://www.kdnuggets.com',
        # 'kaggle': 'http://blog.kaggle.com',
        # 'datacamp': 'https://www.datacamp.com',
        # 'dataschool': 'https://www.dataschool.io',
        # 'dataquest': 'https://www.dataquest.io',
        # 'yhat': 'http://blog.yhat.com',
        # 'data36': 'https://data36.com',
        # 'simplystatistics': 'https://simplystatistics.org',
        # }

api.add_resource(Article, '/article/<int:id>')
api.add_resource(ArticleList, '/articles')
api.add_resource(FeedList, '/feed/<string:feed>')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run()
