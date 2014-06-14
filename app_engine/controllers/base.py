import os
import webapp2
import jinja2
from models import *
from google.appengine.api import taskqueue
from google.appengine.api import users

class BaseRequest(webapp2.RequestHandler):
  @webapp2.cached_property
  def jinja_environment(self):
    template_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'views'))
    return jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    
  @staticmethod
  def app_factory(routes):
    debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
    config = {}
    return webapp2.WSGIApplication(routes, debug=debug, config=config)
    
  def render(self, page, values):
    user = users.get_current_user()
    values['user'] = user.nickname()
    feeds = Feed.query().order(-Feed.unread_count2).order(Feed.name).fetch()
    values['feeds'] = feeds
    url = self.request.url
    start = url.find('.appspot.com') + 12
    url = url[start:]
    values['url'] = url
    values['logout'] = users.create_logout_url("/")
    u = User.query().get()
    values['total_unread_count'] = u.unread_count
    
    template = self.jinja_environment.get_template(page)
    self.response.out.write(template.render(values))
    