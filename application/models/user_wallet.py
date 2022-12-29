from urllib import response
import uuid
from flask import jsonify, request
from helper.dbhelper import Database as db
from application.models.auth import token_required
import requests
from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder



class UserWallet:
    def __init__(self):
        print('userwallet model')

    # create user wallet

    @staticmethod
    def createWallet(userId, acc_id, asset_code, asset_balance):
        try:
            


            _wallet_id = acc_id
            _user_id = userId
            _balance = asset_balance
            _currency_code = asset_code
        

            # addWallet_dict = {"user_id": _user_id, "balance": _balance, "currency_code": _currency_code, "wallet_id": _wallet_id}
            # data = db().insert('user_wallet', **addWallet_dict)

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
            _userId = _json['user_id']
            _assetIssuer = _json['asset_issuer']
            print(_assetIssuer)
            _assetCode = _json['asset_code']

            # checking user
            check_user = get_userDetails(_userId)
            if len(check_user) <= 0:
                response = make_response(403, "INVALID USER")
                return response

            _pubKey = check_user[0]['public_key']
            _secKey = check_user[0]['secret_key']

            server = Server(horizon_url="https://horizon-testnet.stellar.org")
            # using test-network
            network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE

            # adding a wallet
            issuing_asset = Asset(_assetCode, _assetIssuer)
            print (issuing_asset)

            # checking if distributor account exists
            distributor_account = server.load_account(_pubKey)

            # trusting the asset
            trust_transaction = (
                TransactionBuilder(
                    source_account=distributor_account,
                    network_passphrase=network_passphrase,
                    base_fee=100,
                ).append_change_trust_op(asset=issuing_asset, limit="1000000000").set_timeout(100).build()
            )

            trust_transaction.sign(_secKey)
            trust_transaction_resp = server.submit_transaction(trust_transaction)

            response = make_response(100, "successfully added the Asset")
            return response

        except Exception as e:
            print(str(e))
            response = make_response(403, str(e))
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

            check_user = get_userDetails(_user_id)
            if len(check_user) <= 0:
                response = make_response(403, "INVALID USER")
                return response

            _public_key = check_user[0]['public_key']

            # checking user stellar wallets
            server = Server("https://horizon-testnet.stellar.org")
            account = server.accounts().account_id(_public_key).call()
            balances = account['balances']
            data = balances
            response = jsonify(data)
            return response

        except Exception as e:
            print(e)
            response = user_response(403, "syntax error")
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

# responses
def user_response(status, message):
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

