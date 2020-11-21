import os
import unittest

class FeetsExtractorTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python extract_features.py 1 "
        test_string += "test" + os.sep + "test_data "
        test_string += "test" + os.sep + "test_curves.csv "
        test_string += "test" + os.sep + "test_output.csv "
        test_string += "test "
        os.system(test_string)

    def test_output_pdf_files(self):
        self.assertEqual(os.path.exists("test" + os.sep + "test_output.csv"),
                                                     True, 'output not created')

    def tearDown(self):
        os.system("rm -r test" + os.sep + "test_output.csv")

class FeetsExtractorParallelTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python extract_features.py 2 "
        test_string += "test" + os.sep + "test_data "
        test_string += "test" + os.sep + "test_curves.csv "
        test_string += "test" + os.sep + "test_output.csv "
        os.system(test_string)

    def test_output_pdf_files(self):
        self.assertEqual(os.path.exists("test" + os.sep + "test_output.csv"),
                                                     True, 'output not created')

    def tearDown(self):
        os.system("rm -r test" + os.sep + "test_output.csv")

if __name__=="__main__":
    unittest.main()
