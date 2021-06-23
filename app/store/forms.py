# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, EqualTo
from flask import Flask, jsonify, render_template, request, g
import json

app = Flask(__name__)
from ..models import Store

class BrowseStoreForm(FlaskForm):
    """
    Form for users to browse the record store
    """
    search = StringField('search')
    submit = SubmitField('Search Records')
    
class AddRecordForm(FlaskForm):

    artist = StringField('Artist', validators=[DataRequired()])
    album_name = StringField('Album Name', validators=[DataRequired()])
    label = StringField('Label', validators=[DataRequired()])
    format = StringField('Format',  validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    year_released = StringField('Year Released', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    style = StringField('Style', validators=[DataRequired()])
    album_cover = FileField(validators=[FileRequired()])

    submit = SubmitField('Add Record')
