import datetime

from google.appengine.ext import db

class Reviewer(db.Model):
    email_address = db.StringProperty()
    last_visit = db.DateTimeProperty()
    