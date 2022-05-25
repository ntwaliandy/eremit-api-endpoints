import pymysql
from flask import jsonify, request
from helper.dbhelper import Database as db

class UserWallet:
    def __init__(self):
        print('userwallet model')

    # create user wallet

    @staticmethod
    def createWallet():
        try:
            _json = request.json
            _user_id = _json['user_id']
            _balance = _json['balance']
            _currency_id = _json['currency_id']
            _wallet_id = _json['wallet_id']

            check_user = get_user_details(_user_id)

            if len(check_user) > 0:
                response = make_response(403, "user already exists")
                print(check_user)
                return response

            addWallet_dict = {"user_id": _user_id, "balance": _balance, "currency_id": _currency_id, "wallet_id": _wallet_id}
            data = db.insert('user_wallet', **addWallet_dict)

            response = make_response(100, "wallet created successfully")
            return response
        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response

    # delete a wallet
    def deleteWallet():
        try:
            _json = request.json
            _wallet_id = _json['wallet_id']
            sql = "DELETE FROM `user_wallet` WHERE wallet_id = '" + _wallet_id + "' "
            db.delete(sql)
            response = make_response(100, "wallet deleted successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to delete a wallet")
            return response

    # display all wallets
    @staticmethod
    def allWallets():
        try:
            sql = "SELECT * FROM `user_wallet` "
            data = db.select(sql)
            return jsonify(data)

        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response
    
    # wallet details basing on user id
    def getWalletDetails():
        try:
            _json = request.json
            _user_id = _json['user_id']

            data = get_user_details(_user_id)
            response = jsonify(data)
            if len(data) <= 0:
                print(data)
                return make_response(403, "No wallet for User ID " + str(_user_id) + "!")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "syntax error")
            return response







# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})


# get user details basing on e-wallet
def get_user_details(userId):
    sql = "SELECT * FROM `user_wallet` WHERE user_id = '" + str(userId) + "' "
    data = db.select(sql)
    return data