# app/auth/views.py
from inspect import classify_class_attrs
from flask_socketio import join_room, leave_room
from werkzeug.utils import secure_filename
from flask import redirect, render_template, url_for, request, session
from flask_login import login_required, current_user

from . import quiz
from .forms import AddQuestionForm, StartQuiz, adminStartQuiz
import os
import os.path
from ..models import User, get_first_question_id, load_all_present_users, load_all_ready_users, login_required, is_quiz_admin, insert_question, load_questions, load_choices, change_user_conn_status, load_present_user, update_user_conn_status, quizadminhash, update_user_game_status
import json
from app import wss, app

app.config["IMAGE_UPLOADS"] = "app/static/img/uploads"
clients = []

@wss.on('connect', namespace='/Play')
def oog():
    user = current_user.username
    wss.emit('new_response', {'data': user}, namespace='/Play', broadcast=True)

@wss.on('disconnect', namespace='/Play')
def test():
    user = current_user.username
    wss.emit('new_response', {'data': user}, namespace='/Play', broadcast=True)

@wss.on('quiz_redirect')
def start(data):
    print ('USER MESSAGE {}'.format(data))
    wss.emit('redirect', {'url': url_for('quiz.play')}, room=clients)

@wss.on('change_game_state')
def game_start():
    update_user_game_status(1)

@wss.on('connect')
def connect():
    user = current_user.username
    is_present = load_present_user(user)
    isadminuser = User.query.filter_by(username=current_user.username).first()

    print("VERY LARGE COCK MY BROTHER!")

    if isadminuser.is_quiz_admin:
        clients.append(request.sid) 

    #check if admin via is admin
    if is_present == 1:
        data = load_users()
        wss.emit('user_status', {'data': data}, broadcast=True)
    else:
        change_user_conn_status(user, 1)
        data = load_users()
        wss.emit('user_status', {'data': data}, broadcast=True)

@wss.on('disconnect')
def disconnect():
    print("_________________")
    user = current_user.username
    change_user_conn_status(current_user.username, 0)
    print("User NO LONGER WEARING SOCKS!")
    print("_________________")
    update_user_conn_status(user,0)

    data = load_users()
    wss.emit('user_status',{'data': data}, broadcast=True)

@wss.on('ready_user')
def submit(data):
    print(data)
    print("READY")
    user = current_user.username 
    update_user_conn_status(user, 1)
    
    clients.append(request.sid)
    data = load_users()
    
    wss.emit('user_status', {'data': data}, broadcast=True)

@wss.on('unready_user')
def unsubmit(data):
    print(data)
    print("UNREADY")
    
    user = current_user.username 
    update_user_conn_status(user, 0)
    data = load_users()
    clients.remove(request.sid)

    wss.emit('user_status', {'data': data}, broadcast=True)

    #All users are in 1 room, have 2 rooms. When someone readys up, they join the ready room
    #But do not leave the waiting room. Broadcast all changes that happen to users of the waiting room, as everyone is in that room anyway

@wss.on('load_question_data', namespace='/Play')
def testytest(question_num):
    question = load_questions(int(question_num["data"]))
    #recieve question num from client - starting num is 1.
    question_data = {
        'round' : question[0],
        'question' : question[1],
        'additional_info':question[2],
        'file':question[3],
        'points_worth':question[4],
        'question_type':question[6],
        'question_options':question[7],
    }
    #send question data as json object
    wss.emit('question', {'data': question_data}, namespace='/Play', broadcast=True)
    
def load_users():
    present_users = load_all_present_users()
    ready_users = load_all_ready_users()

    data = {
        'present' : present_users,
        'ready' : ready_users
    }
    return data
 
@quiz.route('/quiz', methods=['GET','POST'])
@login_required
def view_quiz():

    user = User.query.filter_by(username=current_user.username).first()
    form = StartQuiz()

    if user.is_quiz_admin:
        form = adminStartQuiz()

    if form.validate_on_submit():
        update_user_game_status(1)
    return render_template('question/view_quiz.html', form=form, title='Start Quiz', async_mode=wss.async_mode)  

@quiz.route('/quiz/play', methods=['GET','POST'])
@login_required
def play():
    """
    use websockets to load question on the same page
    timer runs out (example) and the server sends the question data back
    """
    load_questions(1)
    # load registration template

    return render_template('question/play.html',title='Question: Playing...')

@quiz.route('/quiz/add', methods=['GET', 'POST'])
@is_quiz_admin
def add_question():

    form = AddQuestionForm()
    list = load_choices()
    list.append(('None','None'))
    form.round_choice.choices = list
    
    if form.validate_on_submit(): 
        data = {
                "round": form.round_choice.data,
                "question": form.question.data,
                "additional_info": form.additional_info.data,
                "points_worth":form.points_worth.data,
                "correct_answer":form.correct_answer.data,
                "question_type":form.question_type.data,
                "question_options":"N/A"
        }
        if form.round.data:
            data['round'] = form.round.data

        if form.add_choice_1.data:
            data['question_options']= (form.add_choice_1.data+", "+form.add_choice_2.data+", "+form.add_choice_3.data+", "+form.add_choice_4.data+", "+form.add_choice_5.data)
        
        print("__________________________")
        print(data['question_options'])
        json_data = json.dumps(data)
        print("__________________________")
        
        print(json_data)
        filename = request.files['file']
        path = 'app/static/img/uploads/%s' % (filename.filename)

        if not os.path.exists(path):
            with app.app_context():
                filename.save(os.path.join(app.config["IMAGE_UPLOADS"],secure_filename(filename.filename)))
                insert_question(json_data,secure_filename(filename.filename))
        else:
            with app.app_context():
                filename.filename = resolve_conflict(filename.filename)
                filename.save(os.path.join(app.config["IMAGE_UPLOADS"], secure_filename(filename.filename)))
                insert_question(json_data, secure_filename(filename.filename))
    
        return redirect(url_for('quiz.add_question'))
            
    # load registration template
    return render_template('question/add.html', form=form, title='Add')

def resolve_conflict(basename):
    name, ext = os.path.splitext(basename)
    count = 0
    while True:
        count = count + 1
        newname = '%s_%d%s' % (name, count, ext)
        path = 'app/static/img/uploads/%s' % (newname)
        if not os.path.exists(path):
                return newname
