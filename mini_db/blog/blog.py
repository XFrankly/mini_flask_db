from flask import redirect, render_template, flash, Blueprint, g

bp = Blueprint('blog', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('blog/index.html')

@bp.route('/summ')
def summ():
    return render_template('blog/summ.html')


