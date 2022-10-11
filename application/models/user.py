import hashlib
import pathlib
from random import randint
import jwt
from datetime import datetime, timedelta
from application import application
import uuid
import phonenumbers
from flask import jsonify, request
from application.libs.sms import send
from application.libs.sms import sms
from application.libs.sms import on_finish 
from helper.dbhelper import Database as db
from application.models.user_wallet import UserWallet
from application.models.auth import token_required
import africastalking
import os
from application.libs.aws import s3, bucketName




application.config['SECRET_KEY'] = 'a6d4c1d6828549b6ada2d94ef4aeb9a1'
class User:
    def __init__(self):
        print('user model')

    @staticmethod
    def all_users():
        sql = "SELECT * FROM `user` "
        data = db().select(sql)
        return jsonify(data)


    @staticmethod
    def userAdd():
        try:
            _user_id = uuid.uuid4()
            _json = request.json
            _first_name = _json['first_name']
            _last_name = _json['last_name']
            _phone_number = _json['phone_number']
            _username = _json['username']
            _email = _json['email']
            _password = _json['password']
            _profile_pic = 'null'
            
            print(_phone_number)
            # hash password
            hash_password = hashlib.sha256(str(_password).encode('utf-8')).hexdigest()
            check_user = get_user_detail(_email, _phone_number)
            if len(check_user) > 0:
                return make_response(403, "User Already Exists")
            
            check_username = get_user_by_username(_username)
            if len(check_username) > 0:
                return make_response(403, "Username Already Exists")
                
            otp_generated = randint(0000,9999)

            #sending otp using africa stalking on user adding
            
            sms.send(str(otp_generated) + " " + "is the otp to verify your userdetails on clic. Generated otp doesnt expire unless used ", [_phone_number], callback=on_finish)

            status = 'pending'
            otp_sent = send(otp_generated, _email)
            print("start")
            addUser_dict = {"user_id": _user_id, "first_name": _first_name, "last_name": _last_name, "phone_number": _phone_number, "email": _email, "username": _username, "password": hash_password, "profile_pic": _profile_pic, "otp": otp_generated, "status": status}
            print(addUser_dict)
            data = db().insert('user', **addUser_dict)
            print(data)

            
            response = make_response(100, otp_sent)
            print(response)

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
            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **updatedUser_dict)

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
            

         
    #update user
    @staticmethod
    @token_required
    def userUpdate():
        try:
            _json = request.json
            _userId = _json['user_id']
            _first_name = _json['first_name']
            _last_name = _json['last_name']
            _phone_number = _json['phone_number']
            _email = _json['email']


            updateUser_dict = {"first_name": _first_name, "last_name": _last_name, "phone_number": _phone_number, "email": _email}

            db().Update('user', "user_id  =  '" + str(_userId) + "'", **updateUser_dict)

            response = make_response(100, "user updated successfully")

            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to update user")
            return response

    # update user password
    @staticmethod
    @token_required
    def passwordUpdate():
        try:
            _json = request.json
            _user_id = _json['user_id']
            _current_password = _json['current_password']
            _new_password = _json['new_password']
            _confirm_new_password = _json['confirm_new_password']

            # hash current password
            hash_current_password = hashlib.sha256(str(_current_password).encode('utf-8')).hexdigest()

            check_user_details = get_user_details_by_id_and_password(_user_id, hash_current_password)
            if len(check_user_details) <= 0:
                response = make_response(403, "invalid credentials")
                return response

            if _new_password != _confirm_new_password:
                response = make_response(403, "Password Mismatch")
                return response
            
            hash_new_password = hashlib.sha256(str(_new_password).encode('utf-8')).hexdigest()

            UpdateUser_dict = {"password": hash_new_password}

            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **UpdateUser_dict)

            response = make_response(100, "password updated successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "Failed to update password")
            return response
    

    #forgot password(iranks)
    @staticmethod
    def forgotPassword():
        try:
            _json = request.json
            
            _email = _json['email']

            check_user = get_user_by_email(_email)
            if len(check_user) <= 0:
                response = make_response(403, "Wrong Email")
                return response
            otp_generated = randint(0000,9999)

            #sending sms using africastalking on forgot password
            _phone_number = check_user[0]['phone_number']
            
            sms.send(str(otp_generated) + " " + "is the otp to verify your forgot password claim credentials on clic. Generated otp doesnt expire unless used ", [_phone_number], callback=on_finish)
            status = 'pending'
            _user_id = check_user[0]['user_id']
            otp_sent = send(otp_generated, _email)
            updateUser_dict = { "email": _email,  "otp": otp_generated, "status": status}
            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **updateUser_dict)
            

            
            response = make_response(100, "otp sent successfully")
            print(response)

            return response
        except Exception as e:
            print(e)
            response = make_response(403, "failure to send otp")
            return response

    #verify otp forgot password(iranks)
    @staticmethod
    def passwordOtp():
        try:
            _json = request.json
            _email = _json['email']
            _otp = _json['otp']
            check_usr_exist = get_user_by_email_and_otp(_email, _otp)

            if len(check_usr_exist) <= 0:
                response = make_response(403, "Wrong One Time Password")
                return response
            
            status = 'change'
            _user_id = check_usr_exist[0]['user_id']

            updateUser_dict = {"status": status}
            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **updateUser_dict)
            response = make_response(100, "OTP verified successfully")
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "Invalid OTP")
            return response
    
    #new password (iranks)
    @staticmethod
    def settingPassword():
        try:
            _json = request.json
        
            _email = _json['email']
            _new_password = _json['new_password']
            _confirm_new_password = _json['confirm_new_password']

            if _new_password != _confirm_new_password:
                response = make_response(403, "Password Mismatch")
                return response
            hash_new_password = hashlib.sha256(str(_new_password).encode('utf-8')).hexdigest()
            

            check_user = get_user_by_email(_email)
            status = check_user[0]['status']
            
            if len(check_user) <= 0:
                response = make_response(403, "email doesnt exist")
                return response
            if status != 'change':
                response = make_response(403, "can't change password first verify your email")
                return response

            status = 'Active'
            _user_id = check_user[0]['user_id']
            UpdateUser_dict = { "password": hash_new_password, "status": status}
            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **UpdateUser_dict)

            response = make_response(100, "password updated successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "Failed to change  password")
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
            print(check_user)

            if len(check_user) <= 0:
                data = make_response(403, "Invalid User")
                return data
            
            #sending otp while logging in
            otp_generated = randint(0000,9999)

            #sending sms using africas talking
            _phone_number = check_user[0]['phone_number']
            sms.send(str(otp_generated) + " " + "is the otp to verify your login credentials on clic. Generated otp doesnt expire unless used ", [_phone_number], callback=on_finish)

            status = 'pending'
            _user_id = check_user[0]['user_id']
            otp_sent = send(otp_generated, _email)
            print(otp_sent)
            updateUser_dict = { "otp": otp_generated, "status": status}
            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **updateUser_dict)
            response = make_response(100, "otp sent successfully to your email")
            
            return response

        except Exception as e:
            print(e)
            data = make_response(403, "can't send otp to user")
            return data

        #verifying otp for login
    @staticmethod
    def loginOtp():
        try:
            _json = request.json
            _email = _json['email']
            _otp = _json['otp']
            
            check_usr_exist = get_user_by_email_and_otp(_email, _otp)
            

            if len(check_usr_exist) <= 0:
                response = make_response(403, "Wrong otp")
                return response
            userId = check_usr_exist[0]['user_id']
            Userdata = get_user_details_by_id(userId)
            
            status = 'active'
            _user_id = check_usr_exist[0]['user_id']

            updateUser_dict = {"status": status}
            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **updateUser_dict)
            
            token = jwt.encode({
                'email': _email, 
                'expiration': str(datetime.now() + timedelta(hours=23))
            },
                application.config['SECRET_KEY'])
            response = user_logged_response(100, "user loggedin successfully", Userdata, token)
            return response
            
        except Exception as e:
            print(e)
            response = make_response(403, "Invalid OTP for login")
            return response

    # delete user
    @token_required
    def deleteUser():
        try:
            _json = request.json
            _user_id = _json['user_id']
            sql = "DELETE FROM `user` WHERE user_id = '" + str(_user_id) + "' "
            db().delete(sql)
            sql_wallet = "DELETE FROM `user_wallet` WHERE user_id = '" + str(_user_id) + "' "
            db().delete(sql_wallet)
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

    # get user detials by email(iranks)
    @staticmethod
    @token_required
    def getUserDetailsByEmail():
        try:
            _json = request.json
            _email = _json['email']

            data = get_user_details_by_email(_email)
            
            if len(data) <= 0:
                response = make_response(403, "No such user")
                return response

            response = jsonify(data)
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "failed to pull user with specific email")
            return response


    #save user contacts(iranks)
    @staticmethod
    @token_required
    def saveContact():
        try:
            _json = request.json
            _user_id = _json['user_id']
            _username = _json['username']
            
            check_saved = get_user_contacts(_user_id, _username)
            if len(check_saved) > 0:
                return make_response(403, "Username Already Exists in your favourites")
            data= get_user_by_username(_username)
            if len(data) <= 0:
                response = make_response(403, "wrong username")
                return response
            response = data
            
            
            
            
            _first_name =data[0]['first_name']
            _last_name = data[0]['last_name']
            _email = data[0]['email']
            _phone_number = data[0]['phone_number']
            _username = data[0]['username']


            # verify if the username exists

            # if yes, get his firstname, lastname, phone_number, email
            
            saveContact_dict = {"user_id": _user_id, "first_name": _first_name, "last_name": _last_name, "phone_number": _phone_number, "email": _email, "username": _username}
            print(saveContact_dict)
            data = db().insert('saved_contacts', **saveContact_dict)
            print(data)

            
            response = make_response(100, "user contact saved succcesfully")
            print(response)

            return response
        except Exception as e:
            print(e)
            response = make_response(403, "Invalid data types in saving contact")
            return response

    #get saved contacts by user_id(iranks)
    @staticmethod
    @token_required
    def getSavedContactsByUserId():
        try:
            _json = request.json
            _user_id = _json['user_id']

            data = get_saved_contacts_by_user_id(_user_id)
            
            if len(data) <= 0:
                response = make_response(403, "No saved contacts with this user id")
                return response

            response = jsonify(data)
            return response
        except Exception as e:
            print(e)
            response = make_response(403, "failed to pull saved contacts with this id")
            return response

    #deleting a saved contact(iranks)
    @token_required
    def deleteContact():
        try:
            _json = request.json
            _userId = _json['user_id']
            _username = _json['username']
            sql = "DELETE FROM `saved_contacts` WHERE user_id = '" + _userId + "' AND username = '" + _username + "' "
            
            db().delete(sql)
            
            response = make_response(100, "saved contact deleted successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "failed to delete saved contact")
            return response


    # profile pic update
    @token_required
    def profileUpdate():
        try:
            _files = request.files
            _form = request.form
            _receivedFile = _files['file']
            _user_id = _form['user_id']

            check_user = get_user_details_by_id(_user_id)
            if len(check_user) <= 0:
                response = make_response(403, "invalid user ID")
                return response

            generated_name = str(uuid.uuid4()) + pathlib.Path(_receivedFile.filename).suffix
            

            _receivedFile.save(generated_name)
            s3.upload_file(
                Bucket = bucketName,
                Filename=generated_name,
                Key = generated_name
            )
            path = "https://eremitphotos.s3.eu-west-2.amazonaws.com/" + generated_name
            print(path)

            

            prof_pic_dict = {"profile_pic": path}
            db().Update('user', "user_id  =  '" + str(_user_id) + "'", **prof_pic_dict)

            response = make_response(100, "file received successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response


    # get user details by username
    @token_required
    def getUserByUsername():
        try:
            _json = request.json
            _username = _json['username']

            check_user = get_user_by_username(_username)
            
            if len(check_user) <= 0:
                response = make_response(403, "user doesn't exist")
                return response

            first_name = check_user[0]['first_name']
            last_name = check_user[0]['last_name']

            response = make_response(100, str(first_name) + " " + str(last_name))
            return response

        except Exception as e:
            print(e)
            response = make_response(403, "wrong request")
            return response

            
            




















# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})

# user details
def get_user_details(Email, Password):
    sql = "SELECT * FROM `user` WHERE email = '" + Email + "' AND password = '" + Password + "' "
    data = db().select(sql)
    return data

# user details based on register model
def get_user_detail(Email, Phone_number):
    sql = "SELECT * FROM `user` WHERE email = '" + Email + "' OR phone_number = '" + Phone_number + "' "
    data = db().select(sql)
    return data
#user contacts based on user id and username
def get_user_contacts(user_id, username):
    sql = "SELECT * FROM `saved_contacts` WHERE user_id = '" + user_id + "' AND username = '" + username + "' "
    data = db().select(sql)
    return data



# user details based on id and current password
def get_user_details_by_id_and_password(UserId, CurrentPassword):
    sql = "SELECT * FROM `user` WHERE user_id = '" + UserId + "' AND password = '" + CurrentPassword + "' "
    data = db().select(sql)
    return data

#user details based on id and email (iranks)    
def get_user_details_by_id_and_email(UserId, email):
    sql = "SELECT * FROM `user` WHERE user_id = '" + UserId + "' AND email = '" + email + "' "
    data = db().select(sql)
    return data

#user details based 0on email an otp(iranks)
def get_user_by_email_and_otp(email, otp):
    sql = "SELECT * FROM `user` WHERE email = '" + email + "' AND otp = '" + otp + "' "
    data = db().select(sql)
    return data

    

# user details based on id and status(iranks)
def get_user_details_by_id_and_status(UserId, status):
    sql = "SELECT * FROM `user` WHERE user_id = '" + UserId + "' AND status = '" + status + "' "
    data = db().select(sql)
    return data


# get user details by id
def get_user_details_by_id(userId):
    sql = "SELECT * FROM `user` WHERE user_id = '" + str(userId) + "' "
    result = db().select(sql)
    data = [
        {
            "first_name": result[0]['first_name'], 
            "last_name": result[0]['last_name'], 
            "email": result[0]['email'],
            "username": result[0]['username'],
            "phone_number": result[0]['phone_number'],
            "profile_pic": result[0]['profile_pic'],
            "user_id": result[0]['user_id'],
            "status": result[0]['status'],
            "date_time": result[0]['date_time']
        }
        ]
    
    return data

# user created response
def user_created_response(status, message, data, Token):
    return jsonify({"data": data, "status": status, "message": message, "token": Token})

# user logged in response
def user_logged_response(status, message, data, Token):
    return jsonify({"message": message, "data": data, "status": status, "token": Token})

# get user by email(iranks)
def get_user_details_by_email(email):
    sql = "SELECT * FROM `user` WHERE email = '" + str(email) + "' "
    result = db().select(sql)
    data = [
        {
            "first_name": result[0]['first_name'], 
            "last_name": result[0]['last_name'], 
            "email": result[0]['email'],
            "username": result[0]['username'],
            "phone_number": result[0]['phone_number'],
            "user_id": result[0]['user_id'],
            "status": result[0]['status'],
            "date_time": result[0]['date_time']
        }
        ]
    return data

    # get user by email
def get_user_by_email(email):
    sql = "SELECT * FROM `user` WHERE email = '" + str(email) + "' "
    data = db().select(sql)
    return data



    # get user by username
def get_user_by_username(username):
    sql = "SELECT * FROM `user` WHERE username = '" + str(username) + "' "
    data = db().select(sql)
    return data

    # get user by otp(iranks)
def get_user_by_otp(otp):
    sql = "SELECT * FROM `user` WHERE otp = '" + str(otp) + "' "
    data = db().select(sql)
    return data

# get user data without password, otp
def get_mod_userdetail(Email, Phone_number):
    sql = "SELECT * FROM `user` WHERE email = '" + Email + "' OR phone_number = '" + Phone_number + "' "
    result = db().select(sql)
    data = [
        {
            "first_name": result[0]['first_name'], 
            "last_name": result[0]['last_name'], 
            "email": result[0]['email'],
            "username": result[0]['username'],
            "phone_number": result[0]['phone_number'],
            "user_id": result[0]['user_id'],
            "status": result[0]['status'],
            "date_time": result[0]['date_time']
        }
        ]
    return data

      # get saved contact by  user_id(iranks)
def get_saved_contacts_by_user_id(user_id):
    sql = "SELECT * FROM `saved_contacts` WHERE user_id = '" + str(user_id) + "' "
    data = db().select(sql)
    return data



