#Hetaira
A web tool for calculating Promiscuity Indicies.

Users submit a data file containing measures of function and possibly descriptor bitstrings. The user may instead submit [PubChem](https://pubchem.ncbi.nlm.nih.gov/) Chemical Identification Codes and hetaira will retrieve the CACTVS bitstring descriptors.

Promiscuity Indicies (weighted and unweighted) are calculated and returned along with total set dissimilarity.

Please see the [webpage](https://hetaira.herokuapp.com) and references therein for a full discussion of theory and usage.

[Try it out](https://hetaira.herokuapp.com)

**Local Use**
This repo contains all the code that allows localhost use.
For very basic use (this assumes you have installed [python 3.5.0](https://www.python.org/downloads/):
1. Set up a python virtual environment using [virtualenv](https://virtualenv.readthedocs.org/en/latest/)in the directory of your choice.
2. Install the requirements into the virtual environment using pip. The example below uses the command line.
3. Start the virtual environment (you can also set up [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)).
4. Then start the package. You'll have to either add a `SECRET_KEY` variable in the config.py file or set one in your shell environment `export SECRET_KEY="akey"`, or you can set it as shown below for that single instance.

```sh
$ python -m venv [dirname]
$ path_to_dirname/bin/pip install -r ~/path_to_dir/requirements.txt
$ source path_to_dirname/bin/activate
$ env SECRET_KEY="akey" python run.py
```
You should now be able to navigate to `localhost:5000` in the browser of your choice, however it will be a single thread process. Further deployment options are currently beyond the scope of this introduction, but may be included at some point.


