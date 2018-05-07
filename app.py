import json
import newspaper
import os
import requests
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
from models.article import ArticleModel
from resources.article import Article
from resources.article import ArticleList
from resources.article import FeedList


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
CORS(app)


api.add_resource(Article, '/article/<int:id>')
api.add_resource(ArticleList, '/articles')
api.add_resource(FeedList, '/feed/<string:feed>')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run()
