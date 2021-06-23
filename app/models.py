import sqlite3, os, hashlib
from flask import Flask, jsonify, render_template, request, g, flash, session, redirect, url_for

from functools import wraps
from app import engine 
import json

adminHash = "1c0f000b72e6ce080d17c333068d3678"

class User():
    tablename = "users"
    #create database if it doesn't exist yet
    if not os.path.exists('sqlite:///database.db'):
        if not engine.dialect.has_table(engine, tablename):
            with engine.connect() as connection:
                c = connection.execute("""CREATE TABLE users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, username TEXT, first_name TEXT, last_name TEXT, password_hash TEXT, is_admin INTEGER )""")

class Store():
    tablename = "music"
    if not os.path.exists('sqlite:///database.db'):
        if not engine.dialect.has_table(engine, tablename):
            with engine.connect() as connection:
                c = connection.execute("""CREATE TABLE music(item_id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT, album_name TEXT, album_cover TEXT, label TEXT, format TEXT, country TEXT, year_released TEXT, genre TEXT, style TEXT, user_id_ref INTEGER)""")

        

def add_music(record_json, img_ref, user_id):

    record = json.loads(record_json) 
    with engine.connect() as connection:
        c = connection.execute("""INSERT INTO music(artist, album_name, album_cover, label, format, country, year_released, genre, style, user_id_ref) VALUES(?,?,?,?,?,?,?,?,?,?)""", record["artist"], record["album_name"], img_ref, record["label"], record["format"], record["country"], record["year_released"], record["genre"], record["style"], user_id)
        

def load_music():
    with engine.connect() as connection:
        c = connection.execute("""SELECT * FROM music""")
        music = [{'records':[dict(artist=row[1], album_name=row[2], album_cover=row[3],label=row[4], format=row[5], country=row[6], year_released=row[7], genre=row[8], style=row[9], user_id_ref=row[10]) for row in c.fetchall()]}]
        #print(music)
        
        return music

def search_music(term):
    with engine.connect() as connection:
        c = connection.execute("""DROP TABLE v_music""")
        c  = connection.execute("""CREATE VIRTUAL TABLE v_music USING FTS3(item_id, artist, album_name, album_cover, label, format, country, year_released, genre, style, user_id_ref)""")
        c = connection.execute("""INSERT INTO v_music SELECT * FROM music""")
        d = connection.execute(""" SELECT * FROM v_music WHERE v_music MATCH '%s' """%term)
        a = connection.execute(""" SELECT * FROM v_music""")

        music = [{'records':[dict(artist=row[1], album_name=row[2], album_cover=row[3],label=row[4], format=row[5], country=row[6], year_released=row[7], genre=row[8], style=row[9], user_id_ref=row[10]) for row in d.fetchall()]}]

        return music
  
def add_user(users_json):

    user = json.loads(users_json)

    with engine.connect() as connection:
        c = connection.execute("""INSERT INTO users(username, password_hash, is_admin) VALUES(?,?,?)""", user["username"], user["password_hash"], "0")

def login_user(user_json):
    user = json.loads(user_json)
    with engine.connect() as connection:
            c = connection.execute("""SELECT * FROM users WHERE username = '%s' AND password_hash = '%s'"""%(user['username'], user['password_hash']))
            user_row = c.fetchone()
            if user_row:
                flash('You are logged in!')
                session['logged_in']=True
                session['username']=user_row[1]
                session['user_id']=user_row[0]

                print(user_row[1])
                if user_row[3] == 1: 
                    session['is_admin']=adminHash
                else:
                    session['is_admin']="You Are Not The Admin Fam."

                return True

                #print(session)
            else: 
                flash('Invalid email or password.','success')
                return False
          
# Create password hashes
def hash_pass(passw):
	m = hashlib.md5()
	m.update(passw.encode('utf-8'))
	return m.hexdigest()

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
   
def clear_session():
    session.clear()
    flash('you are now logged out','success')