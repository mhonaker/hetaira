import os
import pygal
from pygal.style import Style
from app import app
from flask import render_template, flash, redirect, url_for, Response, session
from werkzeug import secure_filename
from .forms import DataUpload
from .promiscuity import calculate_results, PubChemError, BitstringError
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
    
    # set up a plot of the results
    fig_style = Style(label_font_size = 16,
                      major_label_font_size = 16,
                      title_font_size = 18)
    fig = pygal.Bar(disable_xml_declaration=True,
                    range=(0.0, 1.0), style=fig_style)
    fig.title = 'Promiscuity Indicies'
    fig.x_labels = [result[0] for result in results[:-1]]
    fig.y_labels = [0.0, 0.25, 0.5, 0.75, 1.0]
    fig.add('I', [float(result[1]) for result in results[:-1]])
    try:
        fig.add('J', [float(result[2]) for result in results[:-1]])
    except IndexError:
        pass
    fig.value_formatter = lambda x: '%.3f' % x

    if len(results) > 20:
        results = results[:21]
    return render_template('results.html', results=results,
                           title='Results', fig=fig)

@app.route('/download')
def download():

    results = (','.join(result) +'\n' for result in session['results'])
    return Response(results, mimetype='text/csv',
                    headers={'Content-Disposition': 
                             'attachment;filename = results.csv'})

@app.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ')

@app.route('/examples')
def examples():
    return render_template('examples.html', title='examples')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
