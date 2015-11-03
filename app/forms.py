from flask_wtf import Form
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed, FileRequired

class DataUpload(Form):
    datafile = FileField('your data', validators=[
        FileAllowed(['csv','tsv','txt','xlsx'], 'Bad filetype!')])
