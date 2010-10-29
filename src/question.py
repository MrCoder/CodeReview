import datetime

from google.appengine.ext import db

MAX_ANSWER_TIME = 120

class Question(db.Model):
  question = db.TextProperty(required=True)
  asker = db.IMProperty(required=True)
  asked = db.DateTimeProperty(required=True, auto_now_add=True)

  assignees = db.ListProperty(db.IM)
  last_assigned = db.DateTimeProperty()

  answer = db.TextProperty()
  answerer = db.IMProperty()
  answered = db.DateTimeProperty()

  @staticmethod
  def _tryAssignTx(key, user, expiry):
    """Assigns and returns the question if it's not assigned already.

    Args:
      key: db.Key: The key of a Question to try and assign.
      user: db.IM: The user to assign the question to.
    Returns:
      The Question object. If it was already assigned, no change is made
    """
    question = Question.get(key)
    if not question.last_assigned or question.last_assigned < expiry:
      question.assignees.append(user)
      question.last_assigned = datetime.datetime.now()
      question.put()
    return question

  @staticmethod
  def assignQuestion(user):
    """Gets an unanswered question and assigns it to a user to answer.

    Args:
      user: db.IM: The identity of the user to assign a question to.
    Returns:
      The Question entity assigned to the user, or None if there are no
        unanswered questions.
    """
    question = None
    while question == None or user not in question.assignees:
      # Assignments made before this timestamp have expired.
      expiry = (datetime.datetime.now()
                - datetime.timedelta(seconds=MAX_ANSWER_TIME))

      # Find a candidate question
      q = Question.all()
      q.filter("answerer =", None)
      q.filter("last_assigned <", expiry).order("last_assigned")
      # If a question has never been assigned, order by when it was asked
      q.order("asked")
      candidates = [x for x in q.fetch(2) if x.asker != user]
      if not candidates:
        # No valid questions in queue.
        break

      # Try and assign it
      question = db.run_in_transaction(Question._tryAssignTx,
                                       candidates[0].key(), user, expiry)

    # Expire the assignment after a couple of minutes
    return question

  def _unassignTx(self, user):
    question = Question.get(self.key())
    if user in question.assignees:
      question.assignees.remove(user)
      question.put()

  def unassign(self, user):
    """Unassigns the given user to this question.

    Args:
      user: db.IM: The user who will no longer be answering this question.
    """
    db.run_in_transaction(self._unassignTx, user)
