
from flask import Blueprint, request, jsonify, json

from application.models.user_wallet import UserWallet

bp_app = Blueprint('mod_wallet', __name__)

@bp_app.route("/user_wallets", methods=['POST'])
def getUserWallets():
    data = UserWallet.getUserWallet()
    return data

# add asset
@bp_app.route("/add_asset", methods=['POST'])
def assetAdd():
    data = UserWallet.addAsset()
    return data
