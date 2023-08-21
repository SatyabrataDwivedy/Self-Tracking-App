from distutils.log import Log
from __init__ import db
from flask_login import UserMixin

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Tracker(db.Model):
     __tablename__ = 'tracker'
     tracker_id=db.Column(db.Integer,primary_key=True,)
     user_name=db.Column(db.String,db.ForeignKey("user.user_name"),nullable=False)
     tracker_name=db.Column(db.String,nullable=False)
     description=db.Column(db.String)
     tracker_type=db.Column(db.String,nullable=False)
     options=db.Column(db.String)
     relative=db.relationship("Log_table",cascade='all,delete',backref="tracker")

class Log_table(db.Model):
    __tablename__='log_table'
    log_id=db.Column(db.Integer,primary_key=True)
    tracker_id=db.Column(db.Integer,db.ForeignKey("tracker.tracker_id"),nullable=False,)
    time=db.Column(db.String,nullable=False,unique=True)
    value=db.Column(db.String,nullable=False)
    note=db.Column(db.String)
    user_name=db.Column(db.String,db.ForeignKey("user.user_name"),nullable=False)
    edited_date=db.Column(db.String)