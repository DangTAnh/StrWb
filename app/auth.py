from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from . import login_manager
from .db import db
from .forms import LoginForm
from .models import AdminUser

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login', next=request.path))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data.strip()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            session.permanent = True
            next_url = request.values.get('next')
            if not next_url or urlsplit(next_url).netloc or not next_url.startswith('/'):
                next_url = url_for('public.home')
            return redirect(next_url)
        flash('Sai tên đăng nhập hoặc mật khẩu', 'error')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công', 'success')
    return redirect(url_for('auth.login'))
