from flask_mail import Mail, Message
from application import application
from flask import jsonify
import africastalking

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

def statusMessage(Email, message):
    msg = Message('EREMIT LTD', sender = 'ntwaliandy90@gmail.com', recipients = [Email])
    msg.body = message
    mail.send(msg)
    return jsonify({"status": 100, "message": "message successfully sent to both accounts."})

#sending messages using sandbox
username = "sandbox"   
api_key = "afe6d0cf21b400ec030b9fc65e87f16658e89070e45ba137395d0950687d9537"     
africastalking.initialize(username, api_key)
sms = africastalking.SMS
           
def on_finish(error, response):
    if error is not None:
        raise error
    print(response)
#  sms.send(otp_generated, [_phone_number], callback=on_finish)


# def sending(message, recipients):
#     sms.send("message", [recipients])
    