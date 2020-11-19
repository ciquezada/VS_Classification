import pandas as pd
import numpy as np
import os

#Pipeliene by F. Gran (fegran at uc.cl)

####### USER INPUT

input_file = 'input_rr.csv' #CSV file with 6 columns: Variable_name, Period, Ks_file, J_file, H_file, PDF_output_name.pdf
output_file = 'output_rr.csv' #CSV file will contain 25 columns with the results: Var_name, Period, Intensity/magnitude mean/median values, Fourier parameters, cost values, and metalicities.

####### END USER INPUT

names = ['var_name', 'P', 'file_ks', 'file_j', 'file_h', 'output_pdf']
data = pd.read_csv(input_file, names=names)

names = ['NAME', 'PERIOD', 'K_MAG' , 'K_INT' , 'J_MAG_MEAN' , 'J_INT_MEAN' , 'J_MAG_MEDI' , 'J_INT_MEDI' , \
            'H_MAG_MEAN' , 'H_INT_MEAN' , 'H_MAG_MEDI' , 'H_INT_MEDI' , 'U1' , 'U2' , 'U3' , 'U4' , 'RMSE' , \
            'COST' , 'COSTN' , 'N_FINAL' , 'N_INITIAL']
to_write = pd.DataFrame(index=data.index.values, columns=names)

for index, var in data.iterrows():
    
    output = os.popen('python pyfiner.py %s %f %s %s %s %s' %(var.var_name, 
        var.P, var.file_ks, var.file_j, var.file_h, var.output_pdf) ).read()

    to_write.iloc[index] = output.split('\n')[-2].split()
    

fill = '0'
to_write['FEH_J95'] = fill
to_write['eFEH_J95'] = fill
to_write['FEH_C09'] = fill
to_write['eFEH_C09'] = fill

for index, var in to_write.iterrows():

    os.system('echo %s > pymerlin_temp.dat' %(' '.join(var[['NAME', 'PERIOD', 'U1', 'U2', 'U3', 'U4']].values)))
    output = os.popen('python pymerlin.py pymerlin_temp.dat').read()
    
    _, feh_j95, efeh_j95, feh_c09, efeh_c09 = output.split('\n')[-2].split()

    to_write.FEH_J95.iloc[index] = feh_j95
    to_write.eFEH_J95.iloc[index] = efeh_c09
    to_write.FEH_C09.iloc[index] = feh_c09
    to_write.eFEH_C09.iloc[index] = efeh_c09

os.system('rm pymerlin_temp.dat')
to_write.to_csv(output_file, index=False, header=True)
