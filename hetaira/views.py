import pygal
from hetaira import app
from flask import render_template, flash, redirect, url_for, Response, session
from .forms import DataUpload
from .promiscuity import calculate_results, example_one, example_two
from .util import PubChemError, BitstringError


# set up the examples
example_one = example_one()
example_two = example_two()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    
    form = DataUpload()
    
    if form.validate_on_submit():
        try:
            session['results'] = calculate_results(form.datafile.data)
            return redirect(url_for('results'))
        except (BitstringError, ValueError):
            flash("Fingerprints can only contain 0's or 1's")
        except IndexError:
            flash('Fingerprints must be of equal length')
        except PubChemError:
            flash("There was a problem collecting fingerprints from \
                  the PubChem database. Please verify the submitted CIDs")
    return render_template('index.html',form=form, title='Welcome')


@app.route('/results')
def results():

    results = session['results']
    
    # set up a plot of the results
    fig_style = Style(label_font_size = 16,
                      major_label_font_size = 16,
                      title_font_size = 18)
    fig = pygal.Bar(disable_xml_declaration=True,
                    range=(0.0, 1.0),
                    style=app.config['STYLE'])
    fig.title = 'Promiscuity Indices'
    fig.x_labels = [result[0] for result in results[:-1]]
    fig.y_labels = app.config['YLAB']
    fig.y_title = app.config['YTITLE']
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
   
    # plot of steadily decreasing promiscuity
    fig1 = pygal.Bar(disable_xml_declaration=True,
                     range=(0.0, 1.0),
                     style=app.config['STYLE'])
    fig1.x_labels = [x[0] for x in example_one[:-1]]
    fig1.y_labels = app.config['YLAB']
    fig1.y_title = app.config['YTITLE']
    fig1.add('I', [float(y[1]) for y in example_one[:-1]])

    # jackknife plot of promiscuous and specific
    fig2 = pygal.Line(disable_xml_declaration=True,
                      range=(0.0, 1.0),
                      style=app.config['STYLE'],
                      x_label_rotation=20)
    fig2.x_labels = ['Cmpd ' + str(i+1) for i in range(len(example_two))]
    fig2.y_labels = app.config['YLAB']
    fig2.y_title = app.config['YTITLE']
    fig2.add('Specific', [i['Sp']['I'] for i in example_two])
    fig2.add('Promiscuous High Activity', [i['PHA']['I'] for i in example_two])
    fig2.add('Promiscuous Low Activity', [i['PLA']['I'] for i in example_two])

    return render_template('examples.html',
                           title='examples',
                           fig1=fig1, fig2=fig2)

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

