from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.html')
