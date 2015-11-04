"""
Module for performing Promiscuity Index
calculations for the Hetaira web tool.
"""

import numpy as np
import requests
from config import FP, CID, CID_FP, PUBCHEM_URL_START, PUBCHEM_URL_END, CID_PAD_LEN, DOWNLOADS
from pandas import read_csv, read_excel
from csv import Sniffer, DictWriter
from binascii import hexlify
from base64 import b64decode


def make_csv(data):
    """
    A helper function to make a csv file of results.
    """
    #with open(os.path.join(DOWNLOADS, 'results.csv'))
    pass

def calculate_results(file):
    """
    The working function to be called by the main view function.
    This function calls the file processing functions, then creates
    a Promiscuity object. This object has mehtods to be called
    to the caluclation of I, J, and dset (see below for further
    definitions). Then it returns the caluclated values in a form
    suitable for use in the view functions.
    """

    data = dataproc(file)
    promiscuity = Promiscuity(data[0], data[1], data[2])
    return {'dset': promiscuity.dset, 'results': promiscuity.results_array()}

def dataproc(file):
    """
    Attempts to determine if there are chemical bitstrings in the file
    or PubChem CID identifiers or none. Completes this only on text-type
    files. It will also attempt to determine if the file is an Excel file.

    Then this function calls the relevant file processing function for
    further processing to process the file into arrays useable by the
    Promiscuity class.
    """

    try:
        with open(file) as f:
            headers = f.readline().lower()
        if FP in headers:
            return fileproc(file, FP)
        elif CID in headers:
            return fileproc(file, CID)
        else:
            return fileproc(file, None)
    except UnicodeDecodeError:
        return excel_fileproc(file)

def fileproc(file, desctype):
    """
    Processes text files containing descriptor bitstrings into arrays
    suitable for generating Promiscuity objects.
    """

    with open(file) as f:
        sep = Sniffer().sniff(f.readline())
    
    if desctype is not None:
        df = read_csv(file, sep=sep.delimiter, dtype={desctype: object})
        ids = df.columns.values[~(df.columns.values == desctype)]
        data = df[ids]

        if desctype == CID:
            descriptors = get_pubchem_descriptors(df[CID])
        else:
            descriptors = bitarray(df[desctype])
    else:
        data = read_csv(file, sep=sep.delimiter)
        ids = data.columns.values
        descriptors = None

    return [ids, data, descriptors]

def excel_fileproc(file):
    """
    Processes Excel files into arrays suitable for generating 
    Promiscuity objects.
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
    2D fingerprints via PUG REST API. Then calls the conversion helper
    functions to return the proper bit array.
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
    padding off the ends.
    """
    
    return bin(int(hexlify(b64decode(b64)), 16))[2:-CID_PAD_LEN]

def bitarray(fprints):
    """
    Converts an array of bitsrings into an array of bit arrays.
    """

    descriptors = np.array([[int(i) for i in fprint] for fprint in fprints])
    # see if bitstrings are equal length, throws IndexError if not equal
    descriptors.shape[1]
    return descriptors


class Promiscuity:


    """
    A class to compute and return Promiscuity Indicies. Included are
    methods for calculating both the unweighted Promiscuity Index (I),
    and J, the Promiscuity Index weighted by set dissimiliarity.
    Also available is the overall set dissimiliarity.
    """

    def __init__(self, items, data, descriptors=None):
        self.items = items
        self.data = np.asarray(data)
        self.descriptors = descriptors
        if self.descriptors is not None:
            self.d_length = len(descriptors)
            self.dset = self.dset()
            self.avg_dists = self.avg_dists()
        else:
            self.dset = 'not determined'

    def __repr__():
        pass

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
        The data should be strictly > 0 and more positive is `better`.
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

    def results_array(self):
        """
        Constructs an array of results.
        """
        
        if self.descriptors is not None:
            results = [{'id': self.items[i],
                        'J': self.jvalue(i),
                        'I': self.ivalue(i)}
                       for i in range(len(self.items))]
        else:
            results = [{'id': self.items[i], 'I': self.ivalue(i),
                        'J': 'not determined'}
                       for i in range(len(self.items))]
        return results
        
class Error(Exception):
    """Base class for some special exception in this module."""

class ArrayLengthError(Error):
    """Exception raised for errors in unequal bitstring lengths."""

class PubChemError(Error):
    """Exception raised to catch Pubchem CID or URL problems."""
