"""
Configuration settings for Hetaira app. Generally variables
that remain static, but might change, so they can all be updated in one
file if they do.

Does NOT contain secret information such as secret keys, database
and file storage routing info. These are not tracked by version
control, and override the settings below in a separate config file once
once instance_relative_config=True in __init__ file.
"""

import os

# Settings related to Flask and Flask extentions
# debug is False in instance config
DEBUG = True

# Place holders for secret instance config settings
UPLOADS = os.path.join(os.path.dirname(__file__), 'app/uploads')
DOWNLOADS = os.path.join(os.path.dirname(__file__), 'app/downloads')

# NCBI Pubchem PUG-REST settings
PUBCHEM_URL_START = 'http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'
PUBCHEM_URL_END = '/property/Fingerprint2D/JSON'
FP = 'fingerprint'
CID = 'cid'
CID_FP = 'Fingerprint2D'
CID_PAD_LEN = 17


