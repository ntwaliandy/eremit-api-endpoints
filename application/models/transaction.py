from datetime import datetime
from urllib import response
import os
import pymysql
import uuid
from flask import jsonify, request, json, redirect
from application.controllers.user_wallet import wallet_details
from helper.dbhelper import Database as db
from application.models.auth import token_required
from application.libs.sms import statusMessage
import requests
from random import randint

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
            _reason = _json['reason']

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
            to_last_name = check_to_personal_account[0]['last_name']

            _from_net_balance = check_from_balance - _amount
            fromupdate_dict = {"balance": _from_net_balance}
            db().Update('user_wallet', "wallet_id = '" + str(_from_account) + "'", **fromupdate_dict)
            
            create_from_transaction_dict = {"transaction_id": _transaction_id, "from_account": _from_account, "to_account": _to_account, "trans_type": _transaction_type, "amount": _amount, "reason": _reason, "status": _statusFrom}
            db().insert('transaction', **create_from_transaction_dict)


            _to_net_balance = check_to_user[0]['balance'] + _amount
            toupdate_dict = {"balance": _to_net_balance}
            db().Update('user_wallet', "wallet_id = '" + str(_to_account) + "'", **toupdate_dict)

            create_to_transaction_dict = {"transaction_id": _transaction_id, "from_account": _from_account, "to_account": _to_account, "trans_type": _transaction_type, "amount": _amount, "reason": _reason, "status": _statusTo}
            db().insert('transaction', **create_to_transaction_dict)
            
            print(to_last_name)
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


    #gettng all user transactions basing on user id
    @staticmethod
    @token_required
    def userTransactions():
        try:
            _json = request.json
            _user_id = _json['user_id']
            
            check_wallets = get_user_wallets(_user_id)
            response = make_response(100, check_wallets)
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "cant see transactions basing on id")
            return response    
    #verifyng currency
    def VerifyCurrency():
        try:
            json = request.json
            _sender_id = json['sender_id']
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
            check_sender_wallets = get_wallet_details(_sender_id, _currency_code)
            if len(check_reciever_wallets) <= 0:
                response = make_response(403, "receiver doesn't have " + _currency_code + " wallet")
                return response
            
            # receiver wallet_id
            receiver_wallet_id = check_reciever_wallets[0]['wallet_id']
            sender_wallet_id = check_sender_wallets[0]['wallet_id']
            response = make_response(100, {"sender_walletId": sender_wallet_id, "receiver_walletId": receiver_wallet_id})
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "can't make this transaction")
            return response

    # depositing to or from MM
    def deposit():
        try:
            _json = request.json
            _user_id = _json['user_id']
            _currency = _json['currency']
            _phoneNumber = _json['phone_number']
            _amount = _json['amount']
            _transType = _json['trans_type']

            

            tx = randint(000000, 999999)

            if _amount <= 0:
                response = make_response(403, "less amount transfer")
                return response

            if _transType == 'To_MM':
                check_wallet = get_wallet_details(_user_id, _currency)
                if len(check_wallet) <= 0:
                    response = make_response(403, "Wallet doesn't Exists")
                    return response
                walletId = check_wallet[0]['wallet_id']
                wallet_amount = check_wallet[0]['balance']
                
                if wallet_amount <= _amount:
                    response = make_response(403, "Not enough funds to withdraw")
                    return response

                latest_amount = wallet_amount - _amount
                updatedWallet_dict = {"balance": latest_amount}

                db().Update("user_wallet", "wallet_id = '" + str(walletId) + "'", **updatedWallet_dict)

                response = make_response(100, "You have successfully withdrawn " + str(_amount) + " " + _currency)
                return response

            elif _transType == 'From_MM':
                checkUser = check_user_by_id(_user_id)
                firstName = checkUser[0]['first_name']
                print(firstName)
                email = checkUser[0]['email']
                print(email)
                check_wallet = get_wallet_details(_user_id, _currency)
                if len(check_wallet) <= 0:
                    response = make_response(403, "Wallet doesn't Exists")
                    return response
                walletId = check_wallet[0]['wallet_id']
                wallet_amount = check_wallet[0]['balance']

                url = 'https://api.flutterwave.com/v3/charges?type=mobile_money_uganda'
                token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                hed = {'Authorization': 'Bearer ' + token}
                data = {
                    "phone_number": _phoneNumber,
                    "network": "MTN",
                    "amount": _amount,
                    "fullname": str(firstName),
                    "currency": _currency,
                    "email": str(email),
                    "tx_ref": str(tx),
                    "redirect_url": "http://18.116.9.199:9000/webhook",
                    "meta": {
                        "user_id": _user_id,
                        "wallet_id": walletId
                    }
                }

                result = requests.post(url, json=data, headers=hed)
                res = result.json()
                print(res)

                # response = make_response(100, "You have successfully deposited " + str(_amount) + " " + _currency)
                response = make_response(100, res)
                return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to make the transaction")
            return response

    
    # webhooks
    def webHooks():
        data = 'hey Andy'
        payload = request.args.to_dict()
        resp = payload['resp']
        res = json.loads(resp)
        if res['status'] == 'success':
            get_email = res['data']['customer.email']
            print(get_email)
            check_user = check_user_by_email(get_email)
            if len(check_user) <= 0:
                response = make_response(403, "Wrong Email")
                return response
            
            _user_id = check_user[0]['user_id']
            _currency = res['data']['currency']
            _amount = res['data']['amount']
            get_userWallet = get_wallet_details(_user_id, _currency)
            if len(get_userWallet) <= 0:
                response = make_response(403, "invalid wallet")
                return response
            _walletId = get_userWallet[0]['wallet_id']
            _currentBalance = get_userWallet[0]['balance']
            _newBalance = _currentBalance + _amount

            transDict = {"transaction_id": uuid.uuid4(), "from_account": "MM_UGANDA", "to_account": _walletId, "amount": _amount, "status": "debit", "trans_type": "mm_to_wallet", "reason": "deposited"}
            db().insert('transaction', **transDict)


            updatedWallet_dict = {"balance": _newBalance}
            db().Update("user_wallet", "wallet_id = '" + str(_walletId) + "'", **updatedWallet_dict)

            emaiSent = statusMessage(get_email, "You have successfuly Deposited " + str(_amount) + _currency + " to your " + " " + _currency + " WALLET")
            return redirect('http://18.116.9.199/eremit/#/dashboard')
        elif res['status'] == 'error':
            data = 'Wrong transaction or link expired'
            return data
        return data
            




            

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
    
# getting user by email
def check_user_by_email(email):
    sql = "SELECT * FROM `user` WHERE email = '" + email + "' "
    data = db().select(sql)
    return data

# getting user wallet details
def get_wallet_details(userId, currency):
    sql = "SELECT * FROM `user_wallet` WHERE user_id = '" + str(userId) + "' AND currency_code = '" + currency + "' "
    data = db().select(sql)
    return data

#check user walllets basing on user_id(iranks)
def get_user_wallets(userId):
    sql = "SELECT transaction.from_account, transaction.to_account, transaction.status, transaction.id, transaction.reason, transaction.date_time, transaction.amount, user_wallet.user_id, user_wallet.currency_code FROM transaction INNER JOIN user_wallet ON (transaction.from_account=user_wallet.wallet_id OR transaction.to_account=user_wallet.wallet_id) AND user_wallet.user_id= '" + str(userId) + "'"
    data = db().select(sql)
    return data
#check user transaction basing on time stamp(iranks)
def get_transaction_time(dateTime):
    sql = "SELECT * FROM `transaction` WHERE date_time = '" + str(dateTime) + "' "
    data = db().select(sql)
    return data
