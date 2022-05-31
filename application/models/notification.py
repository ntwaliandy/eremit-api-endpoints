import pymysql
import uuid
from flask import jsonify, request
from helper.dbhelper import Database as db
from application.models.auth import token_required
class Notification:
    def __init__(self):
        print("notification model")

    # create notification
    @token_required
    def createNotification():
        try:
            _notification_id = uuid.uuid4()
            _json = request.json
            _message = _json['message']

            addNotification_dic = {"notification_id": _notification_id, "message": _message}
            data = db.insert('notification', **addNotification_dic)

            response = make_response(100, "Notification created successfully!!")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to create a notification")
            return response

    # get all notification
    @token_required
    def getNotifications():
        try:
            sql = "SELECT * FROM `notification` "
            data = db.select(sql)
            return jsonify(data)

        except Exception as e:
            print(e)
            response = make_response(403, "failed to pull all the notifications")
            return response


# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})
