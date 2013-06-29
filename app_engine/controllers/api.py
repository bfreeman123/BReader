from controllers.base import *
import logging
import datetime
import json
import config
from google.appengine.api import memcache

class NextHandler(BaseRequest):
  def post(self):
    key = self.request.get('api_key')
    if(key != config.API_KEY):
      self.error(403)
    
    bookmark = self.request.get('bookmark')
    stories, more, next_bookmark = Story.next(bookmark)

    self.response.write(json.dumps({'more': more, 'bookmark': next_bookmark, 'stories': stories}))

class ReadHandler(BaseRequest):
  def post(self):
    key = self.request.get('api_key')
    if(key != config.API_KEY):
      self.error(403)

    key = self.request.get('key')
    Story.mark_read(key, MemcacheValues.user())
    
    self.response.write(json.dumps({'status': 'OK', 'key': key}))

class Account(BaseRequest):
  def post(self):
    key = self.request.get('api_key')
    if(key != config.API_KEY):
      self.error(403)

    u = User.reset_unread()
    self.response.write(json.dumps({'unread_count':u.unread_count, 'read_count':u.read_count, 'created_at':datetime.datetime.strftime(u.created_at, "%m-%d-%Y")}))

class Starred(BaseRequest):
  def post(self):
    key = self.request.get('api_key')
    if(key != config.API_KEY):
      self.error(403)
    
    bookmark = self.request.get('bookmark')
    stories, more, next_bookmark = Story.next(bookmark, True)

    self.response.write(json.dumps({'more': more, 'bookmark': next_bookmark, 'stories': stories}))

class Mark(BaseRequest):
  def post(self):
    key = self.request.get('api_key')
    if(key != config.API_KEY):
      self.error(403)

    key = self.request.get('key')
    Story.mark_starred(key)
    
    self.response.write(json.dumps({'status': 'OK', 'key': key}))

class UnMark(BaseRequest):
  def post(self):
    key = self.request.get('api_key')
    if(key != config.API_KEY):
      self.error(403)

    key = self.request.get('key')
    Story.unmark_starred(key)
    
    self.response.write(json.dumps({'status': 'OK', 'key': key}))
      
    
routes = [('/api/next', NextHandler),
          ('/api/read', ReadHandler),
          ('/api/account', Account),
          ('/api/starred', Starred),
          ('/api/mark', Mark),
          ('/api/unmark', UnMark)]

app = BaseRequest.app_factory(routes)
