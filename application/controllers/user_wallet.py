from flask import Blueprint, request, jsonify, json
from application.models.user_wallet import UserWallet

bp_app = Blueprint('mod_wallet', __name__)


# creating a wallet
@bp_app.route('/user_create_wallet', methods=['POST'])
def create_wallet():
    data = UserWallet.createWallet()
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