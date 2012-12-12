from util.Notifications import Notifications
from ..awesome import app
app.run()


notification = Notifications()
notification.sendDailyEmails()

