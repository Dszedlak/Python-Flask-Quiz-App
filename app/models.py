from enum import auto
from re import S
import sqlite3, os, hashlib
from flask import Flask, jsonify, render_template, request, g, flash, session, redirect, url_for
from flask.globals import current_app
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from jinja2.utils import select_autoescape
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import create_engine

from app import db, login_manager
import json

engine = create_engine('sqlite:////Users/DAVID/Documents/GitHub/Quiz/app/database.db') 

adminHash = "1c0f000b72e6ce080d17c333068d3678"
quizadminhash = "4f511ca2fcb715e2dd48ba684812e8d4"

class User(UserMixin, db.Model):
    
    """
    Create an Users table
    """
    
    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_quiz_admin = db.Column(db.Integer)
    is_admin = db.Column(db.Integer)
    quizes_won = db.Column(db.Integer)
    quizes_hosted = db.Column(db.Integer)

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '{}'.format(self.username)

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Question(db.Model):
    __tablename__ = 'quiz'

    qid = db.Column(db.Integer, primary_key=True)
    round = db.Column(db.String(250))
    question = db.Column(db.String(250))
    additional_info = db.Column(db.String(250))
    file = db.Column(db.String(250))
    points_worth = db.Column(db.Integer())
    correct_answer = db.Column(db.String(250))
    question_type = db.Column(db.Integer())
    question_options = db.Column(db.String(1000))

    def __repr__(self):
        return '<qid {}>'.format(self.qid)   

class Answer(db.Model):
    __tablename__ = 'answer'
    answer_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer())
    user_id = db.Column(db.Integer())
    answer = db.Column(db.String(1000))

class Game(db.Model):
    __tablename__ = 'game'
    game_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(5000))
    game_state = db.Column(db.Integer())
    is_present = db.Column(db.Integer())
    is_ready = db.Column(db.Integer())

def load_game_users(data):
    user = db.session.query(Game.is_present).filter_by(username=data).first()
    for choice in user:
        all = choice
    print(all)
    return all

def insert_game_user(data, num):
    user = db.session.query(Game).filter_by(username=data).first()
    user.is_present = num
    db.session.commit()

def game_user_is_ready(data):
    game_lst = json.loads(data)
    user = db.session.query(Game).filter_by(username=game_lst['username']).first()
    user.is_ready= game_lst['is_ready']
    db.session.commit()

def insert_question(question_json, img_ref):
    question_lst = json.loads(question_json) 
    question = Question(round=question_lst["round"], question=question_lst['question'],additional_info=question_lst["additional_info"], file=img_ref, points_worth=question_lst["points_worth"], correct_answer=question_lst["correct_answer"], question_type=question_lst['question_type'], question_options=question_lst["question_options"])
    db.session.add(question)
    db.session.commit()

def load_choices():
    all=[]
    choices = db.session.query(Question.round).all()
    for choice in choices:
        all.append(choice+choice)

    
    remove_duplicates = list(dict.fromkeys(all))
    print(remove_duplicates)
    print(all)
    return remove_duplicates

def load_questions(question_num):
    question_query = db.session.query(Question.round, Question.question, Question.additional_info, Question.file, Question.points_worth, Question.correct_answer, Question.question_type, Question.question_options).filter_by(qid=question_num).first()
    print(question_query)
    return question_query


# def load_questions():
#     with engine.connect() as connection:
#         c = connection.execute("""SELECT * FROM quiz""")
#         questions = [{'questions':[dict(round=row[1], question=row[2], additional_info=row[3],file=row[4], points_worth=row[5], correct_answer=row[6]) for row in c.fetchall()]}]
#         print(questions)
        
#         return questions

def load_scores():
    with engine.connect() as connection:
        c = connection.execute("""SELECT * FROM users ORDER BY quizes_won DESC""")
        scores = [{'users':[dict(username=row[1], score=row[5]) for row in c.fetchall()]}]
        
    print('____________')
    print(scores)
    print('____________')
    return scores

# def search_questions(term):
#     with engine.connect() as connection:
#         c = connection.execute("""DROP TABLE v_quiz""")
#         c  = connection.execute("""CREATE VIRTUAL TABLE v_quiz USING FTS3(item_id, artist, album_name, album_cover, label, format, country, year_released, genre, style, user_id_ref)""")
#         c = connection.execute("""INSERT INTO v_quiz SELECT * FROM quiz""")
#         d = connection.execute(""" SELECT * FROM v_quiz WHERE v_quiz MATCH '%s' """%term)
#         a = connection.execute(""" SELECT * FROM v_quiz""")
#         music = [{'questions':[dict(artist=row[1], album_name=row[2], album_cover=row[3],label=row[4], format=row[5], country=row[6], year_released=row[7], genre=row[8], style=row[9], user_id_ref=row[10]) for row in d.fetchall()]}]
#         return music

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('auth.login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_admin' in session and session['is_admin']==adminHash:
            return f(*args, **kwargs)
        else:
            flash('Your are prohibited from viewing this page.')
            return redirect(url_for('home.dashboard'))
    return wrap    

def is_quiz_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_quiz_admin' in session and session['is_quiz_admin']==quizadminhash:
            return f(*args, **kwargs)
        else:
            flash('You are prohibited from viewing this page.')
            return redirect(url_for('home.dashboard'))
    return wrap

def clear_session():
    session.clear()
    flash('you are now logged out','success')