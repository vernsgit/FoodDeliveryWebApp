from flask import session, redirect, url_for, flash
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("ℹ️Musíte se přihlásit, abyste mohli pokračovat.", "info")
            return redirect(url_for('login'))

        if 'user_id' in kwargs and kwargs['user_id'] != session.get('user_id'):
            flash('🚫Nemáte oprávnění přistupovat k těmto údajům.', 'danger')
            return redirect(url_for('home_page'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in allowed_roles:
                flash("🚫Nemáte oprávnění přistupovat na tuto stránku.", "danger")
                return redirect(url_for('home_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
