from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import string
import secrets

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    num=16
    res=''.join(secrets.choice(string.ascii_letters + string.digits)for x in range(num))
    app.config['SECRET_KEY'] = "this_is_the_secret_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    from authenticate import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app