import unittest
from immutable_tree import *
from red_black_tree import *
import numpy as np
import os

class ImmutableTreeTest(unittest.TestCase): 
	"""
	These tests concern the ImmutableTree Class
	"""
	def test_requireCommit(self):
		 '''
		 Verify that an error is raised the user doesn't commit a change
		 '''
		 os.system("rm /tmp/test2.dbdb")
		 db = it_connect("/tmp/test2.dbdb")
		 db.set("rahul", "aged")
		 db.set("pavlos", "aged")
		 db.set("kobe", "stillyoung")
		 db.close()
		 db = it_connect("/tmp/test2.dbdb")
		 with self.assertRaises(KeyError):
			 db.get("rahul")

	def test_get(self):
		'''
		Verify that get works as expected after commit
		'''
		os.system("rm /tmp/test2.dbdb")
		db = it_connect("/tmp/test2.dbdb")
		db.set("rahul", "aged")
		db.set("pavlos", "aged")
		db.set("kobe", "stillyoung")
		db.commit()
		db.close()
		db = it_connect("/tmp/test2.dbdb")
		self.assertEqual(db.get("rahul"), 'aged')
		
	def test_reset(self):
		'''
		Verify that setting a key already in the dictionary changes
		the original key-value binding, i.e. duplicates are removed
		and new key-value binding is kept
		'''
		os.system("rm /tmp/test2.dbdb")
		db = it_connect("/tmp/test2.dbdb")
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
		db = it_connect("/tmp/test2.dbdb")
		db.set("rahul", "aged")
		db.set("pavlos", "aged")
		db.set("kobe", "stillyoung")
		db.set("rahul", "young")
		db.commit()
		db.close()
		db = it_connect("/tmp/test2.dbdb")
		self.assertEqual(db.get("rahul"), 'young')

	def test_delete(self):
		'''
		Verify that reset information is kept after commit
		'''
		os.system("rm /tmp/test2.dbdb")
		db = it_connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.delete("pavlos")
		db.commit()
		db.close()
		db = it_connect("/tmp/test2.dbdb")
		with self.assertRaises(KeyError):
			 db.get("pavlos")
                
	def test_multiconnect(self):
		'''
		Verify that keys can be accessed from multiple reads.
		'''
		os.system("rm /tmp/test2.dbdb")
		db1 = it_connect("/tmp/test2.dbdb")
		db1.set("rahul", "aged")
		db1.commit()
		db1.close()
		
		db2 = it_connect("/tmp/test2.dbdb")
		assert db2.get("rahul") == "aged"
		db2.close()
		
	def test_nokey(self):
		'''
		Verify that nonexistent keys cannot be accessed
		'''
		os.system("rm /tmp/test2.dbdb")
		db = it_connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.set("rahul", "aged")
		db.commit()
		with self.assertRaises(KeyError):
			db.get("victor")
			db.close()
        
	def test_overwrite(self):
		'''
		Test overwriting of keys
		'''
		
		os.system("rm /tmp/test2.dbdb")
		db = it_connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.set("pavlos", "young")
		db.commit()
		self.assertEqual(db.get("pavlos"), 'young')
        
	def test_multiwrite(self):
		'''
		Test for writes from multiple db accesses
		'''
		
		os.system("rm /tmp/test2.dbdb")
		db = it_connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.commit()
		db.close()
		
		db2 = it_connect("/tmp/test2.dbdb")
		db2.set("rahul", "young")
		db2.commit()
		db2.close()
		
		db3 = it_connect("/tmp/test2.dbdb")
		self.assertEqual(db3.get("pavlos"), "aged")
        
class RedBlackTreeTest(unittest.TestCase): 
	"""
	These tests concern the RedBlackTree Class
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

	def test_balance(self):
		'''
		Verify that reset information is kept after commit
		'''
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.set("rahul", "aged")
		db.set("victor", "aged")
		self.assertEqual(db.getRootKey(), 'rahul')		
		
	def test_multiconnect(self):
		'''
		Verify that keys can be accessed from multiple reads.
		'''
		os.system("rm /tmp/test2.dbdb")
		db1 = connect("/tmp/test2.dbdb")
		db1.set("rahul", "aged")
		db1.commit()
		db1.close()
		
		db2 = connect("/tmp/test2.dbdb")
		assert db2.get("rahul") == "aged"
		db2.close()
		
	def test_nokey(self):
		'''
		Verify that nonexistent keys cannot be accessed
		'''
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.set("rahul", "aged")
		db.commit()
		with self.assertRaises(KeyError):
			db.get("victor")
			db.close()
        
	def test_overwrite(self):
		'''
		Test overwriting of keys
		'''
		
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.set("pavlos", "young")
		db.commit()
		self.assertEqual(db.get("pavlos"), 'young')
		
	def test_multiwrite(self):
		'''
		Test for writes from multiple db accesses
		'''
		
		os.system("rm /tmp/test2.dbdb")
		db = connect("/tmp/test2.dbdb")
		db.set("pavlos", "aged")
		db.commit()
		db.close()
		
		db2 = connect("/tmp/test2.dbdb")
		db2.set("rahul", "young")
		db2.commit()
		db2.close()
		
		db3 = connect("/tmp/test2.dbdb")
		self.assertEqual(db3.get("pavlos"),"aged")
        
def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(ImmutableTreeTest))
	suite.addTest(unittest.makeSuite(RedBlackTreeTest))
	return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run((suite()))
    

