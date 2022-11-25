from flask import Blueprint, request, jsonify, json, redirect, url_for
from flask import Response

from application.models.transaction import Transaction

bp_app = Blueprint('mod_transaction', __name__)

@bp_app.route("/verify_single_payment", methods=['POST'])
def verifySinglePayment():
    data = Transaction.verifySinglePayment()
    return data

@bp_app.route("/send_single_payment", methods=['POST'])
def sendSinglePayment():
    data = Transaction.sendSinglePayment()
    return data
