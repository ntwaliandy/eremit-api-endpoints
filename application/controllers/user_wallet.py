from crypt import methods
from flask import Blueprint, request, jsonify, json
from application.models.user_wallet import UserWallet

bp_app = Blueprint('mod_wallet', __name__)


# create other wallets
@bp_app.route('/create_other_wallet', methods=['POST'])
def createOtherWallet():
    data = UserWallet.otherWallets()
    return data


# delete a wallet
@bp_app.route('/user_delete_wallet', methods=['DELETE'])
def delete_wallet():
    data = UserWallet.deleteWallet()
    return data

# display all wallets
@bp_app.route('/all_wallets', methods=['GET'])
def all_wallets():
    data = UserWallet.allWallets()
    return data

# display user wallet details by user id

@bp_app.route('/user_wallet_details', methods=['POST'])
def wallet_details():
    data = UserWallet.getWalletDetails()
    return data


# displaying username from user wallet id
@bp_app.route('/username_byWalletID', methods=['POST'])
def username_byWalletID():
    data = UserWallet.getUsernamebyWalletID()
    return data