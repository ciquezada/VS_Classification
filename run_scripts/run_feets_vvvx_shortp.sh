#!/bin/bash
#
#PBS -V
#PBS -N Fitting curves
#PBS -k eo
#PBS -l nodes=6:ppn=20
#PBS -l walltime=168:00:00


# cd VS_Classification/code/feets_extractor
# python ../monitoring/send_email.py "extract_features.py INICIADO" "VVVx short period feature extractor -p rrlyr"
# python extract_features.py 120 ../../downloads/datos_vvvx/rrab_sel445198_vvvx ../../data/vvvx_shortp_curves.csv ../../data/vvvx_shortp_features.csv rrlyr
# python ../monitoring/send_email.py "extract_features.py TERMINADO" "features en ../../data/vvvx_shortp_features.csv "

cd VS_Classification/code/feets_extractor
python run_unittest.py

echo "done!"
