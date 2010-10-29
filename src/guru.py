# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import os
import re
import wsgiref.handlers
from google.appengine.api import xmpp
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.ereporter import report_generator
from google.appengine.ext.webapp import template

import httplib
import urllib

from src.reviewer import Reviewer
from src.question import Question
from src.xmppHandler import XmppHandler




MAX_ANSWER_TIME = 120






class LatestHandler(webapp.RequestHandler):
  """Displays the most recently answered questions."""

  def Render(self, template_file, template_values):
    path = os.path.join(os.path.dirname(__file__), '../templates', template_file)
    self.response.out.write(template.render(path, template_values))

  def get(self):
    q = Question.all().order('-answered').filter('answered >', None)
    template_values = {
      'questions': q.fetch(20),
    }
    self.Render("latest.html", template_values)


def main():
  app = webapp.WSGIApplication([
      ('/', LatestHandler),
      ('/_ah/xmpp/message/chat/', XmppHandler),
      ], debug=True)
  wsgiref.handlers.CGIHandler().run(app)


if __name__ == '__main__':
  main()
