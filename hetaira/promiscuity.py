"""
Module for performing Promiscuity Index
calculations for the Hetaira web tool.
"""

import numpy as np
import requests
from config import FP, CID, CID_FP, PUBCHEM_URL_START, PUBCHEM_URL_END, CID_PAD_LEN
from pandas import read_csv
from csv import Sniffer
from binascii import hexlify
from base64 import b64decode
from io import BytesIO


#----------------------------------------------------------
# Helper Functions to process data files for Promiscuity
# Index calculations.
#----------------------------------------------------------


def calculate_results(file):
    """
    Working function to be called by main view function.
    """
    data = process_data(file)
    promiscuity = Promiscuity(data[0], data[1], data[2])
    return promiscuity.hetaira_results()

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
                      sep=sep.delimiter, dtype={desctype: object})
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

def process_excel(file):
    """
    Helper function for process_data(). Used for excel files.
    """
    
    df = read_excel(file)
    headers = [header.lower() for header in df.columns.values]
    
    if not FP or CID in headers:
        ids = df.columns.values
        data = df
        descriptors = None
        return [ids, data, descriptors]
    if FP in headers:
        desctype = FP
        descriptors = bitarray(df[desctype])
    elif CID in headers:
        desctype = CID
        descriptors = get_pubchem_descriptors(df[desctype].astype(object))
    
    ids = df.columns.values[~(df.columns.values == desctype)]
    data = df[ids]
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


class Promiscuity:

    """
    A class to compute and return Promiscuity Indicies. Included are
    methods for calculating both the unweighted Promiscuity Index (I),
    and J, the Promiscuity Index weighted by dissimiliarity.
    Also available is the overall set dissimiliarity.
    """

    def __init__(self, items, data, descriptors=None, min = 1e-6):
        self.items = items
        # min is the presumeed lower bound of the functional unit
        self.data = np.asarray(data) + min
        self.descriptors = descriptors
        if self.descriptors is not None:
            self.d_length = len(descriptors)
            self.dset = self.dset()
            self.avg_dists = self.avg_dists()
        else:
            self.dset = 'not determined'

    def jaccard(self, u, v):
        """
        Computes the Jaccard distance between two boolean 1-D arrays.
        """

        dist = np.dot(u, v) / np.double(np.bitwise_or(u, v).sum())
        return 1 - dist

    def avg_dists(self):
        """
        Computes the average Jaccard distance between each 1-D 
        boolean array and all the others in the set.
        """
        
        d = self.descriptors
        # make an empty array to fill b/c it is a touch faster
        averages = np.empty([1, self.d_length])
        for i, u in enumerate(d):
            s = 0
            for j, v in enumerate(d):
                if i != j:
                    s += self.jaccard(u, v)
            averages[0, i] = (s / (self.d_length-1))
        return averages[0]

    def ivalue(self, idx):
        """
        Calculates the unweighted Promicuity Index.
        The data should be strictly > 0 and more positive is 'better'.
        """

        a = self.data[:,idx] / self.data[:,idx].sum()
        results = -(np.dot(a, np.log(a))) / np.log(len(self.data[:,idx]))
        return results
    
    def jvalue(self, idx):
        """
        Computes the weighted Promiscuity Index for an array of
        values that measures the `goodness` of function operating 
        on a set of items whose dissimilarity can be measured.

        The data should be strictly non-zero and more positive is `better`.
        Values in the avg_dists array should be in the same order and
        have the same length as the data array.
        """
        
        length = len(self.data)

        a = self.data[:,idx] / self.data[:,idx].sum()
        b = np.dot((self.avg_dists / self.dset), (a * np.log(a)))
        results = -length * (b / ((self.avg_dists / 
                                   self.dset).sum() * np.log(length)))
        return results 

    def dset(self):
        """
        Calculates the overall dissimilairity based on the descriptors.
        """

        a = 0.0
        b = 0.0
        sums = np.sum(self.descriptors, axis=0)
        for sum in sums:
            if sum > 0:
                if sum == self.d_length:
                    b += 1.
                else:
                    a += 1.
        return a / (a+b)

    def results(self):
        """
        Contructs a dict of promiscuity results for the whole dataset.
        This function is primairly for testing.
        """
        
        results = {}
        if self.descriptors is not None:
            for i in range(len(self.items)):
                results[self.items[i]] = {'I': self.ivalue(i),
                                          'J': self.jvalue(i)}
        else:
            for i in range(len(self.items)):
                results[self.items[i]] = {'I': self.ivalue(i)}
        return results

    def hetaira_results(self):
        """
        Returns an array of Promiscuity results suitable for
        delivery into a Flask Response CSV-like object.
        """
        
        if self.descriptors is not None:
            results = [[str(self.items[i]), str(self.ivalue(i)),
                        str(self.jvalue(i))] for i in range(len(self.items))]
        else:
            results = [[str(self.items[i]), str(self.ivalue(i))]
                       for i in range(len(self.items))]

        results.append(['dset', str(self.dset)])
        return results

        
class BitstringError(Exception):
    """Exception raised for errors in unequal bitstring lengths."""

class PubChemError(Exception):
    """Exception raised to catch Pubchem CID or URL problems."""
