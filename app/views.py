import os
from flask import render_template, flash, redirect, url_for, session
from app import app
from .forms import DataUpload
from .promiscuity import calculate_results, PubChemError, BitstringError
from werkzeug import secure_filename
from uuid import uuid4
import io

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    
    form = DataUpload()
    
    if form.validate_on_submit():
        # make a unique and safe filename
        filename = str(uuid4()) + secure_filename(form.datafile.data.filename)
        session['datafile'] = os.path.join(app.config['UPLOADS'], filename)
        form.datafile.data.save(session['datafile'])
        
        try:
            session['results'] = calculate_results(session['datafile'])
            return redirect(url_for('results'))
        except BitstringError:
            flash("Fingerprints can only contain 0's or 1's")
        except IndexError:
            flash('Fingerprints must be of equal length')
        except PubChemError:
            flash("There was a problem collecting fingerprints from the PubChem database. \
                  Please ensure that your CIDs are correct")
        os.remove(session['datafile'])
        
    return render_template('index.html',form=form)

@app.route('/results')
def results():
    results = session['results']['results']
    dset = session['results']['dset']


    return render_template('results.html', results=results, dset=dset)








    # now I will have a specific results page....see also template
    #results = calculate_results(os.path.join(app.config['UPLOADS'], filename))
    return session['stuff']
    
    #return render_template('results.html',
     #                      results=results['results']
      #                     dset=results['dset'])
    
    
# so...I am having trouble passing in the filename or results argument to the results page function.
# it may be that I just render a new template as noted above, but I woudl rather have a new url
# if possible...we'll see.
