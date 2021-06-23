# app/auth/views.py

from flask import flash, redirect, render_template, url_for
from . import admin
from .forms import AdminForm
from app import engine
from app import models
from ..models import login_required, clear_session, is_admin
import json

from base64 import b64decode, b64encode
from flask import Flask, request 
import xml.etree.ElementTree as ET
from lxml import etree
from html import escape
import cgi
import traceback
import xmltodict

@admin.route('/DSadmin', methods=['GET', 'POST'])
@is_admin
def Admin_home():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = AdminForm()

    # load registration template
    return render_template('admin/admin.html', form=form, title='Admin Page')

@admin.route('/DSadmin/Delete', methods=['GET', 'POST'])
def deleteData():

    return render_template('admin/delete.html', title='Admin Page')

@admin.route('/xml', methods=['POST', 'GET'])
def xml():
    parsed_xml = None
    
    html = """
    <html>
      <body>
    """   
    if request.method == 'POST':
        xml = request.form['xml']
        parser = etree.XMLParser(no_network=False, resolve_entities=False) # to enable network entity. see xmlparser-info.txt
        try:
            doc = etree.fromstring(str(xml), parser)
            parsed_xml = etree.tostring(doc)
            print(repr(parsed_xml))
        except:
	        print("Cannot parse the xml")
	        html += "Error:\n<br>\n" + traceback.format_exc()
    if (parsed_xml):
        html += "Result:\n<br>\n" + repr(parsed_xml)
    else:
        html += """
        <form action = "/xml" method = "POST">
            <p><h3>Enter xml to parse</h3></p>
            <textarea class="input" name="xml" cols="40" rows="5"></textarea>
            <p><input type = 'submit' value = 'Parse'/></p>
        </form>
        """
        html += """
        </body>
        </html>
        """
    return html