from classifier import SingleProbRF
import pandas as pd
import numpy as np
import sys
import os


NUM_PROC = int(sys.argv[1]) #numero dep rocesos
TRAINING_FILE = sys.argv[2] #vvv_tset_features.csv
SAMPLE_FILE = sys.argv[3] #vvv_all_features.csv
OUTPUT_FILE = sys.argv[4] #vvv_results.csv
NOALIASES_FILE = "vvvx_rr_noaliases.fnl"

cwd = os.getcwd()

def import_tset(file_path="vvv_tset_features.csv"):
    feets_data = pd.read_csv(file_path, sep=" ")
    feets_data = feets_data.dropna()
    phaser = lambda mjd: (mjd/(2*np.pi))%1.
    feets_data["a21"] = np.abs(feets_data.a2 / feets_data.a1)
    feets_data["a31"] = np.abs(feets_data.a3 / feets_data.a1)
    feets_data["a41"] = np.abs(feets_data.a4 / feets_data.a1)
    feets_data["p21"] = phaser(feets_data.phi_2 - 2*feets_data.phi_1)*2*np.pi
    feets_data["p31"] = phaser(feets_data.phi_3 - 3*feets_data.phi_1)*2*np.pi
    feets_data["p41"] = phaser(feets_data.phi_4 - 4*feets_data.phi_1)*2*np.pi
    feets_data = feets_data.query("period <= 1")
    return feets_data

# Usamos un generador porque memory error
#def vvv_data_gen(model, file, selected_features):
#    dtype = {x:"float32" for x in selected_features}
#    dtype["filename"] = "str"
#    data_gen = pd.read_csv(file,
#                      sep=" ", chunksize=25000,
#                         usecols=["filename"]+selected_features,
#                           dtype=dtype)
#    vvv_fnl = pd.read_csv("vvv_noaliases.fnl")
#    for data in data_gen:
#        data = data.replace([np.inf, -np.inf], np.nan).dropna()
#        no_alias_filter = data.filename.isin(vvv_fnl.filename)
#        period_filter = data.period <= 1
#        data = data[period_filter & no_alias_filter]
#
#        predict_proba = model.predict_proba(data[selected_features])
#        y_pred = predict_proba.idxmax(axis=1)
#        y_prob = predict_proba.max(axis=1)
#        y_classification = pd.DataFrame({"y_pred":y_pred, "y_prob":y_prob})
#        y_classification = y_classification.set_index([data.index])
#        data["y_pred"] = y_classification["y_pred"]
#        data["label"] = y_classification["y_pred"]
#        data["y_prob"] = y_classification["y_prob"]
#        yield data

def classify(model, file, selected_features):
    data = pd.read_csv(file, sep=" ")
    #vvv_fnl = pd.read_csv(NOALIASES_FILE, sep=" ")
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    #no_alias_filter = data.filename.isin(vvv_fnl.filename)
    period_filter = data.period <= 1
    #data = data[period_filter & no_alias_filter]
    data = data[period_filter]   

    #phaser = lambda mjd: (mjd/(2*np.pi))%1.
    #data["a21"] = np.abs(data.a2 / data.a1)
    #data["a31"] = np.abs(data.a3 / data.a1)
    #data["a41"] = np.abs(data.a4 / data.a1)
    #data["p21"] = phaser(data.phi_2 - 2*data.phi_1)*2*np.pi
    #data["p31"] = phaser(data.phi_3 - 3*data.phi_1)*2*np.pi
    #data["p41"] = phaser(data.phi_4 - 4*data.phi_1)*2*np.pi

    predict_proba = model.predict_proba(data[selected_features])
    y_pred = predict_proba.idxmax(axis=1)
    y_prob = predict_proba.max(axis=1)
    y_classification = pd.DataFrame({"y_pred":y_pred, "y_prob":y_prob})
    y_classification = y_classification.set_index([data.index])
    data["y_pred"] = y_classification["y_pred"]
    data["label"] = y_classification["y_pred"]
    data["y_prob"] = y_classification["y_prob"]
    return data


if __name__=="__main__":
    # Entrenamos un modelo
    feets_data = import_tset(TRAINING_FILE)
    feets_Y, feets_X = feets_data.iloc[:,1], feets_data.iloc[:,2:]
    selected_features = [
            'A1A2_ratio',
            'AC_std',
            'AD',
#                     'Amplitude',
#                     'AndersonDarling',
#                     'Autocor_length',
                    'Beyond1Std',
#                     'CAR_mean',
#                     'CAR_sigma',
#                     'CAR_tau',
#                     'Con',
#                     'Eta_e',
#                     'FluxPercentileRatioMid20',
#                     'FluxPercentileRatioMid35',
#                     'FluxPercentileRatioMid50',
#                     'FluxPercentileRatioMid65',
#                     'FluxPercentileRatioMid80',
#                     'Freq1_harmonics_amplitude_0',
#                     'Freq1_harmonics_amplitude_1',
#                     'Freq1_harmonics_amplitude_2',
#                     'Freq1_harmonics_amplitude_3',
#                     'Freq1_harmonics_rel_phase_0',
#                     'Freq1_harmonics_rel_phase_1',
#                     'Freq1_harmonics_rel_phase_2',
#                     'Freq1_harmonics_rel_phase_3',
#                     'Freq2_harmonics_amplitude_0',
#                     'Freq2_harmonics_amplitude_1',
#                     'Freq2_harmonics_amplitude_2',
#                     'Freq2_harmonics_amplitude_3',
#                     'Freq2_harmonics_rel_phase_0',
#                     'Freq2_harmonics_rel_phase_1',
#                     'Freq2_harmonics_rel_phase_2',
#                     'Freq2_harmonics_rel_phase_3',
#                     'Freq3_harmonics_amplitude_0',
#                     'Freq3_harmonics_amplitude_1',
#                     'Freq3_harmonics_amplitude_2',
#                     'Freq3_harmonics_amplitude_3',
#                     'Freq3_harmonics_rel_phase_0',
#                     'Freq3_harmonics_rel_phase_1',
#                     'Freq3_harmonics_rel_phase_2',
#                     'Freq3_harmonics_rel_phase_3',
            'GP_DownRatio',
            'GP_RiseDownRatio',
            'GP_RiseRatio',
            'GP_Skew',
#                     'Gskew',
#                     'LinearTrend',
#                     'MaxSlope',
#                     'Mean',
#                     'Meanvariance',
#                     'MedianAbsDev',
#                     'MedianBRP',
#             'MseTemplate',
#                     'PairSlopeTrend',
#                     'PercentAmplitude',
#                     'PercentDifferenceFluxPercentile',
#                     'PeriodLS',
#                     'Period_fit',
#                     'Psi_CS',
#                     'Psi_eta',
#                     'Q31',
#             'R2Template',
            'Rcs',
#                     'Skew',
#                     'SlottedA_length',
#                     'SmallKurtosis',
#                     'Std',
#                     'StetsonK',
#                     'StetsonK_AC',
#                     'StructureFunction_index_21',
#                     'StructureFunction_index_31',
#                     'StructureFunction_index_32',
            'Tm',
#             'a0',
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
#             'mediana',
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
             'period',
             'a21',
             'a31',
             'a41',
             'p21',
             'p31',
             'p41',
            ]
    model = SingleProbRF(tresh = 0.0)
    model.MODEL_PARAMS["n_jobs"] = NUM_PROC
    model.fit(feets_X[selected_features], feets_Y)
    # CLASIFICAMOS
#    vvv_result = pd.concat([*vvv_data_gen(model, SAMPLE_FILE, selected_features)])

    vvv_result = classify(model, SAMPLE_FILE, selected_features)
    vvv_result.to_csv(OUTPUT_FILE, sep=" ", index=False)
