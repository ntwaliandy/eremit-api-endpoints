from urllib import response
import uuid
from flask import jsonify, request
from helper.dbhelper import Database as db
from application.models.auth import token_required

class UserWallet:
    def __init__(self):
        print('userwallet model')

    # create user wallet

    @staticmethod
    def createWallet(userId):
        try:

            _wallet_id = uuid.uuid4()
            _user_id = userId
            _balance = 0
            _currency_code = "USD"

            addWallet_dict = {"user_id": _user_id, "balance": _balance, "currency_code": _currency_code, "wallet_id": _wallet_id}
            data = db().insert('user_wallet', **addWallet_dict)

            return _wallet_id
        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response

    
    # CREATE OTHER WALLETS
    @token_required
    def otherWallets():
        try:
            _json = request.json
            _user_id = _json['user_id']
            _currency_code = _json['currency_code']
            balance = 0.0
            _wallet_id = uuid.uuid4()

            # check if user exists
            check_user = get_user_details(_user_id)
            if len(check_user) <= 0:
                response = make_response(403, "invalid user")
                return response

            # check user wallet if it already exists
            check_wallet = check_user_currency(_user_id, _currency_code)
            if len(check_wallet) > 0:
                response = make_response(403, "wallet type already exits")
                return response

            other_wallet_dict = {"user_id": _user_id, "wallet_id": _wallet_id, "balance": balance, "currency_code": _currency_code}

            db().insert('user_wallet', **other_wallet_dict)

            response = make_response(100, "New Wallet created successfully")
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "failed to create a new wallet")
            return response

            
            
    

    # delete a wallet
    @token_required
    def deleteWallet():
        try:
            _json = request.json
            _wallet_id = _json['wallet_id']
            check_wallet = get_user_wallet_details(_wallet_id)
            balance = check_wallet[0]['balance']
            if balance > 0:
                response = make_response(403, "can't delete wallet with certain amount")
                return response
            sql = "DELETE FROM `user_wallet` WHERE wallet_id = '" + _wallet_id + "' "
            db().delete(sql)
            response = make_response(100, "wallet deleted successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to delete a wallet")
            return response

    # display all wallets
    @staticmethod
    @token_required
    def allWallets():
        try:
            sql = "SELECT * FROM `user_wallet` "
            data = db().select(sql)
            return jsonify(data)

        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response
    
    # wallet details basing on user id
    @token_required
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

    
    # getting username by wallet id
    @token_required
    def getUsernamebyWalletID():
        try:
            _json = request.json
            _wallet_id = _json['wallet_id']
            walletDeatils = get_user_wallet_details(_wallet_id)
            user_id = walletDeatils[0]['user_id']
            userDetails = get_userDetails(user_id)
            firstName = userDetails[0]['first_name']
            lastName = userDetails[0]['last_name']
            response = make_response(100, firstName + " " + lastName)
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "invalid walletID")
            return response







# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})


# get user details basing on e-wallet
def get_user_details(userId):
    sql = "SELECT * FROM `user_wallet` WHERE user_id = '" + str(userId) + "' "
    data = db().select(sql)
    return data

# get user details basing on e-wallet currency
def check_user_currency(userId, currrency_code):
    sql = "SELECT * FROM `user_wallet` WHERE user_id = '" + userId + "' AND currency_code = '" + currrency_code + "' "
    data = db().select(sql)
    return data

# get wallet details basing on wallet id
def get_user_wallet_details(walletId):
    sql = "SELECT * FROM `user_wallet` WHERE wallet_id = '" + str(walletId) + "' "
    data = db().select(sql)
    return data

# geet user details by userID
def get_userDetails(userId):
    sql = "SELECT * FROM `user` WHERE user_id = '" + str(userId) + "' "
    data = db().select(sql)
    return data

