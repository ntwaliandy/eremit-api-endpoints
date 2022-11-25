from flask import request, jsonify
from helper.dbhelper import Database as db
from stellar_sdk import Server






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




def make_response(status, message):
    return jsonify({"status": status, "message": message})


# get userdetails by ID
def get_user_by_id(userID):
    sql = "SELECT * FROM eremit_db.user WHERE user_id = '" + str(userID) + "' "
    data = db().select(sql)
    return data
    