from awesome.util.Notifications import Notifications
from awesome import app

app.run()


notification = Notifications()
notification.sendDailyEmails()

