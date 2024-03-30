from flask import Blueprint, render_template, session, flash, request, url_for, redirect

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@bp.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')
                

@bp.route("/logout")
def logout():
    return redirect(url_for('index'))