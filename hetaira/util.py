"""
Utility functions for the Hetaira web tool. File reading,
error classes and example data generation.
"""

import numpy as np
import requests
import random
from config import FP, CID, CID_FP, PUBCHEM_URL_START, PUBCHEM_URL_END, CID_PAD_LEN
from pandas import read_csv
from csv import Sniffer
from binascii import hexlify
from base64 import b64decode
from io import BytesIO


def process_data(data):
    """
    Conversion utility to process a data stream into a variable
    array for Promiscuity Index calculations.
    """

    header = data.readline().lower()
    data.seek(0)
    if FP.encode() in header:
        return process_csv(data, FP)
    elif CID.encode() in header:
        return process_csv(data, CID)
    else:
        return process_csv(data, None)


def process_csv(data, desctype):
    """
    Helper function for process_data().   
    """

    sep = Sniffer().sniff(data.readline().decode('utf-8'))
    data.seek(0)
    if desctype is not None:
        df = read_csv(BytesIO(data.read()),
                      sep=sep.delimiter, dtype={desctype: object},
                      skipinitialspace=True)
        ids = df.columns.values[~(df.columns.values == desctype)]
        data = df[ids]
        if desctype == CID:
            descriptors = get_pubchem_descriptors(df[CID])
        else:
            descriptors = bitarray(df[desctype])
    else:
        data = read_csv(BytesIO(data.read()), sep=sep.delimiter)
        ids = data.columns.values
        descriptors = None

    return [ids, data, descriptors]


def get_pubchem_descriptors(cids):
    """
    Takes an an array of Pubchem CIDs and retrieves the base64 encoded
    2D fingerprints via PUG REST API.
    """

    url = PUBCHEM_URL_START + ','.join(cids) + PUBCHEM_URL_END
    r = requests.get(url)
    if r.status_code != 200:
        raise PubChemError
    else:
        fprints = [b64tobitstring(fprint[CID_FP])
                   for fprint in r.json()['PropertyTable']['Properties']]

    return bitarray(fprints) 


def b64tobitstring(b64):
    """
    Converts base64 encoded Pubchem 2D chemical fingerprints into
    bitstrings to be used in the promiscuity class. Also trims the
    padding off the end.
    """
    
    return bin(int(hexlify(b64decode(b64)), 16))[2:-CID_PAD_LEN]


def bitarray(fprints):
    """
    Converts an array of bitsrings into an array of bit arrays.
    """
    
    descriptors = np.array([[int(i) for i in fprint] for fprint in fprints])
    
    # see if bitstrings are equal length, throws IndexError if not equal
    descriptors.shape[1]

    # ensure only 0's and 1's are present in the fingerprints
    if len(set(descriptors.flatten()).union(set([1,0]))) != 2:
        raise BitstringError

    return descriptors

#--------------------------------------------------------------------
#
# Specific error classes to help make meaningful error messages.
#
#--------------------------------------------------------------------

class BitstringError(Exception):
    """Exception raised for errors in unequal bitstring lengths."""

class PubChemError(Exception):
    """Exception raised to catch Pubchem CID or URL problems."""


