import unittest
import os
import sqlite3
import subprocess


class FunctionalTestCase(unittest.TestCase):
    def tearDown(self):
        os.remove('app_test.db')

    def test_end_to_end(self):
        """Run the app in test-mode and verify that the database was created properly.
        """
        subprocess.call('crawl-usesthis -t -d app_test.db', shell=True)
        self.assertTrue(os.path.exists('app_test.db'))

        con = sqlite3.connect('app_test.db')
        cur = con.cursor()
        n_people = cur.execute('select count(*) from people').fetchone()[0]
        n_tools = cur.execute('select count(*) from tools').fetchone()[0]
        n_relations = cur.execute('select count(*) from people_to_tools').fetchone()[0]
        con.close()

        self.assertGreater(n_people, 1)
        self.assertGreater(n_tools, 1)
        self.assertEquals(n_relations, n_tools)

    def test_end_to_end_twice(self):
        """Run the app in test-mode twice, consecutively. Verify that the database is still correct.
        """
        # Run 1
        subprocess.call('crawl-usesthis -t -d app_test.db', shell=True)
        self.assertTrue(os.path.exists('app_test.db'))

        con = sqlite3.connect('app_test.db')
        cur = con.cursor()
        n_people = cur.execute('select count(*) from people').fetchone()[0]
        n_tools = cur.execute('select count(*) from tools').fetchone()[0]
        n_relations = cur.execute('select count(*) from people_to_tools').fetchone()[0]
        con.close()

        self.assertGreater(n_people, 1)
        self.assertGreater(n_tools, 1)
        self.assertEquals(n_relations, n_tools)

        # Run 2
        subprocess.call('crawl-usesthis -t -d app_test.db', shell=True)
        self.assertTrue(os.path.exists('app_test.db'))

        con = sqlite3.connect('app_test.db')
        cur = con.cursor()
        same_n_people = cur.execute('select count(*) from people').fetchone()[0]
        same_n_tools = cur.execute('select count(*) from tools').fetchone()[0]
        same_n_relations = cur.execute('select count(*) from people_to_tools').fetchone()[0]
        con.close()

        self.assertEquals(same_n_people, n_people)
        self.assertEquals(same_n_tools, n_tools)
        self.assertEquals(same_n_relations, n_relations)

    def test_end_to_end_twice_fills_in_missing_person(self):
        """Run the app in test-mode twice. Between runs, remove a person from the database. After the second run, verify that the database is full again.
        """
        # Run 1
        subprocess.call('crawl-usesthis -t -d app_test.db', shell=True)
        self.assertTrue(os.path.exists('app_test.db'))

        con = sqlite3.connect('app_test.db')
        cur = con.cursor()
        n_people = cur.execute('select count(*) from people').fetchone()[0]
        n_tools = cur.execute('select count(*) from tools').fetchone()[0]
        n_relations = cur.execute('select count(*) from people_to_tools').fetchone()[0]
        self.assertGreater(n_people, 1)
        self.assertGreater(n_tools, 1)
        self.assertEquals(n_relations, n_tools)

        # Remove a person and their relevant items
        cur.execute('delete from tools where id = (select tool_id from people_to_tools where person_id = 1)')
        cur.execute('delete from people where id = 1')
        cur.execute('delete from people_to_tools where person_id = 1')
        n_people_rm = cur.execute('select count(*) from people').fetchone()[0]
        n_tools_rm = cur.execute('select count(*) from tools').fetchone()[0]
        n_relations_rm = cur.execute('select count(*) from people_to_tools').fetchone()[0]
        con.close()

        # Check that the removal worked
        self.assertEquals(n_people_rm, n_people-1)
        self.assertLess(n_tools_rm, n_tools)
        self.assertLess(n_relations_rm, n_relations)

        # Run 2
        subprocess.call('crawl-usesthis -t -d app_test.db', shell=True)
        self.assertTrue(os.path.exists('app_test.db'))

        con = sqlite3.connect('app_test.db')
        cur = con.cursor()
        more_n_people = cur.execute('select count(*) from people').fetchone()[0]
        more_n_tools = cur.execute('select count(*) from tools').fetchone()[0]
        more_n_relations = cur.execute('select count(*) from people_to_tools').fetchone()[0]
        con.close()

        # Check that the database is back to normal
        self.assertEqual(more_n_people, n_people)
        self.assertEqual(more_n_tools, n_tools)
        self.assertEqual(more_n_relations, n_relations)
