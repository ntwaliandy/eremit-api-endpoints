import pymysql
import uuid
from flask import jsonify, request
from helper.dbhelper import Database as db
from application.models.auth import token_required


class Transaction:
    def __init__(self):
        print("transaction model")

    # create user transaction
    @staticmethod
    @token_required
    def createTransaction():
        try:
            _json = request.json
            _transaction_id = uuid.uuid4()
            _from_account = _json['from_account']
            _to_account = _json['to_account']
            _transaction_type = _json['trans_type']
            _amount = _json['amount']

            check_from_user = get_walletDetailsBy_walletId(_from_account)
            check_to_user = get_walletDetailsBy_walletId(_to_account)
            if len(check_from_user) <= 0:
                response = make_response(403, "Invalid sender account")
                return response
            if len(check_to_user) <= 0:
                response = make_response(403, "invalid receiver account")
                return response
            if check_from_user == check_to_user:
                response = make_response(403, "You can't send money to yourself plz!")
                return response

            check_from_balance = check_from_user[0]['balance']
            if check_from_balance < _amount:
                response = make_response(403, "Not enough funds to make this transaction")
                return response

            if check_from_user[0]['currency_code'] != check_to_user[0]['currency_code']:
                response = make_response(403, "receiver doesn't use same currency as yours!")
                return response

            _from_net_balance = check_from_balance - _amount
            fromupdate_dict = {"balance": _from_net_balance}
            db.Update('user_wallet', "wallet_id = '" + str(_from_account) + "'", **fromupdate_dict)

            _to_net_balance = check_to_user[0]['balance'] + _amount
            toupdate_dict = {"balance": _to_net_balance}
            db.Update('user_wallet', "wallet_id = '" + str(_to_account) + "'", **toupdate_dict)

            

            _status = "success"
            create_transaction_dict = {"transaction_id": _transaction_id, "from_account": _from_account, "to_account": _to_account, "trans_type": _transaction_type, "amount": _amount, "status": _status}
            data = db.insert('transaction', **create_transaction_dict)
            response = make_response(100, "transaction statement created")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "can't make a transaction")
            return response

    # display all wallets
    @staticmethod
    @token_required
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
    @token_required
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
            response = make_response(403, "can't pull all the transactions of the user.")
            return response

# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})

def get_walletDetailsBy_walletId(walletId):
    sql = "SELECT * FROM `user_wallet` WHERE wallet_id = '" + walletId + "' "
    data = db.select(sql)
    return data
#getting all transactions for a specific wallet id
def get_transactions_details(walletId):
    sql = "SELECT * FROM `transaction` WHERE from_account = '" + walletId + "' OR to_account = '" + walletId + "' "
    data = db.select(sql)
    return data
