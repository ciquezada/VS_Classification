Adapter Ks_metalicity on python 3.7+

Command to run the code:
  python adapter_Ks_metallicity.py number_parallel_processes data_directory curves_file_path output_path

curves dataframe format:
  vvv aov1 aov2 aov3 aov4 ...
  b299_102_51696 0.618356 0.309176 0.448103 0.472323
  b299_102_75503 0.341358 0.411846 0.205923 0.291591
  ...
  b299_102_42048 0.317038 0.376959 0.273658 0.273554
  b299_102_6554 0.83129 1.662566 4.994756 0.453939

run script for geryon2:

#!/bin/bash
#
#PBS -V
#PBS -N Fitting curves
#PBS -k eo
#PBS -l nodes=6:ppn=20
#PBS -l walltime=96:00:00


#####    intentamos algo loco     #####

python send_DONE_email.py "adapter_Ks_metalicity.py INICIADO" "VVVx short period metallicity"
cd VS_Classification/code/ks_metallicities
python adapter_Ks_metallicity.py 120 ../../downloads/datos_vvvx/rrab_sel445198_vvvx ../../data/vvvx_shortp_curves.csv ../../data/vvvx_shortp_metallicities.csv
python send_DONE_email.py "adapter_Ks_metalicity.py TERMINADO" "Se crearon todos los archivos"

echo "done!"
