import pymysql
import uuid
from flask import jsonify, request
from helper.dbhelper import Database as db



class Transaction:
    def __init__(self):
        print("transaction model")

    # create user transaction
    @staticmethod
    def createTransaction():
        try:
            _json = request.json
            _transaction_id = uuid.uuid4()
            _from_account = _json['from_account']
            _to_account = _json['to_account']
            _transaction_type = _json['transaction_type']
            _amount = _json['amount']
            _currency_id = _json['currency_id']
            _wallet_id = _json['wallet_id']

            check_wallet = get_user_wallet_details(_wallet_id)

            if len(check_wallet) <= 0:
                response = make_response('403', "invalid wallet ID")
                return response

            create_transaction_dict = {"transaction_id": _transaction_id, "from_account": _from_account, "to_account": _to_account, "transaction_type": _transaction_type, "amount": _amount, "currency_id": _currency_id, "wallet_id": _wallet_id}
            data = db.insert('transaction', **create_transaction_dict)
            response = make_response(100, "transaction statement created")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response

    # display all wallets
    @staticmethod
    def allTransactions():
        try:
            sql = "SELECT * FROM `transaction` "
            data = db.select(sql)
            return jsonify(data)

        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response

    # get all transactions basing on the wallet
    @staticmethod
    def allCurrencyWallet():
        try:
            _json = request.json
            _wallet_id = _json['wallet_id']
            check_trans = get_transactions_details(_wallet_id)

            if len(check_trans) <= 0:
                response = make_response(403, "invalid wallet id")
                return response
            
            data = jsonify(check_trans)
            return data

        except Exception as e:
            print(e)
            response = make_response(403, "technical error")
            return response

# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})

# get user wallet details basing on transaction statement
def get_user_wallet_details(walletId):
    sql = "SELECT * FROM `user_wallet` WHERE wallet_id = '" + walletId + "' "
    data = db.select(sql)
    return data
#getting all transactions for a specific wallet id
def get_transactions_details(walletId):
    sql = "SELECT * FROM `transaction` WHERE wallet_id = '" + walletId + "' "
    data = db.select(sql)
    return data
