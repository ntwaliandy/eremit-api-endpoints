import hashlib
from random import randint
import jwt
from datetime import datetime, timedelta
from application import application
import uuid
import phonenumbers
from flask import jsonify, request
from application.libs.sms import send
from helper.dbhelper import Database as db
from application.models.user_wallet import UserWallet
from application.models.auth import token_required


application.config['SECRET_KEY'] = 'a6d4c1d6828549b6ada2d94ef4aeb9a1'
class User:
    def __init__(self):
        print('user model')

    @staticmethod
    @token_required
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
            # hash password
            hash_password = hashlib.sha256(str(_password).encode('utf-8')).hexdigest()
            phoneNumber = phonenumbers.parse(_phone_number)
            check_phoneNumber = phonenumbers.is_possible_number(phoneNumber)
            check_user = get_user_detail(_email, _phone_number)
            if check_phoneNumber == False:
                return make_response(403, "Invalid phone number")
            if len(check_user) > 0:
                return make_response(403, "User Already Exists")
            
            otp_generated = randint(0000,9999)
            status = 'pending'
            otp_sent = send(otp_generated, _email)
            addUser_dict = {"user_id": _user_id, "first_name": _first_name, "last_name": _last_name, "phone_number": _phone_number, "email": _email, "password": hash_password, "profile_pic": _profile_pic, "otp": otp_generated, "status": status}
            data = db.insert('user', **addUser_dict)
            
            response = make_response(100, otp_sent)

            return response
        except Exception as e:
            print(e)
            response = make_response(403, "Invalid data types")
            return response

    # verify otp
    @staticmethod
    def verifyOTP():
        try:
            _json = request.json
            _email = _json['email']
            _requested_otp = _json['otp']

            check_user = get_user_by_email(_email)
            if len(check_user) <= 0:
                response = make_response(403, "Wrong Email")
                return response
            
            otp = check_user[0]['otp']
            if _requested_otp != otp:
                response = make_response(403, "Invalid OTP")
                return response
            status = 'Active'
            _user_id = check_user[0]['user_id']

            updatedUser_dict = {"status": status}
            db.Update('user', "user_id  =  '" + str(_user_id) + "'", **updatedUser_dict)

            create_user_wallet = UserWallet.createWallet(_user_id)
            userData = get_user_details_by_id(_user_id)

            # generating jwt for user sessions
            token = jwt.encode({
                'email': _email,
                'expiration': str(datetime.now() + timedelta(hours=24))
            },
                application.config['SECRET_KEY'])

            response = user_created_response(100, "user created successfully", userData, token)
            return response

        except Exception as e:
            print(e)
            return make_response(403, "can't register a user")
            

         

    @staticmethod
    @token_required
    def userUpdate():
        try:
            _json = request.json
            _userId = _json['user_id']
            _first_name = _json['first_name']
            _last_name = _json['last_name']
            _password = _json['password']
            _phone_number = _json['phone_number']
            _email = _json['email']
            _profile_pic = _json['profile_pic']

            # hash password
            hash_password = hashlib.sha256(str(_password).encode('utf-8')).hexdigest()

            updateUser_dict = {"first_name": _first_name, "last_name": _last_name, "phone_number": _phone_number, "email": _email, "password": hash_password, "profile_pic": _profile_pic}

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

            # hash password
            hash_password = hashlib.sha256(str(_password).encode('utf-8')).hexdigest()

            check_user = get_user_details(_email, hash_password)
            userId = check_user[0]['user_id']
            status = check_user[0]['status']
            Userdata = get_user_details_by_id(userId)

            if len(check_user) <= 0:
                data = make_response(403, "Invalid User")
                return data
            if status != 'Active':
                response = make_response(403, "can't log the user in")
                return response
            token = jwt.encode({
                'email': _email,
                'expiration': str(datetime.now() + timedelta(hours=23))
            },
                application.config['SECRET_KEY'])
            response = user_logged_response(100, "user loggedin successfully", Userdata, token)
            
            return response
        
        except Exception as e:
            print(e)
            print(check_user)
            data = make_response(403, "can't login in")
            return data

    # delete user
    @token_required
    def deleteUser():
        try:
            _json = request.json
            _user_id = _json['user_id']
            sql = "DELETE FROM `user` WHERE user_id = '" + str(_user_id) + "' "
            db.delete(sql)
            sql_wallet = "DELETE FROM `user_wallet` WHERE user_id = '" + str(_user_id) + "' "
            db.delete(sql_wallet)
            response = make_response(100, "user deleted successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to delete a user")
            return response

    # get user details by id
    @staticmethod
    @token_required
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
    result = db.select(sql)
    data = [
        {
            "first_name": result[0]['first_name'], 
            "last_name": result[0]['last_name'], 
            "email": result[0]['email'],
            "phone_number": result[0]['phone_number'],
            "user_id": result[0]['user_id'],
            "status": result[0]['status'],
            "date_time": result[0]['date_time']
        }
        ]
    return data

# user created response
def user_created_response(status, message, userId, Token):
    return jsonify({"user_id": userId, "status": status, "message": message, "token": Token})

# user logged in response
def user_logged_response(status, message, data, Token):
    return jsonify({"message": message, "data": data, "status": status, "token": Token})

# get user by email
def get_user_by_email(email):
    sql = "SELECT * FROM `user` WHERE email = '" + str(email) + "' "
    data = db.select(sql)
    return data

# get user data without password, otp
def get_mod_userdetail(Email, Phone_number):
    sql = "SELECT * FROM `user` WHERE email = '" + Email + "' OR phone_number = '" + Phone_number + "' "
    result = db.select(sql)
    data = [
        {
            "first_name": result[0]['first_name'], 
            "last_name": result[0]['last_name'], 
            "email": result[0]['email'],
            "phone_number": result[0]['phone_number'],
            "user_id": result[0]['user_id'],
            "status": result[0]['status'],
            "date_time": result[0]['date_time']
        }
        ]
    return data

