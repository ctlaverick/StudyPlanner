from flask import Blueprint, render_template, session, flash, request, url_for, redirect
from flask_login import current_user, login_required
import calendar
from datetime import date

from . import db
from .models import *

bp = Blueprint('core', __name__) #url_prefix='/' can be used to set a specifc url route for the pages in this blueprint

@bp.route("/")
def index():
    return render_template("core/index.html")

@bp.route("/modules", methods=['GET', 'POST'])
@login_required
def modulesPage():
    user = current_user
    modules = current_user.modules
    # user = User.query.filter_by(id=current_user).first()

    if request.method =="POST":
        if request.form.get('moduleName'): #If the form has an input field of moduleName that contains data
            name = request.form.get('moduleName')
            colour = request.form.get('moduleColour')

            #Combines the users details into the User Model ready to be created in the database
            new_module = Module(user=current_user.id, name=name, colour=colour)
        
            #add the new module to the database
            db.session.add(new_module)
            db.session.commit()
            return redirect(url_for('core.modulesPage'))
        
    return render_template("core/modules.html", user=user, modules=modules)


@bp.route("/modules/delete/<int:id>", methods=['GET'])
@login_required
def deleteModule(id):
    module = Module.query.filter_by(id=id).first()
    if current_user.id == module.user:
        db.session.delete(module)
        db.session.commit()
    return redirect(url_for('core.modulesPage'))

@bp.route("/modules/edit/<int:id>", methods=['GET','POST'])
@login_required
def editModule(id):
    module = Module.query.filter_by(id=id).first()
    if current_user.id != module.user:
        return redirect(url_for('core.modulesPage'))
    
    if request.method == 'POST':
        module.name = request.form.get('moduleName')
        module.colour = request.form.get('moduleColour') 
        db.session.commit()
        return redirect(url_for('core.modulesPage'))
    
    return render_template("core/editModule.html", module=module)



@bp.route("/tasks")
@login_required
def tasksPage():
    user = current_user
    modules = user.modules
    return render_template("core/tasks.html", user=user, modules=modules)

@bp.route("/tasks/add/<int:module_id>", methods=['GET','POST'])
@login_required
def addTask(module_id):
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
        db.session.add(new_task)
        db.session.commit()

        # If add event marked
        # create an event using the modules colour code
        # https://getbootstrap.com/docs/5.3/forms/form-control/

        if request.form.get('addToCalendarCheck'): # If link to calendar checked on form
            event = Event(user=current_user.get_id(), module=module.id, task=new_task.id, name=name, description=description, due_date=due_date)
            db.session.add(event)
            db.session.commit() # Have to add and commit the new event before being able to use it to update the task
            new_task.event = event.id # update the new task to now inlucde the event id
            db.session.commit()
        return redirect(url_for('core.tasksPage'))
    
    return render_template("core/addTask.html", module_id=module_id, module=module)

@bp.route("/tasks/delete/<string:author>/<int:id>", methods=['GET'])
@login_required
def deleteTask(author, id):
    if author == current_user.get_id():
        task = Task.query.filter_by(id=id).first()

        db.session.delete(task)
        db.session.commit()

    return redirect(url_for('core.tasksPage'))

@bp.route("/tasks/edit/<string:author>/<int:id>", methods=['GET','POST'])
@login_required
def editTask(author, id):
    if author != current_user.get_id():
        return redirect(url_for('core.tasksPage'))
    elif request.method == 'POST':
        task = Task.query.filter_by(id=id).first()
        module = Module.query.filter_by(id=task.id).first()
        selectedModule = request.form.get('selectedModule')
        name = request.form.get('taskName')
        description = request.form.get('taskDescription')
        date = request.form.get('taskDueDate').split('-')
        time = request.form.get('taskDueTime').split(':')
        dateAndTime = date + time
        dateAndTime = [int(x) for x in dateAndTime] # changes the list to int not str (comprehension)
        due_date = datetime.datetime(*dateAndTime)
        # print(selectedModule)
        db.session.query(Task).filter_by(id=id).update(dict(name=name, description=description, due_date=due_date, user=current_user.id, module=selectedModule))
        db.session.commit()
        # If the task has an event id stored then update the event as well
        if task.event: # If it is not null
            #update event and commit event to database
            print("Works")
            db.session.query(Event).filter_by(id=task.event).update(dict(name=name, description=description, due_date=due_date, module=selectedModule))
            db.session.commit()

        return redirect(url_for('core.tasksPage'))
    else:
        task = Task.query.filter_by(id=id).first()
        module = Module.query.filter_by(id=task.id).first()
        date = str(task.due_date)
        date = date.split(" ")
        due_date = date[0]
        due_time = date[1]
        due_time = due_time[:-3]
        return render_template("core/editTask.html", task=task, module=module, due_date=due_date, due_time=due_time)

@bp.route("/events/calendar/")
@login_required
def calendarPage():
    userid = current_user.id
    # user = db.get_or_404(User, id)
    today = date.today() # Gets today date
    year = today.year # Gets todays year
    month = today.month #gets todays month
    month_name = calendar.month_name[month]
    day_date = today.day # Gets todays day
    todaysEvents = Event.query.filter_by(user=userid).filter(Event.due_date.between(datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0), datetime.datetime(today.year, today.month, today.day, 23, 59, 59, 999999))).all()

    month_days = generate_calendar(year, month, current_user.id)
    return render_template("core/calendar.html", month=month_days, day_date=day_date, current_month=month, month_name=month_name, todaysEvents=todaysEvents)

# @bp.route("/events/calendar/<int:year>/<int:month>")
# @login_required
# def customCalendarPage(year, month):
#     # If year given = 0 it means current year
#         # if month = 0 it means current month and therefore switch to this month's calendar
#         # elif month > 0 means forward to month N
#         # elif month > 0 means backwards to month N
#     # elif year given > 0 means forward to year N with month = current month
#     # elif year given < 0 means backward to year N with month = current month
#     return render_template("core/index.html", user=current_user.id)

@bp.route("/Events/add", methods=['GET', 'POST'])
@login_required
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


@bp.route("/Events/edit/<int:author>/<int:event_id>", methods=['GET', 'POST'])
@login_required
def editEvent(author, event_id):
    if author != current_user.id:
        return redirect(url_for('core.calendarPage'))
    # task = Task.query.filter_by(event=event.id).first()
    elif request.method == 'POST':
        module = request.form.get('module')
        task = request.form.get('task')
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date').split('-')
        time = request.form.get('time').split(':')
        
        dateAndTime = date + time
        dateAndTime = [int(x) for x in dateAndTime] # changes the list to int not str (comprehension)
        due_date = datetime.datetime(*dateAndTime)

        db.session.query(Event).filter_by(id=event_id).update(dict(module=module, task=task, name=name, description=description, due_date=due_date))
        db.session.commit()
        return redirect(url_for('core.calendarPage'))
    
    event = Event.query.filter_by(id=event_id).first()
    date = str(event.due_date)
    date = date.split(" ")
    due_date = date[0]
    due_time = date[1]
    due_time = due_time[:-3]
    return render_template("core/editEvent.html", event=event, due_date=due_date, due_time=due_time)

@bp.app_template_filter('date_filter') # filters out the date
def date_filter(date):
    date = str(date)
    return date[10:16]

@bp.app_template_filter('time_filter') # filters out the time
def time_filter(date):
    date = str(date)
    date = date[8:10] + "/" + date[5:7] + "/" + date[0:4]
    return date[:10]

def generate_calendar(year, month, userid): #Generates lists required for calendar html template
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
    
    cal = calendar.Calendar(firstweekday=0) # Creates a calendar with the first week day being monday
    month_days = []
    week_days = []
    num = 0
    for day in cal.itermonthdates(year, month): #Generates list of weeks which are lists of days
        num += 1
        list_of_events = Event.query.filter_by(user=userid).filter(Event.due_date.between(datetime.datetime(day.year, day.month, day.day, 0, 0, 0, 0), datetime.datetime(day.year, day.month, day.day, 23, 59, 59, 999999))).all()
        events = []
        if list_of_events:
            for event in list_of_events:
                module = Module.query.filter_by(id=event.module).first()
                brightness = brightness_calculator(module.colour)
                events.append([event, module.colour, brightness])
                       
        dayList = [day.day, day.month, events]
        week_days.append(dayList)
        if num % 7 == 0:
            month_days.append(week_days)
            week_days = []

    return month_days

def brightness_calculator(colour):
    # Working out whether to use black or white font based on background colour
    # Algorithm credit https://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
    # Converted to python and into specific usecase by me Charles Laverick
    rgb = [int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:], 16)]
    # print(f"Hex: {colour}\nRGB: {rgb}\n") #for debugging can remove
    brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])/255
    #A brightness value > 0.5 means a bright colour and therefore use a dark font 
    #A brightness value < 0.5 means a darker colour and therefore use a light font 
    return brightness