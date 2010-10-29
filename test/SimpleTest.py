from src.reviewer import Reviewer, db
import random
import unittest
from gaetest.base import AppEngineTestCase
from google.appengine.api.users import User


class TestFunctions(AppEngineTestCase):

    def setUp(self):
        self.seq = range(10)

    def test_story_db_model(self):
        s = Story()
        s.title = "One"
        keyname = "other_key"
        s = Story.get_or_insert(keyname, title="One")
        s = Story.gql("WHERE title = :1", "One")
        self.assertEqual("One", s[0].title)

        s = Story.all()
        s = s.filter("title =", "One")

        self.assertEqual("One", s[0].title)

    def test_story_stringlist(self):
        s = Story()
        s.title = "new book"
        s.readers = ["Xiao Peng", "Li Yanhui"]
        s.put()
        stories = Story.gql("WHERE readers = :1", "Xiao Peng")
        self.assertEqual("new book", stories[0].title)





class Story(db.Model):
    title = db.StringProperty()
    body = db.TextProperty()
    readers = db.StringListProperty
    created = db.DateTimeProperty(auto_now_add=True)


if __name__ == '__main__':
    unittest.main()
