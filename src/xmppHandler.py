from src.question import Question, db
from src.reviewer import Reviewer
import datetime
from google.appengine.ext.webapp import xmpp_handlers
import urllib
import httplib

class XmppHandler(xmpp_handlers.CommandHandler):
  """Handler class for all XMPP activity."""

  def _GetAsked(self, user):
    """Returns the user's outstanding asked question, if any."""
    q = Question.all()
    q.filter("asker =", user)
    q.filter("answer =", None)
    return q.get()

  def _GetAnswering(self, user):
    """Returns the question the user is answering, if any."""
    q = Question.all()
    q.filter("assignees =", user)
    q.filter("answer =", None)
    return q.get()

  def unhandled_command(self, message=None):
    # Show help text
    message.reply(HELP_MSG % (self.request.host_url,))

  def mylist_command(self, message=None):
      im_from = db.IM("xmpp", message.sender)
      exist_user = Reviewer.all()
      exist_user.filter("email_address=", im_from)

      if exist_user.get():
          message.reply("Your last time visit is at:" + exist_user.get().last_visit)
          exist_user.last_visit = datetime.datetime.now()
          exist_user.put()
      else:
          message.reply("This is your firt visit, would you signup?")
          user = Reviewer()
          user.email_address = im_from
          user.last_visit = datetime.datetime.now()
          user.put()
      params = urllib.urlencode({'startdate':'20100709', 'todate':'20100709'})
      conn = httplib.HTTPConnection("safe-cloud.appspot.com:80")
      headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
      conn.request("POST", "/sign", params, headers)
      response = conn.getresponse()
      conn.close()
      message.reply("Your expense records:\n" + response.read())


  def askme_command(self, message=None):
    im_from = db.IM("xmpp", message.sender)
    currently_answering = self._GetAnswering(im_from)
    question = Question.assignQuestion(im_from)
    if question:
      message.reply(TELLME_MSG % (question.question,))
    else:
      message.reply(EMPTYQ_MSG)
    # Don't unassign their current question until we've picked a new one.
    if currently_answering:
      currently_answering.unassign(im_from)

  def text_message(self, message=None):
    im_from = db.IM("xmpp", message.sender)
    question = self._GetAnswering(im_from)
    if question:
      other_assignees = question.assignees
      other_assignees.remove(im_from)

      # Answering a question
      question.answer = message.arg
      question.answerer = im_from
      question.assignees = []
      question.answered = datetime.datetime.now()
      question.put()

      # Send the answer to the asker
      xmpp.send_message([question.asker.address],
                        ANSWER_INTRO_MSG % (question.question,))
      xmpp.send_message([question.asker.address], ANSWER_MSG % (message.arg,))

      # Send acknowledgement to the answerer
      asked_question = self._GetAsked(im_from)
      if asked_question:
        message.reply(TELLME_THANKS_MSG)
      else:
        message.reply(THANKS_MSG)

      # Tell any other assignees their help is no longer required
      if other_assignees:
        xmpp.send_message([x.address for x in other_assignees],
                          SOMEONE_ANSWERED_MSG)
    else:
      self.unhandled_command(message)

  def tellme_command(self, message=None):
    im_from = db.IM("xmpp", message.sender)
    asked_question = self._GetAsked(im_from)
    currently_answering = self._GetAnswering(im_from)

    if asked_question:
      # Already have a question
      message.reply(WAIT_MSG)
    else:
      # Asking a question
      asked_question = Question(question=message.arg, asker=im_from)
      asked_question.put()

      if not currently_answering:
        # Try and find one for them to answer
        question = Question.assignQuestion(im_from)
        if question:
          message.reply(TELLME_MSG % (question.question,))
          return
      message.reply(PONDER_MSG)

  def submit_command(self, message=None):
      submission = Submission()
      submission.name = message.arg
      submission.put()
#      message.reply("Your submission is accepted!")


class Submission(db.Model):
    name = db.StringProperty()
    reviewers = db.StringListProperty(default=None)

