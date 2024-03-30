from flask import Flask, render_template, session, flash, request, url_for, redirect

import calendar
from datetime import date

app = Flask(__name__)
app.secret_key = "d71da3aa16a41e7005859041a8063229c1e84514118c8a41b0a03438225499e6" #used for sessions

accounts = [
    {
        "Username": "username",
        "Password": "password",
        "Email": "username@email.com",
    },
    {
        "Username": "ctlaverick",
        "Password": "123",
        "Email": "ctlaverick@email.com",
        "Events": [ ["11/03/2024", "Assignment Due"], ["20/03/2024", "Chemistry Test"]],
    },
]

@app.route("/")
def index():
    user=None
    if 'username' in session:
        user=session['username']
    # flash('Hello, test!')
    return render_template("index.html", user=user)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET' and 'username' not in session:
        return render_template("register.html")
    
    elif request.method == 'GET' and'username' in session:
        flash(f'Already Logged in as {session["username"]}')
        return redirect(url_for('index'))
    
    elif request.method == 'POST':
        global accounts

        for account in accounts:
            if request.form['username'] == account["Username"]:
                flash("Username is taken. Enter a different one.", "error")
                return redirect(url_for('register'))
            
            elif request.form['email'] == account["Email"]:
                flash("Account registered with that email already.", "error") # Login with email / forgot username system to be added
                return redirect(url_for('register'))

        if request.form['password1'] == request.form['password2']:
            account = {
                "Username": request.form['username'],
                "Password": request.form['password1'],
                "Email": request.form['email']
            }
            accounts.append(account)
            flash(f"Account created for {request.form['username']}. You can now login", "success")
            return redirect(url_for('login'))
        
        else:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('register'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and 'username' not in session:
        return render_template("login.html")
    elif request.method == 'GET' and'username' in session:
        flash(f'Logged in as {session["username"]}')
        return redirect(url_for('index'))
    elif request.method == 'POST':
        global accounts
        for account in accounts:
            if request.form['username'] == account["Username"]:
                if request.form['password'] == account["Password"]:
                    session['username'] = request.form['username']
                    flash(f'You have been logged in as {session["username"]}', "success")
                    return redirect(url_for('index'))
        flash("Incorrect Username or Password", "error")
        return redirect(url_for('login'))
                

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

@app.route("/calendar/<string:username>")
def calendar_page(*args, **kwargs):

    if 'username' in session:
        user=session['username']
    else:
        return redirect(url_for('login'))
    
    for account in accounts:
        if account['username'] == user:
            user_account = account

    print(f"args: {args}")
    print(f"kwargs: {kwargs}")
    cal = calendar.Calendar(firstweekday=0)
    today = date.today()
    year = today.year
    custom_month = 0
    month = today.month + custom_month
    day_date = today.day

    month_days = []
    week_days = []
    num = 0

    for day in cal.itermonthdates(year, month): #Generates list of weeks which are lists of days
        num += 1
        week_days.append(day.day)
        if num % 7 == 0:
            month_days.append(week_days)
            week_days = []

    return render_template("calendar.html", month=month_days, day_date=day_date, current_month=month, username=session['username'], user=user)


if __name__=="__main__":
    app.run(debug=True)