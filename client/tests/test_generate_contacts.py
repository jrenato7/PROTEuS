#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from tools.generate_contacts import *


# import sqlalchemy
# import testscenarios

class TestContactsFilters(unittest.TestCase):

    def test_treat_pdb_id(self):
        pdb_id = '1bga.pdb.ent'
        self.assertEqual(treat_pdb_id(pdb_id), '1bga')




'''class TestGenerateContactsPdbFile(unittest.TestCase):
    def'''




#load_tests = testscenarios.load_tests_apply_scenarios



if __name__ == '__main__':
    unittest.main()

