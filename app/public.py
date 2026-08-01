from flask import Blueprint, render_template, request, abort

from .models import Product

public_bp = Blueprint('public', __name__)


@public_bp.route('/', methods=['GET'])
def home():
    return render_template('public/index.html')


@public_bp.route('/search', methods=['GET'])
def search():
    q = (request.args.get('q') or '').strip()
    return render_template('public/search.html', q=q, products=None, pagination=None)
