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
from application.libs.sms import on_finish
from application.libs.sms import sms
import africastalking
# from rave_python import Rave
from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder
from stellar_sdk.exceptions import NotFoundError, BadResponseError, BadRequestError


class Transaction:
    def __init__(self):
        print("transaction model")

    # create user transaction
    @staticmethod
    @token_required
    def createTransaction():
        try:
            _json = request.json
            
            _from_account = _json['from_account']
            _to_account = _json['to_account']
            _transaction_id = uuid.uuid4()
            _transaction_type = _json['trans_type']
            _amount = _json['amount']
            _reason = _json['reason']

            _statusTo = "debit" 
            _statusFrom = "credit"

            

            server = Server("https://horizon-testnet.stellar.org")
            source_key = Keypair.from_secret(_from_account)
            destination_id = _to_account 

            # First, check to make sure that the destination account exists.
            # You could skip this, but if the account does not exist, you will be charged
            # the transaction fee when the transaction fails.
            try:
                server.load_account(destination_id)
            except NotFoundError:
                # If the account is not found, surface an error message for logging.
                raise Exception("The destination account does not exist!")

            # If there was no error, load up-to-date information on your account.
            source_account = server.load_account(source_key.public_key)

            # Let's fetch base_fee from network
            base_fee = server.fetch_base_fee()

            # Start building the transaction.
            transaction = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                    base_fee=base_fee,
                )
                    # Because Stellar allows transaction in many currencies, you must specify the asset type.
                    # Here we are sending Lumens.
                    .append_payment_op(destination=destination_id, asset=Asset.native(), amount="40")
                    # A memo allows you to add your own metadata to a transaction. It's
                    # optional and does not affect how Stellar treats the transaction.
                    .add_text_memo("Test Transaction")
                    # Wait a maximum of three minutes for the transaction
                    .set_timeout(10)
                    .build()
            )

            # Sign the transaction to prove you are actually the person sending it.
            transaction.sign(source_key) 

            try:
                # And finally, send it off to Stellar!
                response = server.submit_transaction(transaction)
                print(f"Response: {response}")
            except (BadRequestError, BadResponseError) as err:
                print(f"Something went wrong!\n{err}")

            #checking for private and public key
            check_from_user = get_walletDetailsBy_walletSecret(_from_account)
            from_publicKey = check_from_user[0]['wallet_id']
            print(from_publicKey)
            check_to_user = get_walletDetailsBy_walletId(_to_account)
            to_secretKey = check_to_user[0]['wallet_secret']
            print(to_secretKey)
            # _json = request.json
            # _transaction_id = uuid.uuid4()
            # _from_account = _json['from_account']
            # _to_account = _json['to_account']
            # _transaction_type = _json['trans_type']
            # _receiver_money = _json['receiver_money']
            # _amount = _json['amount']
            # _reason = _json['reason']

            # _statusTo = "debit" 
            # _statusFrom = "credit"
            # #sending payment using stellar
            # #_statusFrom = "credit"
            # # _statusTo = "debit"
            # check_from_user = get_walletDetailsBy_walletId(_from_account)
            # from_secretKey = check_from_user[0]['secret_key']
            # print(from_secretKey)
            # check_to_user = get_walletDetailsBy_walletId(_to_account)
            # to_secretKey = check_to_user[0]['secret_key']
            # print(to_secretKey)
            # if len(check_from_user) <= 0:
            #     response = make_response(403, "Invalid sender account")
            #     return response
            # if len(check_to_user) <= 0:
            #     response = make_response(403, "invalid receiver account")
            #     return response
            # server = Server("https://horizon-testnet.stellar.org")
            # source_key = Keypair.from_secret(from_secretKey)
            # destination_id = _to_account

            # # First, check to make sure that the destination account exists.
            # # You could skip this, but if the account does not exist, you will be charged
            # # the transaction fee when the transaction fails.
            # try:
            #     server.load_account(destination_id)
            # except NotFoundError:
            #     # If the account is not found, surface an error message for logging.
            #     raise Exception("The destination account does not exist!")

            # # If there was no error, load up-to-date information on your account.
            # source_account = server.load_account(source_key.public_key)
            # print(source_account)

            # # Let's fetch base_fee from network
            # base_fee = server.fetch_base_fee()

            # # Start building the transaction.
            # transaction = (
            #     TransactionBuilder(
            #         source_account=source_account,
            #         network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            #         base_fee=base_fee,
            #     )
            #         # Because Stellar allows transaction in many currencies, you must specify the asset type.
            #         # Here we are sending Lumens.
            #         .append_payment_op(destination=destination_id, asset=Asset.native(), amount=_receiver_money)
            #         # A memo allows you to add your own metadata to a transaction. It's
            #         # optional and does not affect how Stellar treats the transaction.
            #         .add_text_memo("Test Transaction")
            #         # Wait a maximum of three minutes for the transaction
            #         .set_timeout(10)
            #         .build()
            # )

            # # Sign the transaction to prove you are actually the person sending it.
            # transaction.sign(source_key)

            # try:
            #     # And finally, send it off to Stellar!
            #     response = server.submit_transaction(transaction)
            #     print(f"Response: {response}")
            # except (BadRequestError, BadResponseError) as err:
            #     print(f"Something went wrong!\n{err}")

            # # _statusFrom = "credit"
            # # _statusTo = "debit"
            # # check_from_user = get_walletDetailsBy_walletId(_from_account)
            # # check_to_user = get_walletDetailsBy_walletId(_to_account)
            # # if len(check_from_user) <= 0:
            # #     response = make_response(403, "Invalid sender account")
            # #     return response
            # # if len(check_to_user) <= 0:
            # #     response = make_response(403, "invalid receiver account")
            # #     return response

            # # if _amount <= 0:
            # #     response = make_response(403, "less amount to transfer")
            # # if check_from_user == check_to_user:
            # #     response = make_response(403, "You can't send money to yourself plz!")
            # #     return response

            # # check_from_balance = check_from_user[0]['balance']
            
            # # if check_from_balance < _amount:
            # #     response = make_response(403, "Not enough funds to make this transaction")
            # #     return response

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

            #_checking_from_net_balance
            server = Server("https://horizon-testnet.stellar.org")
            public_key = from_publicKey
            account = server.accounts().account_id(public_key).call()
            for balance in account['balances']:
                print(f"Type: {balance['asset_type']}, Balance: {balance['balance']}")

            _from_net_balance = {balance['balance']}
            fromupdate_dict = {"balance": _from_net_balance}
            db().Update('user_wallet', "wallet_id = '" + str(from_publicKey) + "'", **fromupdate_dict)
            
            create_from_transaction_dict = {"transaction_id": _transaction_id, "from_account": from_publicKey, "to_account": _to_account, "trans_type": _transaction_type, "amount": _amount, "reason": _reason, "status": _statusFrom}
            db().insert('transaction', **create_from_transaction_dict)

            #checking to_net_balance
            server = Server("https://horizon-testnet.stellar.org")
            public_key = _to_account
            account = server.accounts().account_id(public_key).call()
            for balance in account['balances']:
                print(f"Type: {balance['asset_type']}, Balance: {balance['balance']}")

            _to_net_balance = {balance['balance']}
            toupdate_dict = {"balance": _to_net_balance}
            db().Update('user_wallet', "wallet_id = '" + str(_to_account) + "'", **toupdate_dict)

            create_to_transaction_dict = {"transaction_id": _transaction_id, "from_account": _from_account, "to_account": _to_account, "trans_type": _transaction_type, "amount": _amount, "reason": _reason, "status": _statusTo}
            db().insert('transaction', **create_to_transaction_dict)
            
            print(to_last_name)
            send_from_mail = statusMessage(from_email, "You have successfully sent " + str(_amount) + " " + from_currency + " to " + to_first_name + " " + to_last_name)

            #sending sms using africastalking
            from_phone_number = check_from_personal_account[0]['phone_number'] 
            sms.send("You have successfully sent " + str(_amount) + " " + from_currency + " to " + to_first_name + " " + to_last_name + "login on clic for more details of your transactions", [from_phone_number], callback=on_finish)

            send_from_mail = statusMessage(to_email, "You have successfully received " + str(_amount) + " " + to_currency + " from " + from_first_name + " " + from_last_name)
            
            #sending sms using africastalking
            to_phone_number = check_to_personal_account[0]['phone_number']
            sms.send("You have successfully received " + str(_amount) + " " + to_currency + " from " + from_first_name + " " + from_last_name + "login on clic for more details of your transactions", [to_phone_number], callback=on_finish)

            response = make_response(100, "transaction statement created")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "can't make a transaction")
            return response

    # display all transactions
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
    # def VerifyCurrency():
    #     try:
    #         _json = request.json
    #         _sender_id = _json['sender_id']
    #         _currency_code = _json['currency_code']
    #         _receiver_currency_code = _json['receiver_currency_code']
    #         _username = _json['username']
    #         _amount = _json['amount']

    #         # checking amount
    #         if _amount <= 0:
    #             response = make_response(403, "less amount to transfer")
    #             return response
                
    #         # check user by username
    #         check_reciever = check_user_by_username(_username)
    #         if len(check_reciever) <= 0:
    #             response = make_response(403, "receiver account doesn't Exist")
    #             return response
            
    #         receiver_id = check_reciever[0]['user_id']

    #         # checking receiver wallet deatils
    #         check_reciever_wallets = get_wallet_details(receiver_id, _receiver_currency_code)
    #         check_sender_wallets = get_wallet_details(_sender_id, _currency_code)
    #         if len(check_reciever_wallets) <= 0:
    #             response = make_response(403, "receiver doesn't have " + _receiver_currency_code + " wallet")
    #             return response

    #         to = _receiver_currency_code
    #         from_wallet = _currency_code
    #         url = "https://api.apilayer.com/exchangerates_data/convert?to=" + str(to) + "&from=" + str(from_wallet) + "&amount=" + str(_amount) + ""
    #         payload = {}
    #         headers= {
    #         "apikey": "o7cVMzxBZSiBYsiRtK6Od8H6zFzieYGV"
    #         }
    #         response = requests.get(url, headers=headers, data = payload)
    #         result = response.text
    #         res = json.loads(result)

    #         _receiving_money = res['result']
            
            
    #         # receiver wallet_id
    #         receiver_wallet_id = check_reciever_wallets[0]['wallet_id']
    #         sender_wallet_id = check_sender_wallets[0]['wallet_id']
    #         response = make_response(100, {"sender_walletId": sender_wallet_id, "receiver_walletId": receiver_wallet_id, "receiving_money": _receiving_money})
    #         return response
    #     except Exception as e:
    #         print(e)
    #         response = make_response(403, "can't make this transaction")
    #         return response

    # depositing to or from MM_UGANDA
    def deposit():
        try:
            _json = request.json
            _user_id = _json['user_id']
            _currency = _json['currency']
            _phoneNumber = _json['phone_number']
            _amount = _json['amount']
            _transType = _json['trans_type']

            

            tx = randint(000000, 999999)


            if _transType == 'To_MM':
                checkUser = check_user_by_id(_user_id)
                firstName = checkUser[0]['first_name']
                lastName = checkUser[0]['last_name']
                print(firstName)
                email = checkUser[0]['email']
                print(email)
                check_wallet = get_wallet_details(_user_id, _currency)
                if len(check_wallet) <= 0:
                    response = make_response(403, "Wallet doesn't Exists")
                    return response
                walletId = check_wallet[0]['wallet_id']
                wallet_amount = check_wallet[0]['balance']
                url = 'https://api.flutterwave.com/v3/transfers/fee?currency=' + _currency + '&amount= ' + str(_amount) + '&type=mobilemoney'
                token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                hed = {'Authorization': 'Bearer ' + token}
                result = requests.get(url, headers=hed)
                res = result.json()
                print(res)

                if _amount < 125000:
                    trans_fee = res['data'][0]['fee']
                    print(trans_fee)

                    sys_fee = 0.02 * _amount

                    totalCharge = trans_fee + sys_fee + _amount
                    print(totalCharge)
                    if totalCharge > wallet_amount:
                        response = make_response(403, "You don't have enough money to withdraw")
                        return response

                    url = 'https://api.flutterwave.com/v3/transfers'
                    token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                    hed = {'Authorization': 'Bearer ' + token}
                    data = {
                        "account_bank": "MPS",
                        "account_number": str(_phoneNumber),
                        "amount": _amount,
                        "narration": "UGX momo transfer",
                        "currency": _currency,
                        "reference": str(tx),
                        "beneficiary_name": firstName + ' ' + lastName
                    }
                    resultInit = requests.post(url, json=data, headers=hed)
                    resInit = resultInit.json()
                    print(resInit)

                    if resInit['status'] == 'success':
                        print('yesss')
                        process_data = resInit['data']['id']
                        url = 'https://api.flutterwave.com/v3/transfers/' + str(process_data)
                        token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                        hed = {'Authorization': 'Bearer ' + token}
                        trans_status = requests.get(url, headers=hed)
                        trans_res = trans_status.json()
                        print(trans_res)
                        if len(trans_res) <= 0:
                            response = make_response(403, "can't process the transafer right now")
                            return response

                        if trans_res['data']['status'] != 'SUCCESSFUL':
                            response = make_response(403, "failed to pull the transaction details. fallBack Action")
                            return response
                        
                        latest_amount = wallet_amount - totalCharge
                        updatedWallet_dict = {"balance": latest_amount}

                        db().Update("user_wallet", "wallet_id = '" + str(walletId) + "'", **updatedWallet_dict)
                        trans_id = uuid.uuid4()
                        trans_dict = {"transaction_id": trans_id, "from_account": walletId, "to_account": "MOBILE MONEY", "trans_type": _transType, "amount": totalCharge, "reason": "withdrawn", "status": "credit"}
                        db().insert('transaction', **trans_dict)
                        statusMessage(email, "You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET.")

                        #sending using africastalking
                        sms.send("You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET." + "login on clic for more details of your transactions", [_phoneNumber], callback=on_finish)

                        response = make_response(100, str(_amount) + " " + _currency + " transferred successfully")
                        return response


                elif _amount >= 125000:
                    fee = res['data'][1]['fee']
                    
                    trans_fee = _amount * fee

                    sys_fee = 0.02 * _amount

                    totalCharge = trans_fee + sys_fee + _amount
                    if totalCharge > wallet_amount:
                        response = make_response(403, "You don't have enough money to withdraw")
                        return response

                    url = 'https://api.flutterwave.com/v3/transfers'
                    token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                    hed = {'Authorization': 'Bearer ' + token}
                    data = {
                        "account_bank": "MPS",
                        "account_number": str(_phoneNumber),
                        "amount": _amount,
                        "narration": "UGX momo transfer",
                        "currency": _currency,
                        "reference": str(tx),
                        "beneficiary_name": firstName + ' ' + lastName
                    }
                    resultInit = requests.post(url, json=data, headers=hed)
                    resInit = resultInit.json()
                    print(resInit)

                    if resInit['status'] == 'success':
                        print('yesss')
                        process_data = resInit['data']['id']
                        url = 'https://api.flutterwave.com/v3/transfers/' + str(process_data)
                        token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                        hed = {'Authorization': 'Bearer ' + token}
                        trans_status = requests.get(url, headers=hed)
                        trans_res = trans_status.json()
                        print(trans_res)
                        if len(trans_res) <= 0:
                            response = make_response(403, "can't process the transafer right now")
                            return response

                        if trans_res['data']['status'] != 'SUCCESSFUL':
                            response = make_response(403, "failed to pull the transaction details. fallBack Action")
                            return response
                        
                        latest_amount = wallet_amount - totalCharge
                        updatedWallet_dict = {"balance": latest_amount}

                        db().Update("user_wallet", "wallet_id = '" + str(walletId) + "'", **updatedWallet_dict)
                        trans_id = uuid.uuid4()
                        trans_dict = {"transaction_id": trans_id, "from_account": walletId, "to_account": "MOBILE MONEY", "trans_type": _transType, "amount": totalCharge, "reason": "withdrawn", "status": "credit"}
                        db().insert('transaction', **trans_dict)
                        statusMessage(email, "You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET.")

                        #sending sms using africastalking
                        sms.send("You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET." + "login on clic for more details of your transactions", [_phoneNumber], callback=on_finish)

                        response = make_response(100, str(_amount) + " " + _currency + " transferred successfully")
                        return response
                    

            elif _transType == 'From_MM':
                if _amount <= 999:
                    response = make_response(403, "less amount transfer")
                    return response
                checkUser = check_user_by_id(_user_id)
                firstName = checkUser[0]['first_name']
                lastName = checkUser[0]['last_name']
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
                    "fullname": str(firstName) + " " + str(lastName),
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
            response = make_response(403, "slow network")
            return response

    
    # depositing to or from MM_RWANDA
    def depositRwanda():
        try:
            _json = request.json
            _user_id = _json['user_id']
            _currency = _json['currency']
            _phoneNumber = _json['phone_number']
            _amount = _json['amount']
            _transType = _json['trans_type']

            

            tx = randint(000000, 999999)


            if _transType == 'To_MM':
                checkUser = check_user_by_id(_user_id)
                firstName = checkUser[0]['first_name']
                lastName = checkUser[0]['last_name']
                print(firstName)
                email = checkUser[0]['email']
                print(email)
                check_wallet = get_wallet_details(_user_id, _currency)
                if len(check_wallet) <= 0:
                    response = make_response(403, "Wallet doesn't Exists")
                    return response
                walletId = check_wallet[0]['wallet_id']
                wallet_amount = check_wallet[0]['balance']
                url = 'https://api.flutterwave.com/v3/transfers/fee?currency=' + _currency + '&amount= ' + str(_amount) + '&type=mobilemoney'
                token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                hed = {'Authorization': 'Bearer ' + token}
                result = requests.get(url, headers=hed)
                res = result.json()
                print(res)

                if _amount < 125000:
                    trans_fee = res['data'][0]['fee']
                    print(trans_fee)

                    sys_fee = 0.02 * _amount

                    totalCharge = trans_fee + sys_fee + _amount
                    print(totalCharge)
                    if totalCharge > wallet_amount:
                        response = make_response(403, "You don't have enough money to withdraw")
                        return response

                    url = 'https://api.flutterwave.com/v3/transfers'
                    token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                    hed = {'Authorization': 'Bearer ' + token}
                    data = {
                        "account_bank": "MPS",
                        "account_number": str(_phoneNumber),
                        "amount": _amount,
                        "narration": "RWF MOMO TRANSFER",
                        "currency": _currency,
                        "reference": str(tx),
                        "beneficiary_name": firstName + ' ' + lastName
                    }
                    resultInit = requests.post(url, json=data, headers=hed)
                    resInit = resultInit.json()
                    print(resInit)

                    if resInit['status'] == 'success':
                        print('yesss')
                        process_data = resInit['data']['id']
                        url = 'https://api.flutterwave.com/v3/transfers/' + str(process_data)
                        token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                        hed = {'Authorization': 'Bearer ' + token}
                        trans_status = requests.get(url, headers=hed)
                        trans_res = trans_status.json()
                        print(trans_res)
                        if len(trans_res) <= 0:
                            response = make_response(403, "can't process the transafer right now")
                            return response

                        if trans_res['data']['status'] != 'SUCCESSFUL':
                            response = make_response(403, "failed to pull the transaction details. fallBack Action")
                            return response
                        
                        latest_amount = wallet_amount - totalCharge
                        updatedWallet_dict = {"balance": latest_amount}

                        db().Update("user_wallet", "wallet_id = '" + str(walletId) + "'", **updatedWallet_dict)
                        trans_id = uuid.uuid4()
                        trans_dict = {"transaction_id": trans_id, "from_account": walletId, "to_account": "MOBILE MONEY", "trans_type": _transType, "amount": totalCharge, "reason": "withdrawn", "status": "credit"}
                        db().insert('transaction', **trans_dict)
                        statusMessage(email, "You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET.")
                        
                        #sending sms using africastalking
                        sms.send("You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET." + "login on clic for more details of your transactions", [_phoneNumber], callback=on_finish)

                        response = make_response(100, str(_amount) + " " + _currency + " transferred successfully")
                        return response


                elif _amount >= 125000:
                    trans_fee = res['data'][0]['fee']

                    sys_fee = 0.02 * _amount

                    totalCharge = trans_fee + sys_fee + _amount
                    if totalCharge > wallet_amount:
                        response = make_response(403, "You don't have enough money to withdraw")
                        return response

                    url = 'https://api.flutterwave.com/v3/transfers'
                    token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                    hed = {'Authorization': 'Bearer ' + token}
                    data = {
                        "account_bank": "MPS",
                        "account_number": str(_phoneNumber),
                        "amount": _amount,
                        "narration": "RWF MOMO TRANSFER",
                        "currency": _currency,
                        "reference": str(tx),
                        "beneficiary_name": firstName + ' ' + lastName
                    }
                    resultInit = requests.post(url, json=data, headers=hed)
                    resInit = resultInit.json()
                    print(resInit)

                    if resInit['status'] == 'success':
                        print('yesss')
                        process_data = resInit['data']['id']
                        url = 'https://api.flutterwave.com/v3/transfers/' + str(process_data)
                        token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                        hed = {'Authorization': 'Bearer ' + token}
                        trans_status = requests.get(url, headers=hed)
                        trans_res = trans_status.json()
                        print(trans_res)
                        if len(trans_res) <= 0:
                            response = make_response(403, "can't process the transafer right now")
                            return response

                        if trans_res['data']['status'] != 'SUCCESSFUL':
                            response = make_response(403, "failed to pull the transaction details. fallBack Action")
                            return response
                        
                        latest_amount = wallet_amount - totalCharge
                        updatedWallet_dict = {"balance": latest_amount}

                        db().Update("user_wallet", "wallet_id = '" + str(walletId) + "'", **updatedWallet_dict)
                        trans_id = uuid.uuid4()
                        trans_dict = {"transaction_id": trans_id, "from_account": walletId, "to_account": "MOBILE MONEY", "trans_type": _transType, "amount": totalCharge, "reason": "withdrawn", "status": "credit"}
                        db().insert('transaction', **trans_dict)
                        statusMessage(email, "You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET.")
                        
                        #sending sms using africastalking
                        sms.send("You have successfully withdrawn " + str(_amount) + _currency + " from your " + _currency + " WALLET." + "login on clic for more details of your transactions", [_phoneNumber], callback=on_finish)

                        response = make_response(100, str(_amount) + " " + _currency + " transferred successfully")
                        return response
                    

            elif _transType == 'From_MM':
                if _amount <= 999:
                    response = make_response(403, "less amount transfer")
                    return response
                checkUser = check_user_by_id(_user_id)
                firstName = checkUser[0]['first_name']
                lastName = checkUser[0]['last_name']
                print(firstName)
                email = checkUser[0]['email']
                print(email)
                check_wallet = get_wallet_details(_user_id, _currency)
                if len(check_wallet) <= 0:
                    response = make_response(403, "Wallet doesn't Exists")
                    return response
                walletId = check_wallet[0]['wallet_id']
                wallet_amount = check_wallet[0]['balance']

                url = 'https://api.flutterwave.com/v3/charges?type=mobile_money_rwanda'
                token = 'FLWSECK-dd838ce5bf5cc79bd08b897660f00b14-X'
                hed = {'Authorization': 'Bearer ' + token}
                data = {
                    "phone_number": _phoneNumber,
                    "network": "MTN",
                    "amount": _amount,
                    "fullname": str(firstName) + " " + str(lastName),
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
            response = make_response(403, "slow network")
            return response

    # webhooks
    def webHooks():
        data = 'Unexpected Error occurred'
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

def get_walletDetailsBy_walletSecret(walletSecret):
    sql = "SELECT * FROM `user_wallet` WHERE wallet_secret = '" + walletSecret + "' "
    data = db().select(sql)
    return data
#getting all transactions for a specific wallet id
def get_transactions_details(walletId):
    sql = "SELECT * FROM `transaction` WHERE from_account = '" + walletId + "' OR to_account = '" + walletId + "' "
    data = db().select(sql)
    return data

# getting user by username
def check_user_by_username(Username):
    sql = "SELECT * FROM `user` WHERE username = '" + str(Username) + "' "
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
    sql = "SELECT transaction.from_account, transaction.to_account, transaction.status, transaction.id, transaction.transaction_id, transaction.reason, transaction.date_time, transaction.amount, user_wallet.user_id, user_wallet.currency_code FROM transaction INNER JOIN user_wallet ON (transaction.from_account=user_wallet.wallet_id OR transaction.to_account=user_wallet.wallet_id) AND user_wallet.user_id= '" + str(userId) + "'" + " ORDER BY transaction.date_time DESC LIMIT 8"
    data = db().select(sql)
    return data
#check user transaction basing on time stamp(iranks)
def get_transaction_time(dateTime):
    sql = "SELECT * FROM `transaction` WHERE date_time = '" + str(dateTime) + "' "
    data = db().select(sql)
    return data
