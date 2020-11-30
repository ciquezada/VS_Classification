import os
import io
import unittest


class SearchParamsTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python search_params.py 2 "
        test_string += "unittest" + os.sep + "unittest_train_features.csv "
        test_string += "unittest" + os.sep + "test_best_params.txt "
        test_string += "test "
        os.system(test_string)

    def test_output_files(self):
        self.assertEqual(os.path.exists("unittest" + os.sep + "test_best_params.txt"),
                                                     True, 'output not created')

    def tearDown(self):
        os.system("rm -r unittest" + os.sep + "test_best_params.txt")

class CrossValidationTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python test_cross_validation.py 1 "
        test_string += "unittest" + os.sep + "unittest_train_features.csv "
        test_string += "unittest" + os.sep + "unittest_cv_output "
        test_string += "test "
        os.system(test_string)

    def test_output_files(self):
        output_dir = "unittest" + os.sep + "unittest_cv_output"
        n_pdfs = len([name for name in os.listdir(output_dir)
                                if os.path.isfile(output_dir+os.sep+name)])
        self.assertEqual(n_pdfs, 5, 'incorrect quantity of reports generated')
        self.assertEqual(os.path.exists("unittest" + os.sep + "unittest_cv_output"),
                                                     True, 'output not created')

    def tearDown(self):
        os.system("rm -r unittest" + os.sep + "unittest_cv_output")

class ClassifyTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python classify.py 1 "
        test_string += "unittest" + os.sep + "unittest_train_features.csv "
        test_string += "unittest" + os.sep + "unittest_test_features.csv "
        test_string += "unittest" + os.sep + "unittest_test_results.csv "
        test_string += "test "
        os.system(test_string)

    def test_output_pdf_files(self):
        output_file = "unittest" + os.sep + "unittest_test_results.csv"
        self.assertEqual(os.path.exists(output_file), True,
                                                        'output not created')

    def tearDown(self):
        os.system("rm -r unittest" + os.sep + "unittest_test_results.csv")

if __name__=="__main__":
    unittest.main()
