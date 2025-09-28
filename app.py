import os

from flask import Flask, render_template, request, redirect
from database import database
from flask import flash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config.from_object('config')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
database.init_app(app)
#csrf = CSRFProtect()
#csrf.init_app(app)

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("🚫 Soubor je příliš velký. Maximální velikost je 16 MB.", "danger")
    return redirect(request.url)

def is_active(target_url):
    return 'active' if request.path == target_url else ''

app.jinja_env.globals['is_active'] = is_active

@app.route('/')
def home_page():
    return render_template('home_page.jinja')

from views.user import user_bp
from views.profile import profile_bp
from views.role import role_bp
from views.restaurant import restaurant_bp
from views.manage_menu import manage_menu_bp
from views.cart import cart_bp
app.register_blueprint(user_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(role_bp)
app.register_blueprint(restaurant_bp)
app.register_blueprint(manage_menu_bp)
app.register_blueprint(cart_bp)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)




