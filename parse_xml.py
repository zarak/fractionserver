import feedparser
import logging
import newspaper
import requests
import time
import xml.etree.ElementTree as ET
from article import Article
from base import Session, engine, Base
from sqlalchemy import exc

from time import mktime
from datetime import datetime
from dateutil import parser

logging.basicConfig(filename='/var/www/html/items-rest/log/parse_xml.log', level=logging.INFO)

MAX_DESCRIPTION_LEN = 2000
GOOD_DESCRIPTION_FEEDS = ['kdnuggets']
FEED_URLS = {
        'flowingdata': 'https://flowingdata.com/feed',
        'redditpython': 'https://www.reddit.com/r/python/.rss',
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
	"distil": "https://distill.pub/rss.xml",
	"ruder": "http://ruder.io/rss/index.rss",
	"acolyer": "https://blog.acolyer.org/feed/",
	"wildml": "http://www.wildml.com/feed/",
	"towardsdatascience": "https://towardsdatascience.com/feed",
        }

def extract_data(feed, feed_url):
    """
    Use feedparser to get the title, date, and link from XML, and description using
    newspaper3k.
    """
    logging.info("Parsing {}".format(feed))
    d = feedparser.parse(feed_url)
    for item in d['items']:
        try:
            date = item['date']
            parsed_date = datetime.fromtimestamp(mktime(item['date_parsed']))
        except KeyError:
            date = item['published']
            if item['published_parsed'] is not None:
                parsed_date = datetime.fromtimestamp(mktime(item['published_parsed']))
            else:
                parsed_date = parser.parse(item['published'])
        # logging.debug("DATE\n", date)
        article_url = item['link']
        # logging.debug("URL\n", article_url)
        title = item['title']
        # logging.debug("TITLE\n", title)
        description = parse_description(article_url)
        shortened_description = description[:MAX_DESCRIPTION_LEN]
        # logging.debug("DESCRIPTION\n", shortened_description[:350])

        new_article = Article(feed, date, parsed_date, article_url, title, shortened_description)
        save_to_db(new_article)


def parse_feed(feed, feed_url):
    """
    Use ETree to get the title, date, and link from XML, and description using
    newspaper3k.
    """
    r_session = requests.Session()
    r_session.headers.update({'User-Agent': 'RSS Aggregator for ML feeds'})
    r = requests.get(feed_url)
    print("STATUS CODE", r.status_code)
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError as e:
        print("{}: skipping {}".format(e, feed))
        return

    if feed not in ['reddit']: # Parse depending on type of XML
        for item in root.find('channel').findall('item'):
            # print("FEED\n", feed)
            date = item.find('pubDate').text
            # print("DATE\n", date)
            article_url = item.find('link').text
            # print("URL\n", article_url)
            title = item.find('title').text
            # print("TITLE\n", title)
            description = parse_description(article_url)
            shortened_description = description[:MAX_DESCRIPTION_LEN]
            # print("DESCRIPTION\n", shortened_description[:350])

            new_article = Article(feed, date, article_url, title, shortened_description)
            save_to_db(new_article)
    else:
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            # print("FEED\n", feed)
            date = entry.find('{http://www.w3.org/2005/Atom}updated').text
            # print("DATE\n", date)
            article_url = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
            # print("URL\n", article_url)
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            # print("TITLE\n", title)
            description = parse_description(article_url)
            shortened_description = description[:MAX_DESCRIPTION_LEN]
            # print("DESCRIPTION\n", shortened_description[:350])

            new_article = Article(feed, date, article_url, title, shortened_description)
            save_to_db(new_article)


def save_to_db(new_article):
    session.add(new_article)
    try:
        session.commit()
    except exc.IntegrityError as e:
        logging.warning("Already found in database: {}".format(new_article.url))
        session.rollback()
    else:
        logging.info("Saved to database: {}".format(new_article.url))


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
            logging.warning("Retrying download")
            time.sleep(5)
            article.download()
            continue
        else:
            break
    else:
        logging.error("Description parse for {} failed".format(url))
        return ""
    return article.text


if __name__ == "__main__":
    # 2 - generate database schema
    Base.metadata.create_all(engine)

    # 3 - create a new session
    session = Session()

    for feed, url in FEED_URLS.items():
        # parse_feed(feed, url)
        extract_data(feed, url)
    session.close()
