import unittest
from immutable_tree import *
import numpy as np


class ImmutableTreeTest(unittest.TestCase): 
	"""
	These tests concern the TimeSeries Class
	"""
	def test_requireCommit(self):
		 '''
		 Verify that an error is raised the user doesn't commit a change
		 '''
		 os.system("rm /tmp/test2.dbdb")
		 db = connect("/tmp/test2.dbdb")
		 db.set("rahul", "aged")
		 db.set("pavlos", "aged")
		 db.set("kobe", "stillyoung")
		 db.close()
		 db = connect("/tmp/test2.dbdb")
		 with self.assertRaises(KeyError):
			 db.get("rahul")

	def test_get(self):
		'''
		Verify that get works as expected after commit
		'''
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("rahul", "aged")
		db.set("pavlos", "aged")
		db.set("kobe", "stillyoung")
		db.commit()
		db.close()
		db = connect("/tmp/test2.dbdb")
		self.assertEqual(db.get("rahul"), 'aged')
		
	def test_reset(self):
		'''
		Verify that setting a key already in the dictionary changes
		the original key-value binding, i.e. duplicates are removed
		and new key-value binding is kept
		'''
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("rahul", "aged")
		db.set("pavlos", "aged")
		db.set("kobe", "stillyoung")
		db.set("rahul", "young")
		self.assertEqual(db.get("rahul"), 'young')
		
	def test_resetCommit(self):
		'''
		Verify that reset information is kept after commit
		'''
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("rahul", "aged")
		db.set("pavlos", "aged")
		db.set("kobe", "stillyoung")
		db.set("rahul", "young")
		db.commit()
		db.close()
		db = connect("/tmp/test2.dbdb")
		self.assertEqual(db.get("rahul"), 'young')

	def test_delete(self):
		'''
		Verify that reset information is kept after commit
		'''
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.delete("pavlos")
		db.commit()
		db.close()
		db = connect("/tmp/test2.dbdb")
		with self.assertRaises(KeyError):
			 db.get("pavlos")


def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(ImmutableTreeTest))
	return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run((suite()))
