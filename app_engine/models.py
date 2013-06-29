from google.appengine.ext import ndb
import logging
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import datetime
import feedparser

class Base(ndb.Model):
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  updated_at = ndb.DateTimeProperty(auto_now=True)
  
  @staticmethod
  def retrieve(key):
    key = ndb.Key(urlsafe=key)
    return key.get()

class User(Base):
  user = ndb.UserProperty()
  read_count = ndb.IntegerProperty(indexed=False)
  unread_count = ndb.IntegerProperty(indexed=False)

  @staticmethod
  def reset_unread():
    user = MemcacheValues.user()
    if user == None:
      return
    uc = Story.query().filter(Story.read == False).count()
    user.unread_count = uc
    user.put()
    memcache.set('user', user)
    return user

class Feed(Base):
  name = ndb.StringProperty(required=True)
  url = ndb.StringProperty(required=True)

  @staticmethod
  def parse_charset(input):
    if input == None:
      return None
    
    for token in input.split(';'):
      if token.strip().startswith('charset'):
        return token.strip().split('=')[1]
    return None
  
  @staticmethod
  def fetch_feed(url):
    result = urlfetch.fetch(url)
    if result.status_code == 200:
      charset = Feed.parse_charset(result.headers['content-type'])
      if charset:
        content = result.content.decode(charset)
        content = content.encode('utf-8', 'replace')
      else:
        # if we can't parse a charset from the headers, we will assume utf-8
        content = result.content.decode('utf-8')
        content = content.encode('utf-8', 'replace')
      return content
    else:
      logging.error("Could not fetch " + url)

  @staticmethod
  def add(url):
    try:
      for feed in MemcacheValues.feeds():
        if feed.url == url:
          return
      content = Feed.fetch_feed(url)
      d = feedparser.parse(content)
      feed = Feed(name=d.feed.title, url=url)
      feed.put()

      # cheat for eventual consistency
      feeds = memcache.get('feeds')
      if feeds is not None:
        feeds.append(feed)
        memcache.set('feeds', feeds)
      else:
        memcache.set('feeds', [feed])

      return feed
    except:
      logging.error("error parsing " + url)

  @staticmethod
  def delete(key):
    feed = Feed.retrieve(key)
    if feed is None:
      return
    
    feed.key.delete()
    memcache.delete('feed_' + key)
    
    # cheat for eventual consistency
    feeds = memcache.get('feeds')
    results = []
    if feeds is None:
      feeds = []
    for feed in feeds:
      if feed.key.urlsafe() != key:
        results.append(feed)
    memcache.set('feeds', results)

class Story(Base):
  feed = ndb.KeyProperty(kind=Feed, required=True)
  guid = ndb.StringProperty(indexed=True)
  title = ndb.StringProperty(indexed=False)
  link = ndb.StringProperty(indexed=False)
  description = ndb.TextProperty(indexed=False)
  pub_date = ndb.DateTimeProperty(indexed=True)
  read = ndb.BooleanProperty(default=False)
  starred = ndb.BooleanProperty(default=False)

  @staticmethod
  def next(bookmark=None, starred=False):
    cursor = None
    if bookmark:
      cursor = ndb.Cursor.from_websafe_string(bookmark)

    query = Story.query()
    if starred:
      query = query.filter(Story.starred == True)
    else:
      query = query.filter(Story.read == False)
    query = query.order(Story.pub_date)
    PAGE_SIZE = 10
    stories, next_cursor, more = query.fetch_page(PAGE_SIZE, start_cursor=cursor)

    next_bookmark = None
    if more:
      next_bookmark = next_cursor.to_websafe_string()

    s = []
    for story in stories:
      f = MemcacheValues.feed(story.feed.urlsafe())
      # in case feed was deleted but we still have saved stories
      feed_name = None
      feed_url = None
      if f == None:
        feed_name = "Deleted"
        feed_url = "#"
      else:
        feed_name = f.name
        feed_url = f.url
      s.append(
        {
          'key': story.key.urlsafe(),
          'feed_name': feed_name,
          'feed_url': feed_url,
          'title': story.title,
          'link': story.link,
          'description': story.description,
          'pub_date': datetime.datetime.strftime(story.pub_date, "%Y-%m-%dT%H:%M:%S")
        }
      )

    return s, more, next_bookmark

  @staticmethod
  @ndb.transactional
  def count_up(user):
    if not user.read_count:
      user.read_count = 0
    if not user.unread_count:
      user.unread_count = 0
    user.read_count += 1
    user.unread_count -= 1
    if user.unread_count < 0:
      user.unread_count = 0
      logging.error("forced unread_count to 0")
    user.put()
    memcache.set('user', user)

  @staticmethod
  def mark_read(key, user):
    story = Story.retrieve(key)
    story.read = True
    story.put()
    Story.count_up(user)

  @staticmethod
  def mark_starred(key):
    story = Story.retrieve(key)
    story.starred = True
    story.put()

  @staticmethod
  def unmark_starred(key):
    story = Story.retrieve(key)
    story.starred = False
    story.put()

class MemcacheValues():
  @staticmethod
  def user():
    data = memcache.get('user')
    if data is not None:
      return data
    else:
      data = User.query().get()
      memcache.add('user', data)
      return data

  @staticmethod
  def feeds():
    data = memcache.get('feeds')
    if data is not None:
      return data
    else:
      data = Feed.query().order(Feed.name).fetch(1000)
      memcache.set('feeds', data)
      return data

  @staticmethod
  def feed(key):
    data = memcache.get('feed_' + key)
    if data is not None:
      return data
    else:
      data = Feed.retrieve(key)
      memcache.add('feed_' + key, data)
      return data

  
