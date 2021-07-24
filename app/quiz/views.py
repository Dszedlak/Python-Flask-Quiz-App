# app/auth/views.py
from werkzeug.utils import secure_filename
from flask import redirect, render_template, url_for, request
from flask_login import login_required, current_user

from . import quiz
from .forms import AddQuestionForm, ViewQuestion, MultipleChoice, StartQuiz
import os
import os.path

from ..models import login_required, is_quiz_admin, insert_question, load_questions, load_choices, insert_game_user, load_game_users
import json
from app import wss, app

@wss.on('resp')
def response(data):
    data = load_game_users(str(current_user))
    if data == 1:
         wss.emit('my_response', {'data': data}, broadcast=True)
    else:
        insert_game_user(str(current_user), 1)
        data = load_game_users(str(current_user))
        wss.emit('my_response', {'data': data}, broadcast=True)

@wss.on('resp_disc')
def disconn(data):
    insert_game_user(str(current_user), 0)
    data = "User is not present."
    print("_________________")
    print("YEB MY WEB!")
    print(data)
    print("_________________")
    wss.emit('my_response',{'data': data}, broadcast=True)

@wss.on('user')
def user_response(data):
    
    wss.emit('my_response', {'data': data}, broadcast=True)

@quiz.route('/quiz', methods=['GET','POST'])
@login_required
def view_quiz():
    form = StartQuiz()
    return render_template('question/view_quiz.html', form=form, title='Start Quiz', async_mode=wss.async_mode)

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
