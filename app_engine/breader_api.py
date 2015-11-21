import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from models import *
from string import Template
import logging

package = 'BReader'

class StoryMessage(messages.Message):
  key = messages.StringField(1)
  title = messages.StringField(2)
  link = messages.StringField(3)
  description = messages.StringField(4)
  pub_date = messages.StringField(5)
  feed_name = messages.StringField(6)
  feed_url = messages.StringField(7)
  feed_guid = messages.StringField(8)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      img {max-width:100%}
    </style>
  </head>
  <body>
  $body
  </body>
</html>
"""
def result_to_message(mdl):
  s = StoryMessage()
  s.key = mdl['key']
  s.title = mdl['title']
  s.link = mdl['link']
  t = Template(TEMPLATE)
  s.description = t.substitute(body=mdl['description'])
  s.pub_date = mdl['pub_date']
  s.feed_name = mdl['feed_name']
  s.feed_url = mdl['feed_url']
  s.feed_guid = mdl['feed_guid']
  
  return s

class NextRequest(messages.Message):
  bookmark = messages.StringField(1)

class NextResponse(messages.Message):
  more = messages.BooleanField(1)
  bookmark = messages.StringField(2)
  stories = messages.MessageField(StoryMessage, 3, repeated=True)

DEV_KEY = "292228069948-9os305kmpq2ghgb6r28aprfd16tkfuss.apps.googleusercontent.com"
WEB_CLIENT_ID = "292228069948-o4h6uuvs01ucat8g86phgmv57s0b2a8k.apps.googleusercontent.com"
@endpoints.api(
  name='stories',
  version='v1',
  description='BReader API',
  allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, DEV_KEY, WEB_CLIENT_ID],
  audiences=[WEB_CLIENT_ID],
  scopes=[endpoints.EMAIL_SCOPE])
class StoriesApi(remote.Service):
  @endpoints.method(NextRequest, NextResponse,
                    path='next', http_method='POST',
                    name='stories.next')
  def next_batch(self, request):
    current_user = endpoints.get_current_user()
    logging.error(current_user)
    if current_user is not None:
      email = current_user.email()
      if email != "brian.e.freeman@gmail.com":
        raise endpoints.UnauthorizedException()
    else:
      raise endpoints.UnauthorizedException()
    
    stories, more, next_bookmark = Story.next(request.bookmark, False, None, True)
    res = NextResponse(more=more, bookmark=next_bookmark)
    s = [result_to_message(story) for story in stories]
    res.stories = s
    return res

APPLICATION = endpoints.api_server([StoriesApi])