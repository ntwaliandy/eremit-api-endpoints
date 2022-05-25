from flask import Blueprint, request, jsonify, json
from application.models.notification import Notification
bp_app = Blueprint('mod_notification', __name__)



# creating notification
@bp_app.route('/create_notification', methods=['POST'])
def create_notification():
    data = Notification.createNotification()
    return data

# get all notifications
@bp_app.route('/all_notifications', methods=['GET'])
def all_notifications():
    data = Notification.getNotifications()
    return data