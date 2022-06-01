from flask_mail import Mail, Message
from application import application

application.config['MAIL_SERVER'] = 'smtp.gmail.com'
application.config['MAIL_PORT'] = 465
application.config['MAIL_USERNAME'] = 'ntwaliandy90@gmail.com'
application.config['MAIL_PASSWORD'] = 'eilk znbj smxl pcwl'
application.config['MAIL_USE_TLS'] = False
application.config['MAIL_USE_SSL'] = True

mail = Mail(application)

def send(OTP, RECEIVER):
    msg = Message('EREMIT LTD', sender = 'ntwaliandy90@gmail.com', recipients = [RECEIVER])
    msg.body = " the otp sent is " + str(OTP) + ". Comfirm it ASAP!!!"
    mail.send(msg)
    return "otp sent to " + RECEIVER + " successfully"