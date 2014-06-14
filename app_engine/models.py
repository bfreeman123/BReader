from google.appengine.ext import ndb
import logging
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import datetime
import feedparser
import sys
import traceback

class Base(ndb.Model):
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  updated_at = ndb.DateTimeProperty(auto_now=True)
  
  def guid(self):
    return self.key.urlsafe()

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
    #user = MemcacheValues.user()
    #if user == None:
    #  return
    user = User.query().get()
    uc = Story.query().filter(Story.read == False).count()
    user.unread_count = uc
    user.put()
    memcache.set('user', user)
    return user

class Feed(Base):
  name = ndb.StringProperty(required=True)
  url = ndb.StringProperty(required=True)
  unread_count2 = ndb.IntegerProperty(required=True, default=0)

  @staticmethod
  def parse_charset(input):
    if input == None:
      return None
    
    for token in input.split(';'):
      if token.strip().startswith('charset'):
        return token.strip().split('=')[1]
    return None
  
  @staticmethod
  def fetch_feed(url, retries=1):
    try:
      urlfetch.set_default_fetch_deadline(30)
      result = urlfetch.fetch(url)
      if result.status_code == 200:
        charset = Feed.parse_charset(result.headers['content-type'])
        if charset:
          try:
            content = result.content.decode(charset)
            content = content.encode('utf-8', 'replace')
            return content
          except:
            logging.error("Could not encode " + url)
            logging.error(sys.exc_info()[0])
            return result.content
        else:
          return result.content
      else:
        logging.error("Could not fetch " + url)
    except:
      logging.error("Feed.fetch_feed()" + "".join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])))
      if retries > 0:
        logging.error("retry " + url)
        return Feed.fetch_feed(url, retries-1)

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
  guid = ndb.StringProperty(indexed=True)
  title = ndb.StringProperty(indexed=False)
  link = ndb.StringProperty(indexed=False)
  description = ndb.TextProperty(indexed=False)
  pub_date = ndb.DateTimeProperty(indexed=True)
  read = ndb.BooleanProperty(default=False)
  starred = ndb.BooleanProperty(default=False)

  # taken from http://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
  @staticmethod
  def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
      diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
      diff = now - time 
    elif not time:
      diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
      return ''

    if day_diff == 0:
      if second_diff < 10:
        return "just now"
      if second_diff < 60:
        return str(second_diff) + " seconds ago"
      if second_diff < 120:
        return  "a minute ago"
      if second_diff < 3600:
        return str( second_diff / 60 ) + " minutes ago"
      if second_diff < 7200:
        return "an hour ago"
      if second_diff < 86400:
        return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
      return "Yesterday"
    if day_diff < 7:
      return str(day_diff) + " days ago"
    if day_diff < 31:
      return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
      return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

  def feed(self):
    return self.key.parent().get()

  @staticmethod
  def next(bookmark=None, starred=False, feed=None):
    cursor = None
    if bookmark:
      cursor = ndb.Cursor.from_websafe_string(bookmark)

    query = None
    if feed:
      query = Story.query(ancestor=feed.key)
    else:
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
      f = None
      try:
        f = story.key.parent().get()
      except:
        f = None
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
          'pub_date': Story.pretty_date(story.pub_date),
          'feed_guid': story.feed().guid()
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
  
  @staticmethod
  @ndb.transactional(xg=True)
  def mark_read(key, user):
    story = Story.retrieve(key)
    story.read = True
    story.put()
    Story.count_up(user)
    f = story.feed()
    if f.unread_count2 > 0:
      f.unread_count2 -= 1;
      f.put()

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
  def feeds():
    #data = memcache.get('feeds')
    #if data is not None:
    #  return data
    #else:
      data = Feed.query().order(Feed.name).fetch(1000)
    #  memcache.set('feeds', data)
      return data
