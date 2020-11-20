import os
import unittest

class pyfinerAdapterTestCase(unittest.TestCase):
    def setUp(self):
        test_string = "python adapter_Ks_metallicity.py 1 "
        test_string += "test" + os.sep + "test_data "
        test_string += "test" + os.sep + "test_curves.csv "
        test_string += "test" + os.sep + "test_output.csv "
        os.system(test_string)

    def test_output_pdf_files(self):
        n_pdfs = len([name for name in os.listdir('.')
                                        if os.path.isfile("output_pdf")])
        self.assertEqual(b_pdfs, 5, 'incorrect quantity of pdfs generated')

    def test_output_pdf_files(self):
        self.assertEqual(os.path.exists("test" + os.sep + "test_output.csv"),
                                                     True, 'output not created')

    def tearDown(self):
        os.system('rm -r output_pdf')
        os.system("rm -r test" + os.sep + "test_output.csv")


if __name__=="__main__":
    unittest.main()
