"""
Configuration settings for Hetaira app.
"""

import os
from pygal.style import Style 

# Settings related to Flask and extentions
DEBUG = True

# get the secret key from environment
SECRET_KEY = 'akey'#os.environ['SECRET_KEY']

# NCBI Pubchem PUG-REST settings
PUBCHEM_URL_START = 'http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'
PUBCHEM_URL_END = '/property/Fingerprint2D/JSON'
FP = 'fingerprint'
CID = 'cid'
CID_FP = 'Fingerprint2D'
CID_PAD_LEN = 17

# plot settings for pygal
STYLE = Style(label_font_size = 16,
                      major_label_font_size = 16,
                      title_font_size = 18,
                      colors = ('#00b2f0','#ffd541',
                                '#5ae345','#0662ab', '#42b9de'))
YLAB = [0.0, 0.25, 0.5, 0.75, 1.0]
YTITLE = 'Promiscuity Index'

