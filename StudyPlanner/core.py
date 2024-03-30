from flask import Blueprint, render_template, session, flash, request, url_for, redirect

import calendar
from datetime import date

# from flask_sqlalchemy import SQLAlchemy # used for dealing with a sql database

# app = Flask(__name__)
# app.secret_key = "d71da3aa16a41e7005859041a8063229c1e84514118c8a41b0a03438225499e6" #used for sessions

bp = Blueprint('core', __name__, url_prefix='/')

@bp.route("/")
def index():
    user=None
    if 'username' in session:
        user=session['username']
    # flash('Hello, test!')
    return render_template("core/index.html", user=user)

@bp.route("/calendar/<string:username>")
def calendar_page(*args, **kwargs):

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

    return render_template("calendar.html", month=month_days, day_date=day_date, current_month=month)


# if __name__=="__main__":
#     app.run(debug=True)