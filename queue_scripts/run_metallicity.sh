#!/bin/bash
#
#PBS -V
#PBS -N VSC_pyfiner
#PBS -k eo
#PBS -l nodes=3:ppn=2
#PBS -l walltime=240:00:00


#####    intentamos algo loco     #####

# python send_DONE_email.py "adapter_Ks_metalicity.py INICIADO" "VVVx short period metallicity"
# cd VS_Classification/code/ks_metallicities
# python adapter_Ks_metallicity.py 120 ../../downloads/datos_vvvx/rrab_sel445198_vvvx ../../data/vvvx_shortp_curves.csv ../../data/vvvx_shortp_metallicities.csv
# python send_DONE_email.py "adapter_Ks_metalicity.py TERMINADO" "Se crearon todos los archivos"

cd VS_Classification/code/ks_metallicities
python run_unittest.py

echo "done!"
