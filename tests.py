"""
Testing module for hetaira project.
"""
import unittest
from app.promiscuity import Promiscuity, dataproc, get_pubchem_descriptors, bitarray, PubChemError, BitstringError
from numpy import isnan

class TestCase(unittest.TestCase):
    

    def setUp(self):
        ids = ['id1', 'id2']
        self.p1 = Promiscuity(ids, [[1,1], [1,1]], [[1,1,1,1],[1,1,0,0]])
        self.p2 = Promiscuity(ids, [[1,1], [1,1]], [[1,1,1,1],[0,0,0,0]])
        self.p3 = Promiscuity(ids, [[1,1], [1,1]], [[1,1,1,1],[1,1,1,1]])
        self.p4 = Promiscuity(ids, [[1,1], [1,1]])
        
        testdata1 = dataproc('testdata/testdata.csv')
        self.p5 = Promiscuity(testdata1[0], testdata1[1], testdata1[2])
        testdata2 = dataproc('testdata/testdata.tsv')
        self.p6 = Promiscuity(testdata2[0], testdata2[1], testdata2[2])
        testdata3 = dataproc('testdata/testdata.xlsx')
        self.p7 = Promiscuity(testdata3[0], testdata3[1], testdata3[2])

        self.p8 = Promiscuity(ids, [[0,0], [1,0.5]], [[1,0,1,0], [1,1,0,0]])

    def test_avg_dists(self):
        self.assertEqual(sum(self.p1.avg_dists), sum([0.5,0.5]))
        self.assertEqual(len(self.p1.avg_dists), 2)
        self.assertEqual(sum(self.p2.avg_dists), sum([1.0,1.0]))
        self.assertEqual(sum(self.p3.avg_dists), sum([0.0,0.0]))
        self.assertEqual(round(sum(self.p5.avg_dists), 4), 42.6497)
        self.assertEqual(len(self.p5.avg_dists), 64)
        self.assertEqual(len(self.p6.avg_dists), 64)
        self.assertEqual(len(self.p7.avg_dists), 64)

    def test_dset(self):
        self.assertEqual(self.p1.dset, 0.5)
        self.assertEqual(self.p2.dset, 1.0)
        self.assertEqual(self.p3.dset, 0.0)
        self.assertEqual(round(self.p5.dset, 4), 0.9930)

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
        self.assertEqual(round(self.p5.results()['3A4']['I'], 4), 0.7734)
        self.assertEqual(round(self.p5.results()['3A4']['J'], 4), 0.7775)
        self.assertEqual(self.p4.results()['id1']['I'], 1.0)
        self.assertEqual(round(self.p7.results()['3A4']['J'], 4), 0.7775)
        self.assertEqual(round(self.p8.results()['id1']['I'], 6), 2.1e-5)

    def test_get_pubchem_descriptors(self):
        self.assertEqual(get_pubchem_descriptors(['1']).shape, (1,881))
        self.assertRaises(PubChemError, get_pubchem_descriptors, ['a'])
    
    def test_bitarray(self):
        self.assertRaises(IndexError, bitarray,[[1,1],[1]])
        self.assertRaises(BitstringError, bitarray,[[1,0,3],[0,0,1]])
        


unittest.main()

