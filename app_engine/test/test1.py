from google.appengine.api import memcache
from google.appengine.ext import testbed
import webapp2
import webtest
import os
import sys
import inspect
import unittest2
test_directory = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
parent_directory = os.path.abspath(os.path.join(test_directory, os.path.pardir))
if parent_directory not in sys.path:
  sys.path.insert(0, parent_directory)
from models import *

class HomeTest(unittest2.TestCase):

  def setUp(self):
    f = open(parent_directory + "/controllers/home.py", 'r').read()
    exec(f)
    self.testapp = webtest.TestApp(app)
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_user_stub()
    os.environ['USER_EMAIL'] = 'test@example.com'
    os.environ['USER_ID'] = 'abc'
    os.environ['USER_IS_ADMIN'] = '1'

  def tearDown(self):
     self.testbed.deactivate()

  def test_home_page(self):
    response = self.testapp.get('/')
    self.assertEqual(response.status_int, 200)

if __name__ == '__main__':
  unittest2.main()
