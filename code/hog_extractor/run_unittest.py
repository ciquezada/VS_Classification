import os
import io
import unittest

class FeetsExtractorTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python adapter_hog_extractor.py 1 "
        test_string += "unittest" + os.sep + "test_data "
        test_string += "unittest" + os.sep + "test_curves.csv "
        test_string += "unittest" + os.sep + "test_output.csv "
        test_string += "test "
        os.system(test_string)

    def test_output_file(self):
        self.assertEqual(os.path.exists("unittest" + os.sep + "test_output.csv"),
                                                     True, 'output not created')

    # def test_output_content(self):
    #     test_path = "unittest" + os.sep + "test_output.csv"
    #     correct_test_path = "unittest" + os.sep + "correct_output.csv"
    #     with io.open(test_path) as test:
    #         with io.open(correct_test_path) as correct:
    #             self.assertListEqual(list(test), list(correct), "incorrect output")

    def tearDown(self):
        os.system("rm -r unittest" + os.sep + "test_output.csv")

class FeetsExtractorParallelTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python adapter_hog_extractor.py 2 "
        test_string += "unittest" + os.sep + "test_data "
        test_string += "unittest" + os.sep + "test_curves.csv "
        test_string += "unittest" + os.sep + "test_output.csv "
        os.system(test_string)

    def test_output_file(self):
        self.assertEqual(os.path.exists("unittest" + os.sep + "test_output.csv"),
                                                     True, 'output not created')

    # def test_output_content(self):
    #     test_path = "unittest" + os.sep + "test_output.csv"
    #     correct_test_path = "unittest" + os.sep + "correct_output.csv"
    #     with io.open(test_path) as test:
    #         with io.open(correct_test_path) as correct:
    #             self.assertListEqual(list(test), list(correct), "incorrect output")

    def tearDown(self):
        os.system("rm -r unittest" + os.sep + "test_output.csv")

if __name__=="__main__":
    unittest.main()
