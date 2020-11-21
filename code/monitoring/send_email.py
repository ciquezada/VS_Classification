import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys


FILENAME = sys.argv[1]
if len(sys.argv)==3:
    MSG_EXTRA = sys.argv[2]
else:
    MSG_EXTRA = "END"

mail_content = "Informando Proceso\n\n{}".format(MSG_EXTRA)

#The mail addresses and password
sender_address = 'ciqz.geryon@gmail.com'
sender_pass = 'Terry1234'
receiver_address = 'ciquezada@uc.cl'
#Setup the MIME
message = MIMEMultipart()
message['From'] = sender_address
message['To'] = receiver_address
message['Subject'] = 'Geryon2: {}'.format(FILENAME)   #The subject line
#The body and the attachments for the mail
message.attach(MIMEText(mail_content, 'plain'))

# with open(f, "rb") as fil:
#             part = MIMEApplication(
#                 fil.read(),
#                 Name=basename(f)
#             )
#         # After the file is closed
#         part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
#         msg.attach(part)

#Create SMTP session for sending the mail
session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
session.starttls() #enable security
session.login(sender_address, sender_pass) #login with mail_id and password
text = message.as_string()
session.sendmail(sender_address, receiver_address, text)
session.quit()
print('Mail Sent')
