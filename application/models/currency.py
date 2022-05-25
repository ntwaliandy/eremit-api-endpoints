import pymysql
from flask import jsonify, request
from helper.dbhelper import Database as db

class Currency:
    def __init__(self):
        print('currency model')

    @staticmethod
    def createCurrency():
        try:
            _json = request.json
            _currency_name = _json['currency_name']
            _currency_code = _json['currency_code']

            check_currency = get_currency_details(_currency_name, _currency_code)
            if len(check_currency) > 0:
                response = make_response(403, "currency already exists")
                print(check_currency)
                return response
            
            currency_dict = {"currency_name": _currency_name, "currency_code": _currency_code}

            data = db.insert('currencies', **currency_dict)
            response = make_response(100, "currency created successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, 'failed to add a currency')
            return response
    
    # display all currencies
    @staticmethod
    def allCurrencies():
        sql = "SELECT * FROM currencies"
        data = db.select(sql)
        return jsonify(data)

    # delete a currency
    @staticmethod
    def deleteCurrency():
        try:
            _json = request.json
            _currencyId = _json['currency_id']
            sql = "DELETE FROM `currencies` WHERE currency_id = '" + str(_currencyId) + "' "
            db.delete(sql)
            response = make_response(100, "currency deleted successfully")
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "failed to delete the currency")
            return response


# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})

# currency details basing on code and name
def get_currency_details(Currency_name, Currency_code):
    sql = "SELECT * FROM `currencies` WHERE currency_code = '" + Currency_code + "' OR currency_name = '" + Currency_name + "' "
    data = db.select(sql)
    return data
