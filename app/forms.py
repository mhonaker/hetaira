"""
The set of forms needed for Hetaira.
"""

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import DecimalField, StringField
from wtforms.validators import NumberRange, Optional

class DataUpload(Form):
    datafile = FileField('data', validators=[
        FileAllowed(['csv','tsv','txt','xlsx'], 'Bad filetype'),
        FileRequired('You must upload a data file.')])

    min = DecimalField(places = None,validators=[
        Optional(),
        NumberRange(min=1e-10, message='Minimum value is 1E-10')])

