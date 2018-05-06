from flask_restful import Resource
from models.article import ArticleModel


FEED_URLS = {
        'flowingdata': 'https://flowingdata.com/feed',
        'reddit': 'https://www.reddit.com/r/python/.rss',
        'kdnuggets': 'https://www.kdnuggets.com/feed',
        'kaggle': 'http://blog.kaggle.com/feed',
        'datacamp': 'https://www.datacamp.com/community/rss.xml',
        'dataschool': 'https://www.dataschool.io/rss/',
        'dataquest': 'https://www.dataquest.io/blog/rss/',
        'yhat': 'http://blog.yhat.com/rss.xml',
        'data36': 'https://data36.com/feed/',
        'simplystatistics': 'https://simplystatistics.org/index.xml',
        }


class ArticleList(Resource):
    def get(self):
        # articles = ArticleModel.query.all()
        sorted_articles = ArticleModel.sort_by_date()
        return {"articles": [article.json() for article in sorted_articles]}


class Article(Resource):
    def get(self, id):
        article = ArticleModel.find_by_id(id=id)
        if article is None:
            return {"message": "Article ID not found"}
        return article.json()

    # def post(self):
        # article_url = request.get_json()['url']

        # article = ArticleModel.find_by_url(article_url)
        # if article is None:
            # crawled_description = article.crawl_description(article_url)
            # article = ArticleModel(feed, date, article_url, title, crawled_description)
            # article.save_to_db()
            # print("Saved")
        # else:
            # print("found in db!")

        # return article.json()


class FeedList(Resource):
    def get(self, feed):
        if feed not in FEED_URLS.keys():
            return {"message": "Invalid feed name"}, 404
        articles = ArticleModel.find_by_feed(feed=feed)
        return {"articles": [article.json() for article in articles]}
