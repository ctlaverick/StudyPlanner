import datetime as datetime
from . import db

class User(db.Model): #Usermixin
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True) #nullable means cannot be empty
    password = db.Column(db.String(80), nullable=False)
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))

class Modules(db.Model):
    module_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))
    module_name = db.Column(db.String(100), nullable=False)
    # Creates the relationship between the Users table and this one using the name module_owner to use it e.g. module_owner.module_id
    modules = db.relationship('User', backref='module_owner')
    
class Tasks(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))
    due_date = db.Column(db.DateTime, nullable=False)

    user_task = db.relationship('User', backref='user_task')
    module_task = db.relationship('Modules', backref='module_task')
    event_task = db.relationship('Events', backref='event_task')

class Events(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))
    due_date = db.Column(db.DateTime, nullable=False)

    user_event = db.relationship('User', backref='user_event')
    module_event = db.relationship('Modules', backref='module_event')
    task_event = db.relationship('Tasks', backref='task_event')