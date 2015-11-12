"""
Configuration settings for Hetaira app.
"""

import os

# Settings related to Flask and extentions
DEBUG = False 

# get the secret key from environment
SECRET_KEY = os.environ['SECRET_KEY']

# NCBI Pubchem PUG-REST settings
PUBCHEM_URL_START = 'http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'
PUBCHEM_URL_END = '/property/Fingerprint2D/JSON'
FP = 'fingerprint'
CID = 'cid'
CID_FP = 'Fingerprint2D'
CID_PAD_LEN = 17

