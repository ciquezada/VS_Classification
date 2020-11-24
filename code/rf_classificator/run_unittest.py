import os
import io
import unittest

class CrossValidationTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python test_cross_validation.py 1 "
        test_string += "test" + os.sep + "test_train_features.csv "
        test_string += "test" + os.sep + "test_cv_output "
        test_string += "test "
        os.system(test_string)

    def test_output_pdf_files(self):
        output_dir = "test" + os.sep + "test_cv_output"
        n_pdfs = len([name for name in os.listdir(output_dir)
                                if os.path.isfile(output_dir+os.sep+name)])
        self.assertEqual(n_pdfs, 4, 'incorrect quantity of pdfs generated')
        self.assertEqual(os.path.exists("test" + os.sep + "test_cv_output"),
                                                     True, 'output not created')

    def tearDown(self):
        os.system("rm -r test" + os.sep + "test_cv_output")

if __name__=="__main__":
    unittest.main()
