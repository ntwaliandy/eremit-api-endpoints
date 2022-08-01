from flask import Blueprint, request, jsonify, json
from application.models.transaction import Transaction

bp_app = Blueprint('mod_transaction', __name__)

# create transaction
@bp_app.route('/send', methods=['POST'])
def create_transaction():
    data = Transaction.createTransaction()
    return data

@bp_app.route('/all_transactions', methods=['GET'])
def all_transactions():
    data = Transaction.allTransactions()
    return data

@bp_app.route('/transaction_base_on_wallet', methods=['POST'])
def transaction_base_on_wallet():
    data = Transaction.allCurrencyWallet()
    return data

@bp_app.route('/verify_currency', methods=['POST'])
def verifyCurrency():
    data = Transaction.VerifyCurrency()
    return data

@bp_app.route('/deposit', methods=['POST'])
def userDeposit():
    data = Transaction.deposit()
    return data