from . import db
import datetime as datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True) #nullable means cannot be empty
    password = db.Column(db.String(80), nullable=False)
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))
    modules = db.relationship('Module', backref='module_owner') # Creates a relationship between User and Module
    tasks = db.relationship('Task', backref='task_owner', primaryjoin="User.id==Task.user") # Creates a relationship between User and Task
    events = db.relationship('Event', backref='event_owner', primaryjoin="User.id==Event.user") # Creates a relationship between User and Task


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))
    name = db.Column(db.String(100), nullable=False)
    colour = db.Column(db.String(7), nullable=False)
    tasks = db.relationship('Task', backref='module_tasks', primaryjoin="Module.id==Task.module", cascade="all, delete, delete-orphan")
    events = db.relationship('Event', backref='module_events', primaryjoin="Module.id==Event.module", cascade="all, delete, delete-orphan")
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    module = db.Column(db.Integer, db.ForeignKey('module.id', ondelete="CASCADE"))
    event = db.Column(db.Integer, db.ForeignKey('event.id', ondelete="CASCADE"))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))
    due_date = db.Column(db.DateTime, nullable=False)

    # user_task = db.relationship('User', backref='user_task')
    # module_task = db.relationship('Modules', backref='module_task')
    # event_task = db.relationship('Events', backref='event_task')

    events = db.relationship('Event', backref='events', primaryjoin="Task.id==Event.task", post_update=True,  cascade='save-update, merge, delete, delete-orphan')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    module = db.Column(db.Integer, db.ForeignKey('module.id', ondelete="CASCADE"))
    task = db.Column(db.Integer, db.ForeignKey('task.id', ondelete="CASCADE"))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    creation_date = db.Column(db.DateTime, default= datetime.datetime.now(datetime.UTC))
    due_date = db.Column(db.DateTime, nullable=False)

    # user_event = db.relationship('User', backref='user_event')
    # module_event = db.relationship('Modules', backref='module_event')
    # task_event = db.relationship('Tasks', backref='task_event')

    tasks = db.relationship('Task', backref='task', primaryjoin="Event.id==Task.event", post_update=True,  cascade='save-update, merge, delete, delete-orphan')


# For relationships the first parameter is the child class name and the backref is the new column that will be created for the relationship