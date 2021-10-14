import os
import io
import unittest


cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

class FeetsExtractorTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python adapter_catalog_duplicates.py "
        test_string += f"-p 1 "
        test_string += f"-i \"{cwd}{os.sep}unittest{os.sep}test_catalog.csv\" "
        test_string += f"-o \"{cwd}{os.sep}unittest{os.sep}test_output.csv\" "
        test_string += f"-c \"{cwd}{os.sep}unittest{os.sep}test_duplicates_config.json\" "
        os.system(test_string)

    def test_output_file(self):
        self.assertEqual(os.path.exists("unittest" + os.sep + "test_output.csv"),
                                                     True, 'output not created')

    def test_output_content(self):
        test_path = "unittest" + os.sep + "test_output.csv"
        correct_test_path = "unittest" + os.sep + "correct_output.csv"
        with io.open(test_path) as test:
            with io.open(correct_test_path) as correct:
                self.assertListEqual(list(test), list(correct), "incorrect output")

    def tearDown(self):
        test_file = "unittest" + os.sep + "test_output.csv"
        os.remove(test_file)

class FeetsExtractorParallelTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python adapter_catalog_duplicates.py "
        test_string += f"-p 3 "
        test_string += f"-i \"{cwd}{os.sep}unittest{os.sep}test_catalog.csv\" "
        test_string += f"-o \"{cwd}{os.sep}unittest{os.sep}test_output.csv\" "
        test_string += f"-c \"{cwd}{os.sep}unittest{os.sep}test_duplicates_config.json\" "
        os.system(test_string)

    def test_output_file(self):
        self.assertEqual(os.path.exists("unittest" + os.sep + "test_output.csv"),
                                                     True, 'output not created')

    def test_output_content(self):
        test_path = "unittest" + os.sep + "test_output.csv"
        correct_test_path = "unittest" + os.sep + "correct_output.csv"
        with io.open(test_path) as test:
            with io.open(correct_test_path) as correct:
                self.assertListEqual(list(test), list(correct), "incorrect output")

    def tearDown(self):
        test_file = "unittest" + os.sep + "test_output.csv"
        os.remove(test_file)

if __name__=="__main__":
    unittest.main()