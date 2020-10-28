import functools
from flask import g, Blueprint, url_for, session, redirect
from flask import render_template
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    print(f"session:{type(session)}, dir session:{dir(session)}")
    session['times'] = 1
    print(f"session:{session.__dict__}, dir session:{dir(session)}")
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    print(f"login times:{session}")
    session.clear()
    return redirect(url_for('index'))

