'''
	Emailer Class
	Handles sending emails
'''
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..Constant import Constant

class Emailer:

	#TODO: Move this outside
	#Sendgrid Login credentials
	username = 'projectAwesomer' #For Gmail: 'projectAwesomer@gmail.com'
	password = "bluesteel!"

	#Config Options
	EMAIL_FROM = "\"Project Awesome\" <projectAwesomer@gmail.com>"
	SMTP_SERVER = 'smtp.sendgrid.net' #For Gmail: 'smtp.gmail.com' 
	PORT = 587

	#Keys

	#Create the class
	def __init__(self):
		pass


	#Send a batch of emails
	def sendBatch(self,emailInfo):


		# Open a connection to the SendGrid mail server
		s = smtplib.SMTP(Emailer.SMTP_SERVER, Emailer.PORT)
		
		#For Gmail
		#s.starttls()

		# Authenticate
		s.login(Emailer.username, Emailer.password)

		#Create each email
		for email in emailInfo:

			#Create Message
			message = self.__createMessage(email)

			# sendmail function takes 3 arguments: sender's address, recipient's address
			# and message to send - here it is sent as one string.
			s.sendmail(Emailer.EMAIL_FROM, message[Constant.EMAIL_TO_KEY], message.as_string())

		#Close
		s.quit()


	#Build the message
	def __createMessage(self, email):

		message 			= MIMEMultipart('alternative')
		message['To'] 		= email[Constant.EMAIL_TO_KEY]
		message['Subject'] 	= email[Constant.EMAIL_SUBJECT_KEY]
		message['From'] 	= Emailer.EMAIL_FROM

		# Record the MIME types of both parts - text/plain and text/html.
		#http://stackoverflow.com/questions/5910104/python-how-to-send-utf-8-e-mail
		textPart = MIMEText(email[Constant.EMAIL_BODY_TEXT_KEY], 'plain', "utf-8")
		HTMLPart = MIMEText(email[Constant.EMAIL_BODY_HTML_KEY], 'html', "utf-8")

		# Attach parts into message container.
		message.attach(textPart)
		message.attach(HTMLPart)

		return message
