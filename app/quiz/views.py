# app/auth/views.py
import socketio
from werkzeug.utils import secure_filename
from flask import redirect, render_template, url_for, request, session
from flask_login import login_required, current_user

from . import quiz
from .forms import AddQuestionForm, ViewQuestion, MultipleChoice, StartQuiz, adminStartQuiz
import os
import os.path
from ..models import User, get_first_question_id, load_all_present_users, load_all_ready_users, login_required, is_quiz_admin, insert_question, load_questions, load_choices, change_user_conn_status, load_present_user, update_user_conn_status, quizadminhash, update_user_game_status
import json
from app import wss, app

app.config["IMAGE_UPLOADS"] = "app/static/img/uploads"

@wss.on('connect', namespace='/Play')
def play():
    print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOFMYNIG")
    user = current_user.username
    wss.emit('new_response', {'data': user}, namespace='/Play', broadcast=True)

@wss.on('disconnect', namespace='/Play')
def test():
    print("NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
    user = current_user.username
    wss.emit('new_response', {'data': user}, namespace='/Play', broadcast=True)

@wss.on('connect')
def connect():
    print("_________________")
    print(current_user.username)
    print("_________________")
    user = current_user.username
    is_present = load_present_user(user)

    #check if admin via admin/quizadmin hash
    if is_present == 1:
         wss.emit('my_response', {'data': user}, broadcast=True)
    else:
        change_user_conn_status(user, 1)
        wss.emit('my_response', {'data': user}, broadcast=True)

@wss.on('disconnect')
def disconnect():
    print("_________________")
    change_user_conn_status(current_user.username, 0)
    print("User NO LONGER WEARING SOCKS!")
    print("_________________")
    wss.emit('my_response',{'data': 'cock!'}, broadcast=True)

@wss.on('user')
def load_users():
    present_users = load_all_present_users()
    ready_users = load_all_ready_users()

    data = {
        'present' : present_users,
        'ready' : ready_users
    }
    print(data)
    wss.emit('my_pong', {'data': data}, broadcast=True)

@wss.on('submit')
def submit(data):
    print(data)
    user = current_user.username 
    update_user_conn_status(user, 1)

@wss.on('unsubmit')
def unsubmit(data):
    print(data)
    user = current_user.username
    update_user_conn_status(user,0)

@quiz.route('/quiz', methods=['GET','POST'])
@login_required
def view_quiz():

    user = User.query.filter_by(username=current_user.username).first()
    form = StartQuiz()

    if user.is_quiz_admin:
        form = adminStartQuiz()

    if form.validate_on_submit():
        update_user_game_status()
        return redirect(url_for('quiz.question'))
    return render_template('question/view_quiz.html', form=form, title='Start Quiz', async_mode=wss.async_mode)
    

@quiz.route('/quiz/play', methods=['GET','POST'])
@login_required
def question():
    """
    use websockets to load question on the same page
    timer runs out (example) and the server sends the question data back
    """
    qid = get_first_question_id()
    question = load_questions(int(qid))    

    while True:
        try:
            if question[6] == 2:
                form = MultipleChoice()
                choices = str(question[7]).split(', ')
                form.Answers.choices = choices
            elif question[6] == 1:
                form = ViewQuestion()
            break
        except ValueError:
            return 'Bad request!', 400
        
    # load registration template

    if form.validate_on_submit(): 
        data = form.round_choice.data,

    return render_template('question/play.html', form=form, records=question, qid=qid, title='Question: {}'.format(qid))

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
