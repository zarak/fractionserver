import newspaper
import requests
import xml.etree.ElementTree as ET
from article import Article
from base import Session, engine, Base
from sqlalchemy import exc


def parse_feed(feed, feed_url):
    """Get the title, date, and link from XML, and description using newspaper."""
    if feed in ['kaggle']: # Parse depending on type of XML
        r = requests.get(feed_url)
        root = ET.fromstring(r.text)

        for item in root.find('channel').findall('item'):
            print("FEED", feed)
            date = item.find('pubDate').text
            print("DATE", date)
            article_url = item.find('link').text
            print("URL", article_url)
            title = item.find('title').text
            print("TITLE", title)
            description = parse_description(article_url)
            shortened_description = description[:2000]
            print("DESCRIPTION", shortened_description[:350])

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

    parse_feed('kaggle', 'http://blog.kaggle.com/feed/')
    session.close()
