from google.appengine.api import xmpp

from gaetest.base import AppEngineTestCase
from google.appengine.ext.webapp import Request
from src.xmppHandler import XmppHandler, db, Submission

class MyRequest(Request):
    def __init__(self):
        Request.__init__(self, dict())
    def POST(self):
        vars = {'from':'fromtw', 'to':'totw', 'body':'/submit bodytw'}
        return vars




class TestXmppMessage(AppEngineTestCase):
    myReq = MyRequest()
    message = xmpp.Message(myReq.POST())

    def setUp(self):
        self.seq = range(10)

    def test_message_from_my_request(self):
        self.assertEquals("fromtw", self.message.sender)
        self.assertEquals("totw",self.message.to)
        self.assertEquals("/submit bodytw", self.message.body)
        self.assertEquals("submit", self.message.command)
        self.assertEquals("bodytw", self.message.arg)

    def test_should_save_new_submission(self):
        xmppHandler = XmppHandler()
        xmppHandler.submit_command(self.message)
        submissions = Submission.all()
#        submissions = submissions.filter("name =", "bodytw")
        self.assertEqual("bodytw", submissions[0].name)

    def test_should_update_accepted_by1_when_a_review_accept(self):
        pass
        