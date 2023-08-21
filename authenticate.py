from flask import Blueprint
from __init__ import db
from flask import Blueprint, render_template, redirect, url_for,request,flash
from models import User
from flask_login import login_user,login_required, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(user_name=username).first()

        if not user or not user.password==password:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        return redirect(url_for('main.index'))

@auth.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html')
    if request.method=='POST':
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(user_name=username).first()

        if user:
            flash('Username already exists') 
            return redirect(url_for('auth.signup'))
        
        new_user = User(user_name=username, name=name, password=password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))