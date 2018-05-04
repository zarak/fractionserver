import newspaper
import requests
import xml.etree.ElementTree as ET
from article import Article
from base import Session, engine, Base
from sqlalchemy import exc


FEED_URLS = {
        'flowingdata': 'https://flowingdata.com/feed',
        'reddit': 'https://www.reddit.com/r/python/.rss',
        'kddnuggets': 'https://www.kdnuggets.com/feed',
        'kaggle': 'http://blog.kaggle.com/feed',
        'datacamp': 'https://www.datacamp.com/community/rss.xml',
        'dataschool': 'https://www.dataschool.io/rss/',
        'dataquest': 'https://www.dataquest.io/blog/rss/',
        'yhat': 'http://blog.yhat.com/feed/',
        'data36': 'https://data36.com/fees/',
        'simplystatistics': 'https://simplystatistics.org/index.xml',
        }



def parse_feed(feed, feed_url):
    """Get the title, date, and link from XML, and description using newspaper."""
    if feed in ['kaggle']: # Parse depending on type of XML
        r = requests.get(feed_url)
        root = ET.fromstring(r.text)

        for item in root.find('channel').findall('item'):
            print("FEED\n", feed)
            date = item.find('pubDate').text
            print("DATE\n", date)
            article_url = item.find('link').text
            print("URL\n", article_url)
            title = item.find('title').text
            print("TITLE\n", title)
            description = parse_description(article_url)
            shortened_description = description[:2000]
            print("DESCRIPTION\n", shortened_description[:350])

            print()

            new_article = Article(feed, date, article_url, title, shortened_description)
            session.add(new_article)
            try:
                session.commit()
            except exc.IntegrityError as e:
                session.rollback()


def parse_description(url):
    article = newspaper.Article(url)
    article.download()
    article.parse()
    return article.text


if __name__ == "__main__":
    # 2 - generate database schema
    Base.metadata.create_all(engine)

    # 3 - create a new session
    session = Session()

    for feed, url in FEED_URLS.items():
        parse_feed(feed, url)
    session.close()
