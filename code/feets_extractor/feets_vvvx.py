from ext_fit_fourier import FitFourier
from ext_fit_gp import FitGP
from ext_fit_template import FitTemplate
from ext_inter_percentile_range import InterPercentileRanges
from ext_magnitude_distribution import MagnitudeDistribution
from ext_scipy_anderson_darling import SciPyAndersonDarling
from ext_stats_model_tsa import StatsmodelTSA
import feets
import numpy as np
import pandas as pd
from multiprocessing import Pool
import os
import sys


NUM_PROC = int(sys.argv[1]) #120
TRAINING_FILE = sys.argv[2] #training_set_vvvx_complete.csv	
FEATURES_FILE = sys.argv[3] #training_set_vvvx_features.csv
cwd = os.getcwd()

feets.register_extractor(InterPercentileRanges)
feets.register_extractor(SciPyAndersonDarling)
feets.register_extractor(MagnitudeDistribution)
feets.register_extractor(StatsmodelTSA)
feets.register_extractor(FitGP)
feets.register_extractor(FitTemplate)
feets.register_extractor(FitFourier)

def drop_err(star_data):
    emed = star_data.emag.median()
    esig = star_data.emag.std()
    e95 = min(np.percentile(star_data.emag.values, [95])[0], emed+2.5*esig)
    return star_data.query("emag < {}".format(e95))

def load_features(info_file = "training_set.fnl", selected_features = []):
    """directorio de las curvas"""
    data_path = cwd + os.sep  + ".." + os.sep + "datos_vvvx" + os.sep + "o4_tset_cef" + os.sep
    
    """cargar csv de informacion"""
    info = pd.read_csv(info_file, delim_whitespace=True)

    """para paralelizar"""
    def arg_gen():
        for i, row in info.iterrows():
            bad_tiles = ["b293", "b294", "b295", "b296",
                             "b307", "b308", "b309", "b310"]
            #if (not row["vvv"].split("_")[0] in bad_tiles) and os.path.exists(data_path + row["vvv"] + ".dat"):
            if os.path.exists(data_path + row["vvv"] + ".dat"):
                yield i, row, data_path, selected_features
            else:
                print("Bad tile or non exists: {}".format(row["vvv"]))

    data = []
    p = Pool(NUM_PROC)
    data = p.map(extractor_worker, arg_gen())

    features = pd.DataFrame(data, columns= ["filename", "label", "period"] + selected_features)
    return features

def extractor_worker(arg):
    i, row, path, selected_features = arg
    gp_dependent_features = ["RiseRatio", "DownRatio",
                             "RiseDownRatio", "Tm"]
    template_dependent_features = ["R2Template", "MseTemplate",
                                   "A1A2ratio"]
    fcomponents_dependent_features = ['a0', 'a1', 'a2', 'a3',
                                      'a4', 'a5', 'a6', 'a7',
                                      'phi_1', 'phi_2', 'phi_3',
                                      'phi_4', 'phi_5', 'phi_6',
                                      'phi_7', 'a21', 'a31', 'a41',
                                      'p21', 'p31', 'p41',]
    star_data = pd.read_csv(path + row["vvv"] + ".dat",
                                names=["mjd", "mag", "emag"], 
                                        delim_whitespace=True)
    star_data = drop_err(star_data)
    min_aov = row[["aov1","aov2"]].min()
    
    params = {}
    if not set(selected_features).isdisjoint(gp_dependent_features):
        params["FitGP"] = {"period": min_aov, "gamma": 0.5}
    if not set(selected_features).isdisjoint(template_dependent_features):
        params["FitTemplate"] = {"period": min_aov}
    if not set(selected_features).isdisjoint(fcomponents_dependent_features):
        params["FitFourier"] = {"period": min_aov, "gamma": 0.5}
           
    
    fs = feets.FeatureSpace(data=["time", "magnitude", "error"],
                        only=selected_features,
                        **params
                       )
    
    extr = fs.extract(time=star_data.mjd, magnitude=star_data.mag, error=star_data.emag)
    extr = dict(zip(*extr))
    extr = list(pd.DataFrame([extr])[selected_features].values[0])
    
    return [row["vvv"], row["label"], min_aov] + extr

if __name__=="__main__":
    selected_features = [
            'A1A2_ratio',
            'AC_std',
            'AD',
            	'Amplitude',
            	'AndersonDarling',
            	'Autocor_length',
            	'Beyond1Std',
            	'CAR_mean',
            	'CAR_sigma',
            	'CAR_tau',
            	'Con',
            	'Eta_e',
            	'FluxPercentileRatioMid20',
            	'FluxPercentileRatioMid35',
            	'FluxPercentileRatioMid50',
            	'FluxPercentileRatioMid65',
            	'FluxPercentileRatioMid80',
            	'Freq1_harmonics_amplitude_0',
            	'Freq1_harmonics_amplitude_1',
            	'Freq1_harmonics_amplitude_2',
            	'Freq1_harmonics_amplitude_3',
            	'Freq1_harmonics_rel_phase_0',
            	'Freq1_harmonics_rel_phase_1',
            	'Freq1_harmonics_rel_phase_2',
            	'Freq1_harmonics_rel_phase_3',
            	'Freq2_harmonics_amplitude_0',
            	'Freq2_harmonics_amplitude_1',
            	'Freq2_harmonics_amplitude_2',
            	'Freq2_harmonics_amplitude_3',
            	'Freq2_harmonics_rel_phase_0',
            	'Freq2_harmonics_rel_phase_1',
            	'Freq2_harmonics_rel_phase_2',
            	'Freq2_harmonics_rel_phase_3',
            	'Freq3_harmonics_amplitude_0',
            	'Freq3_harmonics_amplitude_1',
            	'Freq3_harmonics_amplitude_2',
            	'Freq3_harmonics_amplitude_3',
            	'Freq3_harmonics_rel_phase_0',
            	'Freq3_harmonics_rel_phase_1',
            	'Freq3_harmonics_rel_phase_2',
            	'Freq3_harmonics_rel_phase_3',
            'GP_DownRatio',
            'GP_RiseDownRatio',
            'GP_RiseRatio',
            'GP_Skew',
            	'Gskew',
            	'LinearTrend',
            	'MaxSlope',
            	'Mean',
            	'Meanvariance',
            	'MedianAbsDev',
            	'MedianBRP',
            'MseTemplate',
            	'PairSlopeTrend',
            	'PercentAmplitude',
            	'PercentDifferenceFluxPercentile',
            	'PeriodLS',
            	'Period_fit',
            	'Psi_CS',
            	'Psi_eta',
            	'Q31',
            'R2Template',
            'Rcs',
            	'Skew',
            	'SlottedA_length',
            	'SmallKurtosis',
            	'Std',
            	'StetsonK',
            	'StetsonK_AC',
            	'StructureFunction_index_21',
            	'StructureFunction_index_31',
            	'StructureFunction_index_32',
             'Tm',
             'a0',
             'a1',
             'a2',
             'a3',
             'a4',
             'a5',
             'a6',
             'a7',
             'iqr',
             'kurtosis',
             'mad',
             'mediana',
             'mpr20',
             'mpr35',
             'mpr50',
             'mpr65',
             'mpr80',
             'mv',
             'phi_1',
             'phi_2',
             'phi_3',
             'phi_4',
             'phi_5',
             'phi_6',
             'phi_7',
             'sigma',
             'skewness',
             'slope',
             'Beyond3Std',
             'Beyond5Std',
             'a21',
             'a31',
             'a41',
             'p21',
             'p31',
             'p41',
		]

    ext_features = load_features(info_file=TRAINING_FILE, selected_features=selected_features)
    print(ext_features)
    ext_features.to_csv(FEATURES_FILE, sep=" ", index=False)
