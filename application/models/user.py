import pymysql
import uuid
from flask import jsonify, request
from helper.dbhelper import Database as db
from application.models.user_wallet import UserWallet

class User:
    def __init__(self):
        print('user model')

    @staticmethod
    def all_users():
        sql = "SELECT * FROM `user` "
        data = db.select(sql)
        return jsonify(data)
    @staticmethod
    def userAdd():
        try:
            _user_id = uuid.uuid4()
            _json = request.json
            _first_name = _json['first_name']
            _last_name = _json['last_name']
            _phone_number = _json['phone_number']
            _email = _json['email']
            _password = _json['password']
            _profile_pic = _json['profile_pic']

            check_user = get_user_detail(_email, _phone_number)
            if len(check_user) > 0:
                return make_response(403, "User Already Exists")
            
            addUser_dict = {"user_id": _user_id, "first_name": _first_name, "last_name": _last_name, "phone_number": _phone_number, "email": _email, "password": _password, "profile_pic": _profile_pic}
            data = db.insert('user', **addUser_dict)
            create_user_wallet = UserWallet.createWallet(_user_id)
            response = jsonify(_user_id)

            return response
        except Exception as e:
            print(e)
            response = make_response(403, "Invalid data types")
            return response

    @staticmethod
    def userUpdate():
        try:
            _json = request.json
            _userId = _json['user_id']
            _first_name = _json['first_name']
            _last_name = _json['last_name']
            _phone_number = _json['phone_number']
            _email = _json['email']
            _profile_pic = _json['profile_pic']

            updateUser_dict = {"first_name": _first_name, "last_name": _last_name, "phone_number": _phone_number, "email": _email, "profile_pic": _profile_pic}

            db.Update('user', "user_id  =  '" + str(_userId) + "'", **updateUser_dict)

            response = make_response(100, "user updated successfully")

            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to update user")
            return response
    

    # login user
    @staticmethod
    def loginUser():
        try:
            _json = request.json
            _email = _json['email']
            _password = _json['password']

            check_user = get_user_details(_email, _password)

            if len(check_user) <= 0:
                data = make_response(403, "failed to log in")
                return data

            return make_response(100, "user logged in successfully")
        
        except Exception as e:
            print(e)
            data = make_response(403, "failed to login user !!!")
            return data

    # delete user
    def deleteUser():
        try:
            _json = request.json
            _user_id = _json['user_id']
            sql = "DELETE FROM `user` WHERE user_id = '" + str(_user_id) + "' "
            db.delete(sql)
            response = make_response(100, "user deleted successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to delete a user")
            return response

    # get user details by id
    @staticmethod
    def getUserDetailsById():
        try:
            _json = request.json
            _user_id = _json['user_id']

            data = get_user_details_by_id(_user_id)
            if len(data) <= 0:
                response = make_response(403, "No such user")
                return response

            response = jsonify(data)
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "failed to pull user with specific ID")
            return response

            


# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})

# user details
def get_user_details(Email, Password):
    sql = "SELECT * FROM `user` WHERE email = '" + Email + "' AND password = '" + Password + "' "
    data = db.select(sql)
    return data

# user details based on register model
def get_user_detail(Email, Phone_number):
    sql = "SELECT * FROM `user` WHERE email = '" + Email + "' OR phone_number = '" + Phone_number + "' "
    data = db.select(sql)
    return data

# get user details by id
def get_user_details_by_id(userId):
    sql = "SELECT * FROM `user` WHERE user_id = '" + str(userId) + "' "
    data = db.select(sql)
    return data
