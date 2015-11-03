import os
from flask import render_template, flash, redirect, url_for
from app import app
from .forms import DataUpload
from .promiscuity import calculate_results
from werkzeug import secure_filename
from uuid import uuid4


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():

    form = DataUpload()
    
    if form.validate_on_submit():
        # make a unique and safe filename
        filename = str(uuid4()) + secure_filename(form.datafile.data.filename)
        form.datafile.data.save(os.path.join(app.config['UPLOADS'], filename))
        results = calculate_results(os.path.join(app.config['UPLOADS'], filename))

    else:
        filename = 'blah'
        results = {'results': 'arrrrg', 'dset': 'arrrg2'} 
        dset = 'blah'
    return render_template('index.html',
                           form=form,
                           filename=filename,
                           results=results['results'],
                           dset=results['dset'])

@app.route('/results')
def results():
    pass
    
