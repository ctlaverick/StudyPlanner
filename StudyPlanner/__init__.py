from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .models import *

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'd71da3aa16a41e7005859041a8063229c1e84514118c8a41b0a03438225499e6'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)


    with app.app_context():
        db.create_all()

    from . import auth, core
    app.register_blueprint(auth.bp)
    app.register_blueprint(core.bp)

    return app