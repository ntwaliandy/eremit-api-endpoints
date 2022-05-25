from flask import Blueprint, request, jsonify
from application.models.currency import Currency
bp_app = Blueprint('mod_currency', __name__)

# creating a currency
@bp_app.route('/create_currency', methods=['POST'])
def create_user():
    data = Currency.createCurrency()
    return data

# display all currencies
@bp_app.route('/all_currencies', methods=['GET'])
def all_currencies():
    data = Currency.allCurrencies()
    return data

# delete a currency
@bp_app.route('/delete_currency', methods=['DELETE'])
def delete_currency():
    data = Currency.deleteCurrency()
    return data