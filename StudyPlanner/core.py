from flask import Blueprint, render_template, session, flash, request, url_for, redirect
from flask_login import current_user
import calendar
from datetime import date

from . import db
from .models import *

# from flask_sqlalchemy import SQLAlchemy # used for dealing with a sql database

# app = Flask(__name__)
# app.secret_key = "d71da3aa16a41e7005859041a8063229c1e84514118c8a41b0a03438225499e6" #used for sessions

bp = Blueprint('core', __name__) #url_prefix='/'

@bp.route("/")
def index():
    user=None
    if 'username' in session:
        user=session['username']
    # flash('Hello, test!')
    return render_template("core/index.html", user=user)

@bp.route("/modules", methods=['GET', 'POST'])
def modulesPage():
    user = current_user
    modules = current_user.modules
    # user = User.query.filter_by(id=current_user).first()

    if request.method =="POST":
        print(request)
        print(request.form.get('moduleName'))

        if request.form.get('moduleName'): #If the form has an input field of moduleName that contains data
            print("True")
            module = request.form.get('moduleName')

            #Combines the users details into the User Model ready to be created in the database
            new_module = Module(name=request.form.get('moduleName'), user=current_user.id)
        
            #add the new module to the database
            db.session.add(new_module)
            db.session.commit()
            return redirect(url_for('core.modulesPage'))
        
    return render_template("core/modules.html", user=user, modules=modules)


@bp.route("/modules/delete/<int:id>", methods=['GET'])
def deleteModule(id):

    module = Module.query.filter_by(id=id).first()
    print(module)
    db.session.delete(module)
    db.session.commit()
    return redirect(url_for('core.modulesPage'))

@bp.route("/modules/edit/<int:id>", methods=['GET','POST'])
def editModule(id):
    module = Module.query.filter_by(id=id).first()

    if request.method == 'POST':
        module.module_name = request.form.get('moduleName')
        db.session.commit()
        return redirect(url_for('core.modulesPage'))


    return render_template("core/editModule.html", module=module)



@bp.route("/tasks")
def tasksPage():
    user = current_user
    modules = user.modules
    return render_template("core/tasks.html", user=user, modules=modules)

@bp.route("/tasks/add/<int:module_id>", methods=['GET','POST'])
def addTask(module_id):
    user = current_user

    module = Module.query.filter_by(id=module_id).first()

    if request.method == 'POST':
        name = request.form.get('taskName')
        description = request.form.get('taskDescription')
        date = request.form.get('taskDueDate').split('-')
        time = request.form.get('taskDueTime').split(':')
        dateAndTime = date + time
        dateAndTime = [int(x) for x in dateAndTime] # changes the list to int not str
        due_date = datetime.datetime(*dateAndTime)
        new_task = Task(name=name, description=description, due_date=due_date, user=current_user.id, module=module.id)
        # create event for task to be added to the calendar on task creation
        db.session.add(new_task)
        db.session.commit()
        
        return redirect(url_for('core.tasksPage'))
    
    return render_template("core/addTask.html", user=user, module_id=module_id, module=module)

@bp.route("/tasks/delete/<string:author>/<int:id>", methods=['GET'])
def deleteTask(author, id):
    if author == current_user.get_id():
        task = Task.query.filter_by(id=id).first()
        print(task)

        db.session.delete(task)
        db.session.commit()

    return redirect(url_for('core.tasksPage'))

@bp.route("/tasks/edit/<string:author>/<int:id>", methods=['GET','POST'])
def editTask(author, id):
    if author == current_user.get_id():
        task = Task.query.filter_by(id=id).first()
        module = Module.query.filter_by(id=task.id).first()
        if request.method == 'POST':
            selectedModule = request.form.get('selectedModule')
            name = request.form.get('taskName')
            description = request.form.get('taskDescription')
            date = request.form.get('taskDueDate').split('-')
            time = request.form.get('taskDueTime').split(':')
            dateAndTime = date + time
            dateAndTime = [int(x) for x in dateAndTime] # changes the list to int not str (comprehension)
            due_date = datetime.datetime(*dateAndTime)
            print(selectedModule)
            db.session.query(Task).filter_by(id=id).update(dict(name=name, description=description, due_date=due_date, user=current_user.id, module=selectedModule))
            db.session.commit()

            return redirect(url_for('core.tasksPage'))
        print(task.due_date)
        date = str(task.due_date)
        date = date.split(" ")
        due_date = date[0]
        due_time = date[1]
        due_time = due_time[:-3]
        return render_template("core/editTask.html", task=task, module=module, due_date=due_date, due_time=due_time)
    
    return redirect(url_for('core.tasksPage'))

@bp.route("/events/calendar")
def calendarPage():

    userid = current_user.get_id()
    # user = db.get_or_404(User, id)
    

    cal = calendar.Calendar(firstweekday=0) # Creates a calendar with the first week day being monday
    today = date.today() # Gets today date
    year = today.year # Gets todays year
    month = today.month #gets todays month
    month_name = calendar.month_name[month]
    day_date = today.day # Gets todays day

    month_days = []
    week_days = []
    num = 0

    date1 = date(year, month, 1)
    date2 = date(year, (month+1), 1)
    events = Event.query.filter_by(user=userid).filter(Event.due_date.between(date1, date2)).all()
    userEvents = current_user.events
    # print(userEvents)
    # print(userEvents[1].due_date.day)


    #New Format
    # Generate list for the calendar [calendar]
    # List contains a sub list for week [ [week1], [week2], ...]
    # Which contains a sublist for day
    # which will include day, month, events
    # Then in the template loop through the calendar list for each week
    # Loop for each day
    # for each day print the day number
    # If it is the last month or current month change to a greyish colour
    # if the day is current day, highlight it
    #for event in day list, list the event names
    
    for day in cal.itermonthdates(year, month): #Generates list of weeks which are lists of days
        # print(day)
        num += 1
        events = Event.query.filter_by(user=userid).filter(Event.due_date.between(datetime.datetime(day.year, day.month, day.day, 0, 0, 0, 0), datetime.datetime(day.year, day.month, day.day, 23, 59, 59, 999999))).all()
        dayList = [day.day, day.month, events]
        week_days.append(dayList)
        if num % 7 == 0:
            month_days.append(week_days)
            week_days = []
            
    # print(month_days)
    todaysEvents = Event.query.filter_by(user=userid).filter_by(due_date = today).all()
    # print(todaysEvents)
    return render_template("core/calendar.html", month=month_days, day_date=day_date, current_month=month, month_name=month_name, todaysEvents=todaysEvents)

@bp.route("/Events/add", methods=['GET', 'POST'])
def addEvent():
    if request.method=='POST':
        module = request.form.get('module')
        task = request.form.get('task')
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date').split('-')
        time = request.form.get('time').split(':')

        dateAndTime = date + time
        dateAndTime = [int(x) for x in dateAndTime] # changes the list to int not str
        due_date = datetime.datetime(*dateAndTime)

        if task == "none":
            event = Event(user=current_user.get_id(), module=module, name=name, description=description, due_date=due_date)
        else:
            event = Event(user=current_user.get_id(), module=module, task=task, name=name, description=description, due_date=due_date)
        
        db.session.add(event)
        db.session.commit()

        return redirect(url_for('core.calendarPage'))
    
    return render_template("core/addEvent.html")