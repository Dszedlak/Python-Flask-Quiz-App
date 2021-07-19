# app/auth/views.py
from sqlalchemy.sql.base import Executable
from threading import Lock
from werkzeug.utils import secure_filename
from flask import flash, redirect, render_template, url_for, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_login import login_required, login_manager, current_user
from . import quiz
import requests
from .forms import AddQuestionForm, ViewQuestion, MultipleChoice, StartQuiz
import os
import os.path

from .forms import app, socketio, async_mode
from ..models import session, login_required, is_quiz_admin, insert_question, load_questions, load_choices, insert_game_user, load_game_users
import json

app.config["IMAGE_UPLOADS"] = "app/static/img/uploads"

thread = None
thread_lock = Lock()

@socketio.on('quiz')
def connect(data):
    emit('my_response', {'message': data})

@socketio.event
def user(data):
    emit('my_response', {'message': data})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    
@quiz.route('/quiz', methods=['GET','POST'])
@login_required
def view_quiz():
    form = StartQuiz()
    return render_template('question/view_quiz.html', form=form, title='Start Quiz', async_mode=socketio.async_mode)

@quiz.route('/quiz/question_<int:qid>', methods=['GET','POST'])
@login_required
def question(qid):
    """
    Handle requests to the /view question page
    """
    question = load_questions(qid)    
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

    return render_template('question/view_question.html', form=form, records=question, qid=qid, title='Question: {}'.format(qid))

@quiz.route('/quiz/add', methods=['GET', 'POST'])
@is_quiz_admin
def add_question():

    form = AddQuestionForm()
    form.round_choice.choices = load_choices()
    
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
            filename.save(os.path.join(app.config["IMAGE_UPLOADS"],secure_filename(filename.filename)))
            insert_question(json_data,secure_filename(filename.filename))
        else:
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
