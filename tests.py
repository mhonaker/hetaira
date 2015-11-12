"""
Testing module for hetaira project.
"""

import unittest
import hetaira
from hetaira.promiscuity import Promiscuity, get_pubchem_descriptors, bitarray
from hetaira.promiscuity import PubChemError, BitstringError, process_data
from numpy import isnan


class TestCase(unittest.TestCase):
    

    def setUp(self):
        self.app = hetaira.app.test_client()
        ids = ['id1', 'id2']
        self.p1 = Promiscuity(ids, [[1,1], [1,1]], [[1,1,1,1],[1,1,0,0]])
        self.p2 = Promiscuity(ids, [[1,1], [1,1]], [[1,1,1,1],[0,0,0,0]])
        self.p3 = Promiscuity(ids, [[1,1], [1,1]], [[1,1,1,1],[1,1,1,1]])
        self.p4 = Promiscuity(ids, [[1,1], [1,1]])

        self.p5 = Promiscuity(ids, [[0,0], [1,0.5]], [[1,0,1,0], [1,1,0,0]])

    def test_avg_dists(self):
        self.assertEqual(sum(self.p1.avg_dists), sum([0.5,0.5]))
        self.assertEqual(len(self.p1.avg_dists), 2)
        self.assertEqual(sum(self.p2.avg_dists), sum([1.0,1.0]))
        self.assertEqual(sum(self.p3.avg_dists), sum([0.0,0.0]))

    def test_dset(self):
        self.assertEqual(self.p1.dset, 0.5)
        self.assertEqual(self.p2.dset, 1.0)
        self.assertEqual(self.p3.dset, 0.0)

    def test_ivalue(self):
        self.assertEqual(self.p1.ivalue(0), 1.0)
        self.assertEqual(self.p1.ivalue(1), 1.0)
        self.assertEqual(self.p4.ivalue(0), 1.0) 

    def test_jvalue(self):
        self.assertEqual(self.p1.jvalue(0), 1.0)
        self.assertEqual(self.p1.jvalue(1), 1.0)
        assert isnan(self.p3.jvalue(0))
        with self.assertRaises(TypeError):
            self.p4.jvalue(0)

    def test_results(self):
        self.assertEqual(self.p4.results()['id1']['I'], 1.0)
        self.assertEqual(round(self.p5.results()['id1']['I'], 6), 2.1e-5)

    def test_get_pubchem_descriptors(self):
        self.assertEqual(get_pubchem_descriptors(['1']).shape, (1,881))
        self.assertRaises(PubChemError, get_pubchem_descriptors, ['a'])
    
    def test_bitarray(self):
        self.assertRaises(IndexError, bitarray,[[1,1],[1]])
        self.assertRaises(BitstringError, bitarray,[[1,0,3],[0,0,1]])
        self.assertRaises(ValueError, bitarray, [['a', 0, 0],[1,1,1]])

    def test_app_get_index(self):
        resp = self.app.get('/')
        assert b'Theory' in resp.get_data()
        self.assertEqual(self.app.post('/', data='testdata/testdata.csv').status_code, 200)

unittest.main()

