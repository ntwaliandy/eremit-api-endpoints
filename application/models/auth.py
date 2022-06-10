from functools import wraps
from urllib import response
from flask import jsonify, request
import jwt
from application import application
from datetime import datetime
# requesting jwt token
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        data = request.headers.get('Authorization')
        token = str.replace(str(data), 'Bearer ', '')
        # print(data)
        # print(token)
        if data == None:
            return jsonify({'Alert!': 'Token missing'})
        
        try:
            data = jwt.decode(token, application.config['SECRET_KEY'], algorithms=['HS256'])
            if data['expiration'] < str(datetime.now()):
                return jsonify({"status": "token expired"})
        except Exception as e:
            print(e)
            response = make_response(403, "failed to decode the token")
            return response
        return func(*args, **kwargs)
    return decorated


def make_response(status, message):
    data = jsonify({"status": status, "message": message})
    return data
