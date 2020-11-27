import pandas as pd
import numpy as np
import os
import sys


#Pipeliene by F. Gran (fegran at uc.cl)

def run_pyfiner(data):
    '''Pipeline by F. Gran (fegran at uc.cl) to calculate mellicities of RR Lyr

        Args:
            data (DataFrame):
                columns: ['var_name', 'period', 'ks_curve_file',
                            'j_curve_file', 'h_curve_file', 'output_pdf']

        Raises:
            None

        Returns:
            to_write (DataFrame): ['NAME', 'PERIOD', 'K_MAG', 'K_INT',
                                    'J_MAG_MEAN', 'J_INT_MEAN',
                                    'J_MAG_MEDI', 'J_INT_MEDI', 'H_MAG_MEAN',
                                    'H_INT_MEAN', 'H_MAG_MEDI', 'H_INT_MEDI',
                                    'U1', 'U2', 'U3', 'U4', 'RMSE', 'COST',
                                    'COSTN', 'N_FINAL', 'N_INITIAL']
        '''

    names = ['NAME', 'PERIOD', 'K_MAG', 'K_INT', 'J_MAG_MEAN', 'J_INT_MEAN',    \
                'J_MAG_MEDI', 'J_INT_MEDI', 'H_MAG_MEAN', 'H_INT_MEAN',         \
                 'H_MAG_MEDI', 'H_INT_MEDI', 'U1', 'U2', 'U3', 'U4', 'RMSE',    \
                  'COST', 'COSTN', 'N_FINAL', 'N_INITIAL']
    to_write = pd.DataFrame(index=data.index.values, columns=names)

    for index, var in data.iterrows():

        output = os.popen('python pyfiner.py %s %f %s %s %s %s' %(var.var_name,
            var.P, var.file_ks, var.file_j, var.file_h, var.output_pdf) ).read()
        # Validamos output
        if len(output.split('\n'))>1:
            to_write.iloc[index] = output.split('\n')[-2].split()
        else:
            to_write.iloc[index] = [var.var_name, var.P, np.nan, np.nan,
                                        np.nan, np.nan, np.nan, np.nan,
                                         np.nan, np.nan, np.nan, np.nan,
                                          np.nan, np.nan, np.nan, np.nan,
                                           np.nan, np.nan, np.nan, np.nan, np.nan]


    fill = '0'
    to_write['FEH_J95'] = fill
    to_write['eFEH_J95'] = fill
    to_write['FEH_C09'] = fill
    to_write['eFEH_C09'] = fill
    return to_write

def run_pymerlin(to_write, pymerlin_input_file):
    for index, var in to_write.iterrows():
        # Validamos input
        if not var.isna().U1:
            # os.system('echo %s > pymerlin_temp.dat' %(' '.join(var[['NAME', 'PERIOD', 'U1', 'U2', 'U3', 'U4']].values)))
            input_params = "{} {} {} {} {} {}".format(var.NAME, var.PERIOD,
                                                        var.U1, var.U2,
                                                         var.U3, var.U4)
            os.system(f"echo {input_params} > {pymerlin_input_file}")
            output = os.popen(f'python pymerlin.py {pymerlin_input_file}').read()

            _, feh_j95, efeh_j95, feh_c09, efeh_c09 = output.split('\n')[-2].split()
        else:
            feh_j95, efeh_j95, feh_c09, efeh_c09 = np.nan, np.nan, np.nan, np.nan

        to_write.FEH_J95.iloc[index] = feh_j95
        to_write.eFEH_J95.iloc[index] = efeh_c09
        to_write.FEH_C09.iloc[index] = feh_c09
        to_write.eFEH_C09.iloc[index] = efeh_c09

    # os.system(f'rm {pymerlin_input_file}')

    return to_write

if __name__=="__main__":
    ####### USER INPUT
    # input_file = "input_rr.csv" #CSV file with 6 columns: Variable_name, Period, Ks_file, J_file, H_file, PDF_output_name.pdf
    # output_file = 'output_rr.csv' #CSV file will contain 25 columns with the results: Var_name, Period, Intensity/magnitude mean/median values, Fourier parameters, cost values, and metalicities.
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    ####### END USER INPUT

    names = ['var_name', 'P', 'file_ks', 'file_j', 'file_h', 'output_pdf']
    data = pd.read_csv(input_file, names=names)

    # Pipeline by F. Gran (fegran at uc.cl)
    to_write = run_pyfiner(data)
    if not "-p-no_pymerlin" in sys.argv:
        pymerlin_input_file = sys.argv[3]
        to_write = run_pymerlin(to_write, pymerlin_input_file)
    to_write.to_csv(output_file, index=False, header=True)
