from flask import Blueprint, render_template
from flask_login import login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def _protect_admin():
    """Require login for every admin route."""
    pass


@admin_bp.route('/', methods=['GET'])
def dashboard():
    return render_template('admin/dashboard.html')
