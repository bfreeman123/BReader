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
    values['logout'] = users.create_logout_url("/")
    url = self.request.url
    if "/feeds" in url:
      values['home_url_class'] = ''
      values['feeds_url_class'] = 'active'
      values['starred_url_class'] = ''
    elif "/account" in url:
      values['home_url_class'] = ''
      values['feeds_url_class'] = ''
      values['starred_url_class'] = ''
    elif "/show_starred" in url:
      values['home_url_class'] = ''
      values['feeds_url_class'] = ''
      values['starred_url_class'] = 'active'
    else:
      values['home_url_class'] = 'active'
      values['feeds_url_class'] = ''
      values['starred_url_class'] = ''
    
    template = self.jinja_environment.get_template(page)
    self.response.out.write(template.render(values))
    