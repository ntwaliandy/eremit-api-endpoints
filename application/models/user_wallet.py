import json
from flask import request, jsonify
from helper.dbhelper import Database as db
from stellar_sdk import Server, Asset, Network, TransactionBuilder






class UserWallet():
    def __init__(self):
        print("******USER WALLET*****")

    # getting all user wallets
    def getUserWallet():
        try:
            _json = request.json
            _userId = _json['user_id']

            check_user = get_user_by_id(_userId)
            if len(check_user) <= 0:
                response = make_response(403, "INVALID USER")
                return response

            _pubKey = check_user[0]['pub_key']

            # checking user stellar wallets
            server = Server("https://horizon-testnet.stellar.org")
            account = server.accounts().account_id(_pubKey).call()
            balances = account['balances']
            
            response = make_response(100, balances)
            return response

        except Exception as e:
            print(str(e))
            response = make_response(403, "can't pull user wallets")
            return response

    # add a stellar based Asset
    def addAsset():
        try:
            _json = request.json
            _userId = _json['user_id']
            _assetIssuer = _json['asset_issuer']
            _assetCode = _json['asset_code']

            # checking user
            check_user = get_user_by_id(_userId)
            if len(check_user) <= 0:
                response = make_response(403, "INVALID USER")
                return response

            _pubKey = check_user[0]['pub_key']
            _secKey = check_user[0]['sec_key']

            server = Server(horizon_url="https://horizon-testnet.stellar.org")
            # using test-network
            network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE

            # adding a wallet
            issuing_asset = Asset(_assetCode, _assetIssuer)

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



def make_response(status, message):
    return jsonify({"status": status, "message": message})


# get userdetails by ID
def get_user_by_id(userID):
    sql = "SELECT * FROM eremit_db.user WHERE user_id = '" + str(userID) + "' "
    data = db().select(sql)
    return data
    