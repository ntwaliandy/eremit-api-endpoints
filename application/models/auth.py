from functools import wraps
from flask import jsonify, request
import jwt
from application import application
# requesting jwt token
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        data = request.headers['Authorization']
        token = str.replace(str(data), 'Bearer ', '')
        print(token)
        if not token:
            return jsonify({'Alert!': 'Token missing'})
        try:
            data = jwt.decode(token, application.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            print(e)
            return jsonify({"Error": str(e)})
        return func(*args, **kwargs)
    return decorated
