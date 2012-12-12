from util.Emailer import Emailer
from Constant import Constant

email = {}
email[Constant.EMAIL_TO_KEY] = "nikilster@gmail.com"
email[Constant.EMAIL_SUBJECT_KEY] = "Hi!"
email[Constant.EMAIL_BODY_TEXT_KEY] = "Hi!\nHow are you?\n"
email[Constant.EMAIL_BODY_HTML_KEY] = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
    </p>
  </body>
</html>
"""

emailer = Emailer()
emailer.sendBatch([email])