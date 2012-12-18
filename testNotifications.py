from awesome.util.Notifications import Notifications
from awesome import app

# Create fake Flask request context and push onto context stack.
# The request context is needed for render_template to work.
ctx = app.test_request_context('test_request_context')
ctx.push()



# Now do whatever work we want in the request context
notification = Notifications()
notification.sendDailyEmails()



# Pop the request context
ctx.pop()

# $eof
