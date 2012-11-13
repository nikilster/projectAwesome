import re

class Verifier:
  # TODO: be more strict about this later
  @staticmethod
  def nameValid(name):
    if len(name) <= 0:
      return False
    return True

  @staticmethod
  def emailValid(email):
    if len(email) <= 3:
      return False
    if not ('@' in email):
      return False
    return True

  # TODO: be more strict about this later
  @staticmethod
  def passwordValid(password):
    if len(password) < 6:
      return False
    if len(password) > 60:
      return False
    return True

  @staticmethod
  def urlValid(url):
    if len(url) > 7 and url[0:4] == 'http':
      return True
    return False

