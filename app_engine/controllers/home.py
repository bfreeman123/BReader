from controllers.base import *
import feedparser
import logging
import datetime
import json
from xml.dom.minidom import parseString
from google.appengine.api import memcache
import sys

class MainPage(BaseRequest):
  def get(self):
    u = User.query().get()
    if not u:
      u = User(user=users.get_current_user())
      u.put()
    u2 = User.reset_unread()
    if u2 == None:
      u2 = u
    self.render('index.html', {'unread_count':u2.unread_count})

class FeedPage(BaseRequest):
  def get(self):
    feeds = MemcacheValues.feeds()
    self.render('feeds.html', {'feeds':feeds})

class FeedHandler(webapp2.RequestHandler):
  def get(self):
    now = datetime.datetime.now()
    if now.minute == 30:
      taskqueue.add(url='/feeds_worker', params={})
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Job Added')
    else:
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Sleeping')

class FeedsWorker(webapp2.RequestHandler):
  def post(self):
    feeds = MemcacheValues.feeds()
    for feed in feeds:
      taskqueue.add(url='/feed_worker', params={'key':feed.key.urlsafe()})

class FeedWorker(webapp2.RequestHandler):
  def post(self):
    user = MemcacheValues.user()
    key = self.request.get('key')
    feed = MemcacheValues.feed(key)
    try:
      content = Feed.fetch_feed(feed.url)
      d = feedparser.parse(content)
      for entry in d.entries:
        try:
          story_date = datetime.datetime(*(entry.published_parsed[0:6]))
          yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
          try:
            entry.id == None
          except:
            entry.id = entry.link
          if story_date > yesterday:
            if not Story.query().filter(Story.guid == entry.id).get():
              db_key = ndb.Key(urlsafe=key)
              story = Story(feed=db_key)
              story.title = entry.title
              story.link = entry.link
              x = entry.description
              try:
                if x != entry.content[0].value:
                  x = x + entry.content[0].value
              except:
                x = x
              # get mp3
              if entry.links:
                for link in entry.links:
                  if link['href'].endswith('.mp3'):
                    x = x + "<div><a href='" + link['href'] + "'>" + link['href'] + "</a></div>"
                  elif link['href'].endswith('.jpg') or link['href'].endswith('.jpeg') or link['href'].endswith('.bmp') or link['href'].endswith('.png' or link['href'].endswith('.gif')):
                    x = x + "<div><img src='" + link['href'] + "'>" + "</div>"
              story.description = x
              story.pub_date = story_date
              story.guid = entry.id
              story.put()
        except:
          logging.error("error parsing story" + json.dumps(entry))
    except:
      logging.error("error parsing " + feed.url)
      logging.error(sys.exc_info()[0])

class NewFeed(BaseRequest):
  def post(self):
    url = self.request.get('url')
    Feed.add(url)
    self.redirect('/feeds')

class DeleteFeed(BaseRequest):
  def get(self):
    key = self.request.get('id')
    Feed.delete(key)
    self.redirect('/feeds')

class NextHandler(BaseRequest):
  def get(self):
    bookmark = self.request.get('bookmark')
    stories, more, next_bookmark = Story.next(bookmark)

    self.response.write(json.dumps({'more': more, 'bookmark': next_bookmark, 'stories': stories}))

class ReadHandler(BaseRequest):
  def get(self):
    key = self.request.get('key')
    Story.mark_read(key, MemcacheValues.user())
    
    self.response.write(json.dumps({'status': 'OK', 'key': key}))

class FeedImport(BaseRequest):
  def post(self):
    file = self.request.get('file')
    dom = parseString(file)
    links = dom.getElementsByTagName("outline")
    for link in links:
      url = link.getAttribute('xmlUrl')
      taskqueue.add(url='/feed_import_worker', params={'url':url})
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('This will take a few minutes to import. Refresh the feed page to see what has been imported so far')

class FeedImportWorker(BaseRequest):
  def post(self):
    url = self.request.get('url')
    Feed.add(url)

class Prune(BaseRequest):
  def get(self):
    taskqueue.add(url='/prune_worker', params={})

class PruneWorker(BaseRequest):
  def post(self):
    query = Story.query().filter(Story.read == True).filter(Story.starred == False)
    stories, next_cursor, more = query.fetch_page(1000, start_cursor=None)

    cutoff = datetime.datetime.now() - datetime.timedelta(days=2)
    for story in stories:
      if story.created_at < cutoff:
        story.key.delete()

class Account(BaseRequest):
  def get(self):
    u = User.reset_unread()
    self.render('account.html', {'unread_count':u.unread_count, 'read_count':u.read_count, 'created_at':datetime.datetime.strftime(u.created_at, "%m-%d-%Y")})

class StarredPage(BaseRequest):
  def get(self):
    u = MemcacheValues.user()
    self.render('starred.html', {'unread_count':u.unread_count})

class StarredHandler(BaseRequest):
  def get(self):
    bookmark = self.request.get('bookmark')
    stories, more, next_bookmark = Story.next(bookmark, True)

    self.response.write(json.dumps({'more': more, 'bookmark': next_bookmark, 'stories': stories}))

class MarkStar(BaseRequest):
  def get(self):
    key = self.request.get('key')
    Story.mark_starred(key)
    
    self.response.write(json.dumps({'status': 'OK', 'key': key}))

class UnMarkStar(BaseRequest):
  def get(self):
    key = self.request.get('key')
    Story.unmark_starred(key)
    
    self.response.write(json.dumps({'status': 'OK', 'key': key}))

class Sync(BaseRequest):
  def get(self):
    User.reset_unread()
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Set unread count')
      
    
routes = [('/', MainPage),
          ('/feeds', FeedPage),
          ('/update_feeds', FeedHandler),
          ('/feeds_worker', FeedsWorker),
          ('/feed_worker', FeedWorker),
          ('/feed_new', NewFeed),
          ('/feed_delete', DeleteFeed),
          ('/next', NextHandler),
          ('/read', ReadHandler),
          ('/feed_import', FeedImport),
          ('/feed_import_worker', FeedImportWorker),
          ('/prune', Prune),
          ('/prune_worker', PruneWorker),
          ('/account', Account),
          ('/show_starred', StarredPage),
          ('/starred', StarredHandler),
          ('/mark_star', MarkStar),
          ('/unmark_star', UnMarkStar),
          ('/sync', Sync)]

app = BaseRequest.app_factory(routes)
