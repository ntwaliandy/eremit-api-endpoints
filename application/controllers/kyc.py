
from flask import Blueprint

from application.models.kyc import Kyc
bp_app = Blueprint('mod_kyc', __name__)


# create kyc
@bp_app.route("/add_kyc", methods=['POST'])
def create_kyc():
    data = Kyc.createKyc()
    return data