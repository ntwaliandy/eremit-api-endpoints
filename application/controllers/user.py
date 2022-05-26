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

# login a user
@bp_app.route('/login_user', methods=['POST'])
def login_user():
    data = User.loginUser()
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
