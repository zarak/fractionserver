import newspaper
import requests
import time
import xml.etree.ElementTree as ET
from article import Article
from base import Session, engine, Base
from sqlalchemy import exc


MAX_DESCRIPTION_LEN = 2000
FEED_URLS = {
        'flowingdata': 'https://flowingdata.com/feed',
        'reddit': 'https://www.reddit.com/r/python/.rss',
        'kdnuggets': 'https://www.kdnuggets.com/feed',
        'kaggle': 'http://blog.kaggle.com/feed',
        # 'datacamp': 'https://www.datacamp.com/community/rss.xml',
        'dataschool': 'https://www.dataschool.io/rss/',
        'dataquest': 'https://www.dataquest.io/blog/rss/',
        'yhat': 'http://blog.yhat.com/rss.xml',
        'data36': 'https://data36.com/feed/',
        'simplystatistics': 'https://simplystatistics.org/index.xml',
        }


def parse_feed(feed, feed_url):
    """
    Get the title, date, and link from XML, and description using
    newspaper3k.
    """
    r_session = requests.Session()
    r_session.headers.update({'User-Agent': 'RSS Aggregator for ML feeds'})
    r = requests.get(feed_url)
    print("STATUS CODE", r.status_code)
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError as e:
        print(f"{e}: skipping {feed}")
        return

    if feed not in ['reddit']: # Parse depending on type of XML
        for item in root.find('channel').findall('item'):
            print("FEED\n", feed)
            date = item.find('pubDate').text
            print("DATE\n", date)
            article_url = item.find('link').text
            print("URL\n", article_url)
            title = item.find('title').text
            print("TITLE\n", title)
            description = parse_description(article_url)
            shortened_description = description[:MAX_DESCRIPTION_LEN]
            print("DESCRIPTION\n", shortened_description[:350])

            print()

            new_article = Article(feed, date, article_url, title, shortened_description)
            session.add(new_article)
            try:
                session.commit()
            except exc.IntegrityError as e:
                session.rollback()
    else:
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            print("FEED\n", feed)
            date = entry.find('{http://www.w3.org/2005/Atom}updated').text
            print("DATE\n", date)
            article_url = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
            print("URL\n", article_url)
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            print("TITLE\n", title)
            description = parse_description(article_url)
            shortened_description = description[:MAX_DESCRIPTION_LEN]
            # if shortened_description == "":
                # # TODO: Get the first comment, if it exists
                # continue
            print("DESCRIPTION\n", shortened_description[:350])

            print()

            new_article = Article(feed, date, article_url, title, shortened_description)
            session.add(new_article)
            try:
                session.commit()
            except exc.IntegrityError as e:
                session.rollback()


def parse_description(url):
    """
    Parse the description from the article url for feeds with a CDATA tag in
    the description field of the XML.
    """
    article = newspaper.Article(url)
    article.download()
    for _ in range(3):
        try:
            article.parse()
        except newspaper.article.ArticleException as e:
            print("Retrying download")
            time.sleep(5)
            article.download()
            continue
        else:
            break
    else:
        print(f"Description parse for {url} failed")
        return ""
    return article.text


if __name__ == "__main__":
    # 2 - generate database schema
    Base.metadata.create_all(engine)

    # 3 - create a new session
    session = Session()

    for feed, url in FEED_URLS.items():
        parse_feed(feed, url)
    session.close()
