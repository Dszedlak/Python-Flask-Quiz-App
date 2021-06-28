# app/auth/views.py
from werkzeug.utils import secure_filename
from flask import flash, redirect, render_template, url_for, request

from flask_login import login_required, login_manager, current_user
from . import quiz
import requests
from .forms import AddQuestionForm, BrowseStoreForm
import os
import os.path

from ..models import engine
from .forms import app
from ..models import session, login_required, is_quiz_admin, add_questions, load_questions
import json

app.config["IMAGE_UPLOADS"] = "app/static/img/uploads"

@quiz.route('/quiz', methods=['GET'])
@login_required
def view_quiz():
    
    """
    Handle requests to the /browse route
    Add a user to the database through the registration form
    """
    records = load_questions()        
    
    # load registration template
    return render_template('question/view_quiz.html', records=records, title='Start Quiz')

@quiz.route('/quiz/add', methods=['GET', 'POST'])
@is_quiz_admin
def add_question():
    
    form = AddQuestionForm()
    if form.validate_on_submit(): 
            data = {
                    "round": form.round.data,
                    "question": form.question.data,
                    "additional_info": form.additional_info.data,
                    "points_worth":form.points_worth.data,
                    "correct_answer":form.correct_answer.data
        }
            json_data = json.dumps(data)
            filename = request.files['file']
            path = 'app/static/img/uploads/%s' % (filename.filename)

            if not os.path.exists(path):
                filename.save(os.path.join(app.config["IMAGE_UPLOADS"],secure_filename(filename.filename)))
                add_questions(json_data,secure_filename(filename.filename))
            else:
                filename.filename = resolve_conflict(filename.filename)
                filename.save(os.path.join(app.config["IMAGE_UPLOADS"], secure_filename(filename.filename)))
                add_questions(json_data, secure_filename(filename.filename))
       
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
