"""
Module for performing Promiscuity Index
calculations for the Hetaira web tool.
"""

import numpy as np
from .util import process_data
from string import ascii_lowercase


def calculate_results(file):
    """
    Working function to be called by main view function.
    """
    data = process_data(file)
    promiscuity = Promiscuity(data[0], data[1], data[2])
    return promiscuity.hetaira_results()


class Promiscuity:
    """
    A class to compute and return Promiscuity Indicies. Included are
    methods for calculating both the unweighted Promiscuity Index (I),
    and J, the Promiscuity Index weighted by dissimiliarity.
    Also available is the overall set dissimiliarity.
    """

    def __init__(self, items, data, descriptors=None, min = 1e-6):
        self.items = items
        # min is the presumed lower bound of the functional unit
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


#---------------------------------------------------------------------
#
# create a couple of examples
#
#---------------------------------------------------------------------

def example_one():
    """
    Generates a set of sample data for the
    examples page of the hetaira web tool.
    """
    
    np.random.seed(5)
    ids = ['Pr'] + list(ascii_lowercase) + ['Sp']
    
    # make some data where all activities are the same
    data = np.ones((26,26))
    
    # make some random activites to pull from
    y = np.random.uniform(1000, 2500, (26,26))
    
    # this will replace the ones with numbers from the uniform
    # distribution, increasing by one at each column
    # using the upper triangular matrix
    data[np.triu_indices(26)] = y[np.triu_indices(26)]

    # stack a perfectly promiscuous and a perfectly (almost)
    # specific column on either side of the data
    data = np.hstack((np.full((26,1), 1e-10), data, np.ones((26,1))))
    data[0,0] = 100
    descriptors = None
    example = Promiscuity(ids, np.fliplr(data), descriptors)
    return example.hetaira_results()


def example_two():
    """
    Generates a set of jackknife analysis data 
    for the hetaira web tool.
    """
    
    ids = ['PLA', 'PHA', 'Sp']
    d1 = np.random.uniform(11, 12, (10,1))
    d2 = np.random.uniform(1000, 2000, (10,1))
    d3 = np.random.uniform(0.1, 0.3, (10,1))
    data = np.hstack((d1, d2, d3))
    data[5,-1] = 100
    
    results = []
    for row in range(data.shape[0]):
        pr_obj = Promiscuity(ids, np.concatenate((
            data[:row], data[row+1:]), axis=0), None)
        results.append(pr_obj.results())
    return results

