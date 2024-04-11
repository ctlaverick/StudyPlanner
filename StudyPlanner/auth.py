from flask import Blueprint, render_template, session, flash, request, url_for, redirect
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

bp = Blueprint('auth', __name__,) #url_prefix='/'

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        email = request.form.get('email')
        name = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        email_check = User.query.filter_by(email=email).first() # Tries to find account with this email
        username_check = User.query.filter_by(email=email).first()
        
        if email_check: # if a user is found, redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('auth.register'))
        
        if username_check: #If there is an account with that username, redirect them back to register page
            flash('Username taken please try again')
            return redirect(url_for('auth.register'))
        
        if password1 != password2: #Makes sure passwords match
            flash('Passwords do not match')
            return redirect(url_for('auth.register'))
        
        #room to add password check for strength

        #Combines the users details into the User Model ready to be created in the database
        new_user = User(email=email, username=name, password=generate_password_hash(password1, method='scrypt'))
        
        #add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        #redirect them to login now
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('core.index'))
    
    return render_template('auth/login.html')
                

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index'))