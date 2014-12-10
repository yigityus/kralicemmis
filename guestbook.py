#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import datetime
import webapp2
import logging
import datetime
import time
import urllib2
import re

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import memcache

guestbook_key = ndb.Key('Guestbook', 'default_guestbook')

class Greeting(ndb.Model):
  author = ndb.UserProperty()
  content = ndb.TextProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):
  def get(self):
    logging.info('Starting MainPage')
    self.response.out.write('<html><body>')

    greetings = ndb.gql('SELECT * '
                        'FROM Greeting '
                        'WHERE ANCESTOR IS :1 '
                        'ORDER BY date DESC LIMIT 10',
                        guestbook_key)

    for greeting in greetings:
      if greeting.author:
        self.response.out.write('<b>%s</b> wrote:' % greeting.author.nickname())
      else:
        self.response.out.write('An anonymous person wrote:')
      self.response.out.write('<blockquote>%s</blockquote>' %
                              cgi.escape(greeting.content))


    self.response.out.write("""
          <form action="/sign" method="post">
            <div><textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Sign Guestbook"></div>
          </form>
        </body>
      </html>""")


class Guestbook(webapp2.RequestHandler):
  def post(self):
    logging.info('Starting Guestbook')
    greeting = Greeting(parent=guestbook_key)

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')


class Job(webapp2.RequestHandler):
  def get(self):
    today = datetime.date.today()
    logging.info('Starting Job 123***')
    logging.info(today.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))

    url = "http://google.com/"
    try:
      result = urllib2.urlopen(url)
      r = result.read()
      s = r.index('tarih')
      f = r[s+7:s+28]
      logging.info(f)

      #memcache.add(key='kralicemmis', value='test', time=3600)

      d = memcache.get('kralicemmis')
      if d is None:
        d = f
        memcache.add(key='kralicemmis', value=f, time=3600)

      if d != f:
        logging.info('send mail')
        mail.send_mail(sender="yy@gmail.com",
              to="yy@gmail.com",
              subject="Online",
              body='d=' + d + ' f=' + f)

      memcache.add(key='kralicemmis', value=f, time=3600)
    except urllib2.URLError, e:
      logging.error(e)

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/sign', Guestbook),
  ('/job', Job)
], debug=True)
