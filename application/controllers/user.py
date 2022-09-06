
from flask import Blueprint, request, jsonify, json
from application.models.user import User

bp_app = Blueprint('mod_user', __name__)
# getting all users
@bp_app.route('/all_users')
def get_users():
    data = User.all_users()
    return data

# Creating a user
@bp_app.route('/add_user', methods=['POST'])
def add_user():
    data = User.userAdd()
    return data

# update a user
@bp_app.route('/update_user', methods=['PUT'])
def update_user():
    data = User.userUpdate()
    return data

# update user password
@bp_app.route('/update_user_password', methods=['PUT'])
def update_user_password():
    data = User.passwordUpdate()
    return data

# login a user
@bp_app.route('/login_user', methods=['POST'])
def login_user():
    data = User.loginUser()
    return data

# verfying loginOTP
@bp_app.route('/login_otp', methods=['POST'])
def login_otp():
    data = User.loginOtp()
    return data

# delete a user
@bp_app.route('/delete_user', methods=['DELETE'])
def delete_user():
    #isValid =  checkJWT
    #if is not isValidre
    #return an errr
    data = User.deleteUser()
    return data

# get user details by id
@bp_app.route('/get_user_by_id', methods=['POST'])
def get_user_by_id():
    data = User.getUserDetailsById()
    return data

# otp verification
@bp_app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = User.verifyOTP()
    return data

# get user details by email(iranks)
@bp_app.route('/get_user_by_email', methods=['POST'])
def get_user_details_by_email():
    data = User.getUserDetailsByEmail()
    return data

# forgot password(iranks)
@bp_app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = User.forgotPassword()
    return data

# password otp(iranks)
@bp_app.route('/password_otp', methods=['POST'])
def password_otp():
    data = User.passwordOtp()
    return data
# new password setting (iranks)
@bp_app.route('/setting_password', methods=['PUT'])
def setting_password():
    data = User.settingPassword()
    return data

# get user details by username (iranks)
@bp_app.route('/user_by_username', methods=['POST'])
def get_user_details_by_username():
    data = User.getUserDetailsByUsername()
    return data

#save user contacts (iranks)
@bp_app.route('/saving_contacts', methods=['PUT'])
def saveContact():
    data = User.saveContact()
    return data

#get saved contacts by user id (iranks)
@bp_app.route('/saved_contacts', methods=['POST'])
def get_saved_contacts_by_user_id():
    data = User.getSavedContactsByUserId()
    return data

#deleting saved contact(iranks)
@bp_app.route('/delete_contact', methods=['POST'])
def delete_contact():
    data = User.deleteContact()
    return data