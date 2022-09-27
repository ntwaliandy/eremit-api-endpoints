import os
import uuid
from application.models.auth import token_required
from flask import jsonify, request
import pathlib
from helper.dbhelper import Database as db



class Kyc:
    def __init__(self):
        print("kyc model")

    # profile pic update
    @token_required
    def createKyc():
        try:
            _files = request.files
            _form = request.form
            _user_id = _form['user_id']
            _first_name = _form['first_name']
            _last_name = _form['last_name']
            _gender = _form['gender']
            _date_of_birth = _form['date_of_birth']
            _nin = _form['nin']
            _status = _form['status']
            _personalPic = _files['personal_pic']
            _frontPic = _files['front_pic']
            _backPic = _files['back_pic']
            

            check_user = get_userDetails_by_id(_user_id)
            if len(check_user) > 0:
                response = make_response(403, "User Already Exists")
                return response

            generated_personal_name = str(uuid.uuid4()) + pathlib.Path(_personalPic.filename).suffix
            generated_front_name = str(uuid.uuid4()) + pathlib.Path(_frontPic.filename).suffix
            generated_back_name = str(uuid.uuid4()) + pathlib.Path(_backPic.filename).suffix
            folder = "/var/www/html/eremit_uploads/"

            _personalPic.save(os.path.join(folder, generated_personal_name))
            _frontPic.save(os.path.join(folder, generated_front_name))
            _backPic.save(os.path.join(folder, generated_back_name))
            personal_path = "http://18.116.9.199/eremit_uploads/" + generated_personal_name
            front_path = "http://18.116.9.199/eremit_uploads/" + generated_front_name
            back_path = "http://18.116.9.199/eremit_uploads/" + generated_back_name

            

            kyc_dict = {"user_id": _user_id, "first_name": _first_name, "last_name": _last_name, "gender": _gender, "date_of_birth": _date_of_birth, "nin": _nin, "status": _status, "front_pic": front_path, "back_pic": back_path, "personal_pic": personal_path}
            db().insert('kyc', **kyc_dict)

            response = make_response(100, "Kyc sent successfully")
            return response

        except Exception as e:
            print(e)
            response = make_response(403, str(e))
            return response


# responses
def make_response(status, message):
    return jsonify({"message": message, "status": status})


    # checking user by user_id in kyc table
def get_userDetails_by_id(userID):
    sql = "SELECT * FROM `kyc` WHERE user_id = '" + str(userID) + "' "
    data = db().select(sql)
    return data