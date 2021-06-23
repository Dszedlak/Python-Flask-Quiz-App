# app/auth/views.py
from werkzeug.utils import secure_filename
from flask import flash, redirect, render_template, url_for, request

#from flask_login import login_required, login_user, logout_user, login_manager
from . import store
import requests
from .forms import BrowseStoreForm, AddRecordForm
import os
import os.path

from app import engine
from .forms import app
from ..models import add_music, load_music, session, login_required, search_music, is_quiz_admin
import json

app.config["IMAGE_UPLOADS"] = "app/static/img/uploads"

@store.route('/store', methods=['GET'])
@login_required
def browse_store():
    
    """
    Handle requests to the /browse route
    Add a user to the database through the registration form
    """

    if request.method == 'GET' and request.args.get("search"):
        term = request.args.get('search')
        records = search_music(term)  
    
    else: 
        records = load_music()        
    

    # load registration template
    return render_template('store/browse.html', records=records, title='Browse Store', )

@store.route('/store/add', methods=['GET', 'POST'])
@is_quiz_admin
def add_record():
    
    form = AddRecordForm()
    if form.validate_on_submit(): 
            data = {
                    "artist": form.artist.data,
                    "album_name": form.album_name.data,
                    "label": form.label.data,
                    "format": form.format.data,
                    "country":form.country.data,
                    "year_released":form.year_released.data,
                    "genre":form.genre.data,
                    "style":form.style.data,
        }
            json_data = json.dumps(data)
            filename = request.files['album_cover']
            path = 'app/static/img/uploads/%s' % (filename.filename)

            if not os.path.exists(path):
                filename.save(os.path.join(app.config["IMAGE_UPLOADS"],secure_filename(filename.filename)))
                add_music(json_data,secure_filename(filename.filename), session['user_id'])
            else:
                filename.filename = resolve_conflict(filename.filename)
                filename.save(os.path.join(app.config["IMAGE_UPLOADS"], secure_filename(filename.filename)))
                add_music(json_data, secure_filename(filename.filename), session['user_id'])
       
            return redirect(url_for('store.add_record'))
            
    # load registration template
    return render_template('store/add.html', form=form, title='Add')

def resolve_conflict(basename):
    name, ext = os.path.splitext(basename)
    count = 0
    while True:
        count = count + 1
        newname = '%s_%d%s' % (name, count, ext)
        path = 'app/static/img/uploads/%s' % (newname)
        if not os.path.exists(path):
                return newname
