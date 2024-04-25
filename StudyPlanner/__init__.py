from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy() # Has to be here to create the db instance before it is tried to be imported from .models

from StudyPlanner.models import *

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'd71da3aa16a41e7005859041a8063229c1e84514118c8a41b0a03438225499e6'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    with app.app_context():
        # db.drop_all() can be used to remove all tables in the databse
        db.create_all()

    from StudyPlanner import auth, core
    app.register_blueprint(auth.bp)
    app.register_blueprint(core.bp)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user to get the user object
        return User.query.get(int(user_id))

    return app