from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField,BooleanField,HiddenField
from wtforms.validators import DataRequired,ValidationError
from flask import current_app

class AdminForm(FlaskForm):
    source = StringField('Source')
    destination = StringField('Destination')
    rename = SubmitField('Rename')
    
    delete_ref = StringField('Delete')
    delete = SubmitField('Delete')
