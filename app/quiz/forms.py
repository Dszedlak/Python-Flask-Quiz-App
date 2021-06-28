# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, EqualTo
from flask import Flask, jsonify, render_template, request, g
import json

app = Flask(__name__)
from ..models import Question

class BrowseStoreForm(FlaskForm):
    """
    Form for users to browse the record store
    """    
class AddQuestionForm(FlaskForm):

    round = StringField('Round', validators=[DataRequired()])
    question = StringField('Question', validators=[DataRequired()])
    additional_info = StringField('Additional info')
    points_worth = StringField('Points Worth', validators=[DataRequired()])
    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    file = FileField(validators=[FileRequired()])

    submit = SubmitField('Add Question')
