from unicodedata import name
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from __init__ import create_app
from flask_sqlalchemy import SQLAlchemy
from models import *
import matplotlib.pyplot as plt
from datetime import date

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/profile')
@login_required
def profile():
    trackers=Tracker.query.filter(Tracker.user_name==current_user.user_name).all()
    totalTrack=len(trackers)
    track=Tracker.query.with_entities(Tracker.tracker_id).filter(Tracker.user_name==current_user.user_name).all()
    print(track)
    lg=[]
    for trk in track:
        logg=Log_table.query.with_entities(Log_table.edited_date).filter(Log_table.tracker_id==trk[0]).all()
        for l in logg:
            lg.append(l[0])
        
    lg.sort(reverse=True)
    s=""
    if lg!=[]:
        s=lg[0]
    return render_template('dashboard.html' ,name=current_user.name,trackers=trackers,totalTrack=totalTrack,lg=s)

@main.route('/addTracker',methods=['GET','POST'])
@login_required
def addTracker():
    if request.method=="GET":
        return render_template('addtracker.html' ,name=current_user.name)
    if request.method=="POST":
        tr_name =request.form.get('tname')
        tr_type = request.form.get('choices')
        tr_desc = request.form.get('desc')
        tr_sets = request.form.get('sets')
        flag=Tracker.query.filter(Tracker.tracker_name==tr_name.strip() and Tracker.user_name==current_user.user_name).first()
        print("------"+tr_name)
        if flag is not None:
            flash("The Tracker already exist try a different tracker")
            return redirect(url_for("main.addTracker"))
        else:
            new_tr=Tracker(tracker_name=tr_name,user_name=current_user.user_name,tracker_type=tr_type,description=tr_desc,options=tr_sets)
            db.session.add(new_tr)
            db.session.commit()
            flash("The "+tr_name+" Tracker added Succesfully")
            return redirect(url_for("main.profile"))

@main.route('/deleteTracker/<track_id>')
@login_required
def deleteTracker(track_id):
    tracker=Tracker.query.get(track_id)
    track_name=tracker.tracker_name
    db.session.delete(tracker)
    db.session.commit()
    flash(track_name+" Tracker removed Successfully")
    return redirect('/profile')

@main.route('/editTracker/<track_id>',methods=['GET','POST'])
@login_required
def editTracker(track_id):
    if request.method=='GET':
        tracker=Tracker.query.filter(Tracker.tracker_id==track_id).first()
        return render_template('edittracker.html',tracker=tracker,name=current_user.name)
    if request.method=="POST":
        tr_name = request.form.get('tname')
        tr_type = request.form.get('choices')
        tr_desc = request.form.get('desc')
        tr_sets = request.form.get('sets')
        etracker=Tracker.query.get(track_id)
        flag=Tracker.query.filter(Tracker.tracker_name==tr_name.strip() and Tracker.user_name==current_user.user_name).first()
        if flag is not None:
            if etracker.tracker_name!=tr_name:
                flash("The Tracker name already exist try a different Name")
                return redirect('/editTracker/'+track_id)
            else:
                etracker.tracker_name=tr_name
                etracker.tracker_type=tr_type
                etracker.description=tr_desc
                etracker.options=tr_sets
                db.session.commit()
                flash("The "+tr_name+" Tracker edited Succesfully")
                return redirect(url_for("main.profile"))
        else:
            etracker.tracker_name=tr_name
            etracker.tracker_type=tr_type
            etracker.description=tr_desc
            etracker.options=tr_sets
            db.session.commit()
            flash("The "+tr_name+" Tracker edited Succesfully")
            return redirect(url_for("main.profile"))

@main.route('/TrackerInfo/<track_id>',methods=['GET','POST']) 
@login_required
def TrackerInfo(track_id):
    if request.method=='GET':
        logs_val=Log_table.query.with_entities(Log_table.value,Log_table.time).filter(Log_table.tracker_id==track_id).all()
        track_t=Tracker.query.with_entities(Tracker.tracker_type).filter(Tracker.tracker_id==track_id).first()
        valuesl=[]
        timel=[]
        for l in logs_val:
            if track_t[0]=='Integer':
                valuesl.append(int(l[0]))
            else:
                valuesl.append(l[0])
            timel.append(l[1])
        plt.gcf().autofmt_xdate()
        fig, ax = plt.subplots(figsize=(8, 5))
        plt.xlabel('Date and Time')
        plt.ylabel('Values')
        ax.plot(timel,valuesl)
        plt.savefig("static/hist.png")

        cur_tracker=Tracker.query.filter(Tracker.tracker_id==track_id).first()
        cur_logs=Log_table.query.filter(Log_table.tracker_id==track_id).all()
        return render_template('TrackerInfo.html',name=current_user.name,cur_tracker=cur_tracker,cur_logs=cur_logs) 

@main.route('/<track_id>/addLog',methods=['GET','POST'])
@login_required
def addLog(track_id):
    if request.method=='GET':
        option_list=[]
        tracker_on=Tracker.query.get(track_id)
        if tracker_on.tracker_type=='Multiple Choice':
            str1=tracker_on.options
            option_list=str1.split(',')
            print(option_list)
        cur_tracker=Tracker.query.filter(Tracker.tracker_id==track_id).first()
        return render_template('addLog.html',name=current_user.name,cur_tracker=cur_tracker,option_list=option_list)
    if request.method=='POST':
        f_time=request.form.get('date')
        f_value=request.form.get('val')
        f_notes=request.form.get('notes')
        cur_date= date.today()
        new_log=Log_table(time=f_time,value=f_value,note=f_notes,tracker_id=track_id,user_name=current_user.user_name,edited_date=cur_date)
        db.session.add(new_log)
        db.session.commit()
        flash("Log added Successfully")
        return redirect("/"+track_id+"/addLog")

@main.route('/deleteLog/<l_id>',methods=['GET','POST'])
@login_required
def deleteLog(l_id):
    dlog=Log_table.query.get(l_id)
    t_id=dlog.tracker_id
    db.session.delete(dlog)
    db.session.commit()
    flash('Log Removed Successfully.')
    return redirect(url_for('main.TrackerInfo',track_id=t_id))

@main.route('/editLog/<l_id>',methods=['GET','POST'])
@login_required
def editLog(l_id):
    if request.method=='GET':
        elog=Log_table.query.get(l_id)
        option_list=[]
        tracker_on=Tracker.query.get(elog.tracker_id)
        if tracker_on.tracker_type=='Multiple Choice':
            str1=tracker_on.options
            option_list=str1.split(',')
            print(option_list)
        cur_tracker=Tracker.query.filter(Tracker.tracker_id==elog.tracker_id).first()
        return render_template('editLog.html',name=current_user.name,cur_tracker=cur_tracker,option_list=option_list,etime=elog.time,eval=elog.value,enote=elog.note)
    if request.method=='POST':
        elog=Log_table.query.get(l_id)
        t_id=elog.tracker_id
        elog.value=request.form.get('val')
        elog.note=request.form.get('notes')
        elog.time=request.form.get('date')
        cur_date= date.today()
        elog.edited_date=cur_date
        db.session.commit()
        flash('Log Edited Successfully.')
        return redirect(url_for('main.TrackerInfo',track_id=t_id))    

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
