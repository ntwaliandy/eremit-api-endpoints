import pymysql
import uuid
from flask import jsonify, request
from helper.dbhelper import Database as db
from application.models.auth import token_required
from application.libs.sms import statusMessage


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

            _statusFrom = "credit"
            _statusTo = "debit"
            check_from_user = get_walletDetailsBy_walletId(_from_account)
            check_to_user = get_walletDetailsBy_walletId(_to_account)
            if len(check_from_user) <= 0:
                response = make_response(403, "Invalid sender account")
                return response
            if len(check_to_user) <= 0:
                response = make_response(403, "invalid receiver account")
                return response

            if _amount <= 0:
                response = make_response(403, "less amount to transfer")
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

            from_userId = check_from_user[0]['user_id']
            from_currency = check_from_user[0]['currency_code']
            check_from_personal_account = check_user_by_id(from_userId)
            from_email = check_from_personal_account[0]['email']
            from_first_name = check_from_personal_account[0]['first_name']
            from_last_name = check_from_personal_account[0]['last_name']

            to_userId = check_to_user[0]['user_id']
            to_currency = check_to_user[0]['currency_code']
            check_to_personal_account = check_user_by_id(to_userId)
            to_email = check_to_personal_account[0]['email']
            to_first_name = check_to_personal_account[0]['first_name']
            to_last_name = check_from_personal_account[0]['last_name']

            _from_net_balance = check_from_balance - _amount
            fromupdate_dict = {"balance": _from_net_balance}
            db().Update('user_wallet', "wallet_id = '" + str(_from_account) + "'", **fromupdate_dict)
            
            create_from_transaction_dict = {"transaction_id": _transaction_id, "from_account": _from_account, "to_account": _to_account, "trans_type": _transaction_type, "amount": _amount, "status": _statusFrom}
            db().insert('transaction', **create_from_transaction_dict)


            _to_net_balance = check_to_user[0]['balance'] + _amount
            toupdate_dict = {"balance": _to_net_balance}
            db().Update('user_wallet', "wallet_id = '" + str(_to_account) + "'", **toupdate_dict)

            create_to_transaction_dict = {"transaction_id": _transaction_id, "from_account": _from_account, "to_account": _to_account, "trans_type": _transaction_type, "amount": _amount, "status": _statusTo}
            db().insert('transaction', **create_to_transaction_dict)

            send_from_mail = statusMessage(from_email, "You have successfully sent " + str(_amount) + " " + from_currency + " to " + to_first_name + " " + to_last_name)

            send_from_mail = statusMessage(to_email, "You have successfully received " + str(_amount) + " " + to_currency + " from " + from_first_name + " " + from_last_name)

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
            data = db().select(sql)
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
    
    def VerifyCurrency():
        try:
            json = request.json
            _currency_code = json['currency_code']
            _receiver_phonenumber = json['receiver_phonenumber']
            _amount = json['amount']

            # checking amount
            if _amount <= 0:
                response = make_response(403, "less amount to transfer")
                return response
                
            # check user by phone number
            check_reciever = check_user_by_phonenumber(_receiver_phonenumber)
            if len(check_reciever) <= 0:
                response = make_response(403, "receiver account doesn't Exist")
                return response
            
            receiver_id = check_reciever[0]['user_id']

            # checking receiver wallet deatils
            check_reciever_wallets = get_wallet_details(receiver_id, _currency_code)
            if len(check_reciever_wallets) <= 0:
                response = make_response(403, "receiver doesn't have " + _currency_code + " wallet")
                return response
            
            # receiver wallet_id
            receiver_wallet_id = check_reciever_wallets[0]['wallet_id']
            response = make_response(100, receiver_wallet_id)
            return response
        except Exception as e:
            print(e)


            

# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})

def get_walletDetailsBy_walletId(walletId):
    sql = "SELECT * FROM `user_wallet` WHERE wallet_id = '" + walletId + "' "
    data = db().select(sql)
    return data
#getting all transactions for a specific wallet id
def get_transactions_details(walletId):
    sql = "SELECT * FROM `transaction` WHERE from_account = '" + walletId + "' OR to_account = '" + walletId + "' "
    data = db().select(sql)
    return data

# getting user by phone number
def check_user_by_phonenumber(phone):
    sql = "SELECT * FROM `user` WHERE phone_number = '" + phone + "' "
    data = db().select(sql)
    return data

# getting user by user_id
def check_user_by_id(userId):
    sql = "SELECT * FROM `user` WHERE user_id = '" + str(userId) + "' "
    data = db().select(sql)
    return data

# getting user wallet details
def get_wallet_details(userId, currency):
    sql = "SELECT * FROM `user_wallet` WHERE user_id = '" + str(userId) + "' AND currency_code = '" + currency + "' "
    data = db().select(sql)
    return data