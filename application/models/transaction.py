from flask import jsonify, request
import uuid
from helper.dbhelper import Database as db
from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder



class Transaction:
    def __init__(self):
        print("********** transaction model **********")


    # verify single wallet payment
    def verifySinglePayment():
        try:
            _json = request.json
            _userId = _json['user_id']
            _receiverName = _json['receiver_name']
            _amount = _json['amount']
            _assetType = _json['asset_type']


            if _amount <= 0:
                response = make_response(403, "LESS AMOUNT TO SEND")
                return response

            check_sender_user = get_user_by_id(_userId)
            if len(check_sender_user) <= 0:
                response = make_response(403, "INVALID SENDER USER")
                return response

            check_receiver_user = get_user_by_username(_receiverName)
            if len(check_receiver_user) <= 0:
                response = make_response(403, "INVALID RECEIVER USER")
                return response

            

            senderPubKey = check_sender_user[0]['pub_key']
            senderSecKey = check_sender_user[0]['sec_key']

            receiverPubKey = check_receiver_user[0]['pub_key']
            receiverSecKey = check_receiver_user[0]['sec_key']

            trans_id = str(uuid.uuid4())
            trans_dict = {"transaction_id": trans_id, "from_account": senderPubKey, "to_account": receiverPubKey, "status": "pending", "amount": _amount, "asset_type": _assetType, "trans_type": "P2P", "reason": ""}
            db().insert("eremit_db.transaction", **trans_dict)

            update_dict = {"senderPubKey": senderPubKey, "senderSecKey": senderSecKey, "receiverPubKey": receiverPubKey, "receiverSecKey": receiverSecKey, "asset_type": _assetType, "amount": _amount, "transaction_id": trans_id}

            response = make_response(100, update_dict)
            return response

        except Exception as e:
            print(str(e))
            response = make_response(403, "Can't Verify The Transaction")
            return response

    # send single payment
    def sendSinglePayment():
        try:
            _json = request.json

            _amount = _json['amount']
            _assetType = _json['asset_type']
            _receiverPubKey = _json['receiverPubKey']
            _receiverSecKey = _json['receiverSecKey']
            _senderPubKey = _json['senderPubKey']
            _senderSecKey = _json['senderSecKey']
            _transactionId = _json['transaction_id']
            _note = _json['message']

            # configuring horizon instance
            server = Server(horizon_url="https://horizon-testnet.stellar.org")

            # valid sequence number
            source_account = server.load_account(_senderPubKey)

            base_fee = 100

            # submit the transaction to the testNetwork
            transaction = TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=base_fee
            ).add_text_memo(_note).append_payment_op(_receiverPubKey, Asset.native(), str(_amount)).set_timeout(60).build()

            # sign the transaction with the SEC KEY
            transaction.sign(_senderSecKey)

            result = server.submit_transaction(transaction)
            is_sucess = result['successful']
            print(is_sucess)

            if is_sucess:
                update_dict = {"status": "success", "reason": _note}
                db().Update("eremit_db.transaction", "transaction_id = '" + _transactionId + "' ", **update_dict)

                response =  make_response(100, "Successfully Sent")
                return response

            else:
                update_dict = {"status": "failed", "reason": _note}
                db().Update("eremit_db.transaction", "transaction_id = '" + _transactionId + "' ", **update_dict)

                response =  make_response(100, "Failed to send")
                return response
                

        except Exception as e:
            print(str(e))
            response = make_response(403, str(e))
            return response




    # verifying path payment
    def VerifySendPathPayment():
        try:
            _json = request.json
            _userId = _json['user_id']
            _receiverUsername = _json['receiver_userName']
            _amount = _json['amount']
            _senderAssetCode = _json['sender_assetCode']
            _receiverAssetCode = _json['receiver_assetCode']


            server = Server(horizon_url="https://horizon-testnet.stellar.org")

            # checking amount
            if _amount <= 0:
                response = make_response(403, "LESS AMOUNT TO TRANSFER")
                return response

            # checking sending user
            check_sender_user = get_user_by_id(_userId)
            if len(check_sender_user) <= 0:
                response = make_response(403, "INVALID SENDER")

            # check receiving user
            check_receiver_user = get_user_by_username(_receiverUsername)
            if len(check_receiver_user) <= 0:
                response = make_response(403, "INVALID RECEIVER")
                return response

            _senderPubKey = check_sender_user[0]['pub_key']
            _senderSecKey = check_sender_user[0]['sec_key']

            _receiverPubKey = check_receiver_user[0]['pub_key']
            _receiverSecKey = check_receiver_user[0]['sec_key']

            sender_account = server.load_account(_senderPubKey)
            _senderAccountID = sender_account.account.account_id

            receiver_account = server.load_account(_receiverPubKey)
            _receiverAccountID = receiver_account.account.account_id

            response = make_response(100, {
                "senderPubKey": _senderPubKey,
                "senderSecKey": _senderSecKey,
                "senderAssetCode": _senderAssetCode,
                "senderAccountID": _senderAccountID,
                "receiverPubKey": _receiverPubKey,
                "receiverSecKey": _receiverSecKey,
                "receiverAssetCode": _receiverAssetCode,
                "receiverAccountID": _receiverAccountID,
                "amount": _amount
            })
            return response

        except Exception as e:
            response = make_response(403, str(e))
            return response

    # send path payment
    def sendPathPayment():
        try:
            _json = request.json
            _amount = _json['amount']
            _senderPubKey = _json['sender_pubKey']
            _senderSecKey = _json['sender_secKey']
            _senderAssetCode = _json['sender_assetCode']
            _senderAccountId = _json['sender_accountId']
            _receiverPubKey = _json['receiver_pubKey']
            _receiverSecKey = _json['receiver_secKey']
            _receiverAssetCode = _json['receiver_assetCode']
            _receiverAccountId = _json['receiver_accountId']


            server = Server(horizon_url="https://horizon-testnet.stellar.org")
            source_account = server.load_account(_senderPubKey)
            
            transaction = (
                TransactionBuilder(

                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100,
                ).append_path_payment_strict_receive_op(
                destination=_receiverPubKey,
                send_asset=Asset.native(),
                send_max=str(_amount),
                dest_asset=Asset("USD", "GC4MQOLFBOGBZ4GBNF7K7E56QUKNNX3BD4VREWMPDPHHUCABFNRS2A23"),
                dest_amount="5.50",
                path=[
                    Asset("USD", "GC4MQOLFBOGBZ4GBNF7K7E56QUKNNX3BD4VREWMPDPHHUCABFNRS2A23"),
                    Asset("EUR", "GCHOAJINSPAMUEHGD2NEPUXU7OD4ZQMJOR3JCMGKXYDCEOU4AXDBZ2FA")
                ]
                ).set_timeout(30).build()
                
                )

            transaction.sign(_senderSecKey)
            res = server.submit_transaction(transaction)

            print(res)

            response = make_response(100, "success")

        except Exception as e:
            response = make_response(403, str(e))
            return response







def make_response(status, message):
    return jsonify({"status": status, "message": message})


# get userdetails by ID
def get_user_by_id(userID):
    sql = "SELECT * FROM eremit_db.user WHERE user_id = '" + str(userID) + "' "
    data = db().select(sql)
    return data


# get userdetails by USERNAME
def get_user_by_username(userName):
    sql = "SELECT * FROM eremit_db.user WHERE username = '" + str(userName) + "' "
    data = db().select(sql)
    return data

#  check transaction by transaction ID
def get_trans_by_id(transID):
    sql = "SELECT * FROM eremit_db.transaction WHERE transaction_id = '" + str(transID) + "' AND status = pending" 
    data = db().select(sql)
    return data
    