import os
from app import app
from flask import render_template, flash, redirect, url_for, Response, session 
from .forms import DataUpload
from .promiscuity import calculate_results, PubChemError, BitstringError
from werkzeug import secure_filename
from uuid import uuid4


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    
    form = DataUpload()
    
    if form.validate_on_submit():
        # make a unique and safe filename
        filename = str(uuid4()) + secure_filename(form.datafile.data.filename)
        session['datafile'] = os.path.join(os.path.join(
            os.path.dirname(__file__), 'uploads'), filename)
        form.datafile.data.save(session['datafile'])
        try:
            session['results'] = calculate_results(session['datafile'])
            return redirect(url_for('results'))
        except (BitstringError, ValueError):
            flash("Fingerprints can only contain 0's or 1's")
        except IndexError:
            flash('Fingerprints must be of equal length')
        except PubChemError:
            flash("There was a problem collecting fingerprints from \
                  the PubChem database. Please verify the submitted CIDs")
        finally:
            os.remove(session['datafile'])
        
    return render_template('index.html',form=form, title='Welcome')

@app.route('/results')
def results():

    results = session['results']
    if len(results) > 20:
        results = results[:21]
    return render_template('results.html', results=results, title='Results')

@app.route('/download')
def download():

    results = (','.join(result) +'\n' for result in session['results'])
    return Response(results, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename = results.csv'})

@app.route('/example')
def example():
    
    results = calculate_results(os.path.join(
        os.path.dirname(__file__), 'exampledata.csv'))
    return render_template('results.html', results=results)

@app.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ')

@app.route('/examples')
def examples():
    return render_template('examples.html', title='examples')
