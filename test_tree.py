import unittest
from immutable_tree import *
import numpy as np


class immutableTreeTest(unittest.TestCase): 
	"""
	These tests concern the TimeSeries Class
	"""
	def test_requireCommit(self):
		'''
		Verify that an error is raised the user doesn't commit a change
		'''
                !rm /tmp/test2.dbdb
                db = connect("/tmp/test2.dbdb")
                db.set("rahul", "aged")
                db.set("pavlos", "aged")
                db.set("kobe", "stillyoung")
                db.close()
		with self.assertRaises(KeyError):
                    db = connect("/tmp/test2.dbdb")
                    db.get("rahul")

