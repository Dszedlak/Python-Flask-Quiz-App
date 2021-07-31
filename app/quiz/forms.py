# app/auth/forms.py

from flask_wtf import FlaskForm
from flask_wtf.recaptcha import widgets
from wtforms import StringField, SubmitField, ValidationError, BooleanField
from wtforms.fields.simple import HiddenField
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileRequired
from wtforms.fields.core import RadioField, SelectField
from wtforms.validators import DataRequired, EqualTo
from flask import Flask, jsonify, render_template, request, g
from wtforms.widgets.core import HiddenInput
from flask_socketio import SocketIO
import json

class ViewQuestion(FlaskForm):
    """
    Form for users to answer input field questions
    """
    Answers = StringField('Your Answer', validators=[DataRequired()])
    submit = SubmitField('Submit Answer')

class MultipleChoice(FlaskForm):
    """
    Form for users to answer multiple choice questions
    """
    Answers = RadioField('Select question type',choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit Answer')
    
class StartQuiz(FlaskForm):
    """
    Form for users to view the quiz
    """
    ready = SubmitField('Ready')
    unready = SubmitField('Unready')

class adminStartQuiz(FlaskForm):
    start = SubmitField('Start Quiz')

class AddQuestionForm(FlaskForm):

    round = StringField('Create New Round', render_kw={"placeholder":"Leave empty to select existing round."})
    round_choice = SelectField('Select Round',choices=[])
    question_type = SelectField('Select question type',choices=[('1', 'User Input Based'),('2','Multiple Choice')], render_kw={"onchange":"show()"})
    question = StringField('Question', validators=[DataRequired()])
    additional_info = StringField('Additional info')
    points_worth = StringField('Points Worth', validators=[DataRequired()])
    correct_answer = StringField('Correct Answer (User Input)', validators=[DataRequired()])
    file = FileField('')
    
    add_choice_1 = StringField('Choice 1')
    add_choice_2 = StringField('Choice 2')
    add_choice_3 = StringField('Choice 3')
    add_choice_4 = StringField('Choice 4')
    add_choice_5 = StringField('Choice 5')
    
    submit = SubmitField('Add Question')
