import numpy as np


## PARAMETERS

# Classifier
threshold = 0.0

# Features selection
selected_features = {}
# RRlyr features preset
selected_features["rrlyr"] = [
                                'A1A2_ratio',
                                'AC_std',
                                'AD',
                                   	# 'Amplitude',
                                   	# 'AndersonDarling',
                                   	# 'Autocor_length',
                                    'Beyond1Std',
                                   	# 'CAR_mean',
                                   	# 'CAR_sigma',
                                   	# 'CAR_tau',
                                   	# 'Con',
                                   	# 'Eta_e',
                                   	# 'FluxPercentileRatioMid20',
                                   	# 'FluxPercentileRatioMid35',
                                   	# 'FluxPercentileRatioMid50',
                                   	# 'FluxPercentileRatioMid65',
                                   	# 'FluxPercentileRatioMid80',
                                   	# 'Freq1_harmonics_amplitude_0',
                                   	# 'Freq1_harmonics_amplitude_1',
                                   	# 'Freq1_harmonics_amplitude_2',
                                   	# 'Freq1_harmonics_amplitude_3',
                                   	# 'Freq1_harmonics_rel_phase_0',
                                   	# 'Freq1_harmonics_rel_phase_1',
                                   	# 'Freq1_harmonics_rel_phase_2',
                                   	# 'Freq1_harmonics_rel_phase_3',
                                   	# 'Freq2_harmonics_amplitude_0',
                                   	# 'Freq2_harmonics_amplitude_1',
                                   	# 'Freq2_harmonics_amplitude_2',
                                   	# 'Freq2_harmonics_amplitude_3',
                                   	# 'Freq2_harmonics_rel_phase_0',
                                   	# 'Freq2_harmonics_rel_phase_1',
                                   	# 'Freq2_harmonics_rel_phase_2',
                                   	# 'Freq2_harmonics_rel_phase_3',
                                   	# 'Freq3_harmonics_amplitude_0',
                                   	# 'Freq3_harmonics_amplitude_1',
                                   	# 'Freq3_harmonics_amplitude_2',
                                   	# 'Freq3_harmonics_amplitude_3',
                                   	# 'Freq3_harmonics_rel_phase_0',
                                   	# 'Freq3_harmonics_rel_phase_1',
                                   	# 'Freq3_harmonics_rel_phase_2',
                                   	# 'Freq3_harmonics_rel_phase_3',
                                'GP_DownRatio',
                                'GP_RiseDownRatio',
                                'GP_RiseRatio',
                                'GP_Skew',
                                   	# 'Gskew',
                                   	# 'LinearTrend',
                                   	# 'MaxSlope',
                                   	# 'Mean',
                                   	# 'Meanvariance',
                                   	# 'MedianAbsDev',
                                   	# 'MedianBRP',
                               # 'MseTemplate',
                                   	# 'PairSlopeTrend',
                                   	# 'PercentAmplitude',
                                   	# 'PercentDifferenceFluxPercentile',
                                   	# 'PeriodLS',
                                   	# 'Period_fit',
                                   	# 'Psi_CS',
                                   	# 'Psi_eta',
                                   	# 'Q31',
                               # 'R2Template',
                                'Rcs',
                                   	# 'Skew',
                                   	# 'SlottedA_length',
                                   	# 'SmallKurtosis',
                                   	# 'Std',
                                   	# 'StetsonK',
                                   	# 'StetsonK_AC',
                                   	# 'StructureFunction_index_21',
                                   	# 'StructureFunction_index_31',
                                   	# 'StructureFunction_index_32',
                                 'Tm',
                                 # 'a0',
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
                                 # 'mediana',
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
                                 # 'Beyond3Std',
                                 # 'Beyond5Std',
                                 'a21',
                                 'a31',
                                 'a41',
                                 'p21',
                                 'p31',
                                 'p41',
                                    ]

# Default features preset
selected_features["default"] = [
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
                                 'period',
                                 'Beyond3Std',
                                 'Beyond5Std',
                                 'a21',
                                 'a31',
                                 'a41',
                                 'p21',
                                 'p31',
                                 'p41',
                                    ]

# Test features preset
selected_features["test"] = [
                                'AD',
                                    'Amplitude',
                                'GP_RiseDownRatio',
                                'R2Template',
                                 'iqr',
                                 'period',
                                 'p41',
                                    ]

# Test features preset
selected_features["aliases"] = [
                                'A1A2_ratio',
                                'AC_std',
                                'AD',
                                   	# 'Amplitude',
                                   	# 'AndersonDarling',
                                   	# 'Autocor_length',
                                    'Beyond1Std',
                                   	# 'CAR_mean',
                                   	# 'CAR_sigma',
                                   	# 'CAR_tau',
                                   	# 'Con',
                                   	# 'Eta_e',
                                   	# 'FluxPercentileRatioMid20',
                                   	# 'FluxPercentileRatioMid35',
                                   	# 'FluxPercentileRatioMid50',
                                   	# 'FluxPercentileRatioMid65',
                                   	# 'FluxPercentileRatioMid80',
                                   	# 'Freq1_harmonics_amplitude_0',
                                   	# 'Freq1_harmonics_amplitude_1',
                                   	# 'Freq1_harmonics_amplitude_2',
                                   	# 'Freq1_harmonics_amplitude_3',
                                   	# 'Freq1_harmonics_rel_phase_0',
                                   	# 'Freq1_harmonics_rel_phase_1',
                                   	# 'Freq1_harmonics_rel_phase_2',
                                   	# 'Freq1_harmonics_rel_phase_3',
                                   	# 'Freq2_harmonics_amplitude_0',
                                   	# 'Freq2_harmonics_amplitude_1',
                                   	# 'Freq2_harmonics_amplitude_2',
                                   	# 'Freq2_harmonics_amplitude_3',
                                   	# 'Freq2_harmonics_rel_phase_0',
                                   	# 'Freq2_harmonics_rel_phase_1',
                                   	# 'Freq2_harmonics_rel_phase_2',
                                   	# 'Freq2_harmonics_rel_phase_3',
                                   	# 'Freq3_harmonics_amplitude_0',
                                   	# 'Freq3_harmonics_amplitude_1',
                                   	# 'Freq3_harmonics_amplitude_2',
                                   	# 'Freq3_harmonics_amplitude_3',
                                   	# 'Freq3_harmonics_rel_phase_0',
                                   	# 'Freq3_harmonics_rel_phase_1',
                                   	# 'Freq3_harmonics_rel_phase_2',
                                   	# 'Freq3_harmonics_rel_phase_3',
                                'GP_DownRatio',
                                'GP_RiseDownRatio',
                                'GP_RiseRatio',
                                'GP_Skew',
                                   	# 'Gskew',
                                   	# 'LinearTrend',
                                   	# 'MaxSlope',
                                   	# 'Mean',
                                   	# 'Meanvariance',
                                   	# 'MedianAbsDev',
                                   	# 'MedianBRP',
                               # 'MseTemplate',
                                   	# 'PairSlopeTrend',
                                   	# 'PercentAmplitude',
                                   	# 'PercentDifferenceFluxPercentile',
                                   	# 'PeriodLS',
                                   	# 'Period_fit',
                                   	# 'Psi_CS',
                                   	# 'Psi_eta',
                                   	# 'Q31',
                               # 'R2Template',
                                'Rcs',
                                   	# 'Skew',
                                   	# 'SlottedA_length',
                                   	# 'SmallKurtosis',
                                   	# 'Std',
                                   	# 'StetsonK',
                                   	# 'StetsonK_AC',
                                   	# 'StructureFunction_index_21',
                                   	# 'StructureFunction_index_31',
                                   	# 'StructureFunction_index_32',
                                 'Tm',
                                 # 'a0',
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
                                 # 'mediana',
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
                                 # 'period',
                                 # 'Beyond3Std',
                                 # 'Beyond5Std',
                                 'a21',
                                 'a31',
                                 'a41',
                                 'p21',
                                 'p31',
                                 'p41',
                                    ]

# HOGS
selected_features["hogs"] = ["period"]+[f"{x}" for x in range(3780)]

# HOGS+FEATURES
selected_features["hogs+rrlyr"] = ["period"]+[f"{x}" for x in range(3780)]

# Hyperparameters selection
model_parameters = {}
# RR Lyr model parameters preset
model_parameters["rrlyr"] = {'bootstrap': True,
                                 'ccp_alpha': 0.0,
                                 'criterion': 'gini',
                                 'max_depth': 78.76327201157883,
                                 'max_features': "auto",
                                 'max_leaf_nodes': None,
                                 'max_samples': None,
                                 'min_impurity_decrease': 0.0,
                                 'min_impurity_split': None,
                                 'min_samples_leaf': 0.0008813199066153201,
                                 'min_samples_split': 0.007490673261301018,
                                 'min_weight_fraction_leaf': 0.0,
                                 'n_estimators': 20000,
                                 'n_jobs': 60,
                                 'oob_score': True,
                                 'random_state': None,
                                 'verbose': 0,
                                 'warm_start': False}
# default model parameters preset
model_parameters["default"] = {'bootstrap': True,
                                 'ccp_alpha': 0.0,
                                 'criterion': 'gini',
                                 'max_depth': 78.76327201157883,
                                 'max_features': "auto",
                                 'max_leaf_nodes': None,
                                 'max_samples': None,
                                 'min_impurity_decrease': 0.0,
                                 'min_impurity_split': None,
                                 'min_samples_leaf': 0.0008813199066153201,
                                 'min_samples_split': 0.007490673261301018,
                                 'min_weight_fraction_leaf': 0.0,
                                 'n_estimators': 150,
                                 'n_jobs': 60,
                                 'oob_score': True,
                                 'random_state': None,
                                 'verbose': 0,
                                 'warm_start': False}

# RR Lyr model parameters preset
model_parameters["aliases"] = {'bootstrap': True,
                                 'ccp_alpha': 0.0,
                                 'criterion': 'gini',
                                 'max_depth': 78.76327201157883,
                                 'max_features': "auto",
                                 'max_leaf_nodes': None,
                                 'max_samples': None,
                                 'min_impurity_decrease': 0.0,
                                 'min_impurity_split': None,
                                 'min_samples_leaf': 0.0008813199066153201,
                                 'min_samples_split': 0.007490673261301018,
                                 'min_weight_fraction_leaf': 0.0,
                                 'n_estimators': 20000,
                                 'n_jobs': 60,
                                 'oob_score': True,
                                 'random_state': None,
                                 'verbose': 0,
                                 'warm_start': False}

# test model parameters preset
model_parameters["test"] = {'bootstrap': True,
                                 'ccp_alpha': 0.0,
                                 'criterion': 'gini',
                                 'max_depth': 15,
                                 'max_features': "auto",
                                 'max_leaf_nodes': None,
                                 'max_samples': None,
                                 'min_impurity_decrease': 0.0,
                                 'min_impurity_split': None,
                                 'min_samples_leaf': 0.001,
                                 'min_samples_split': 0.01,
                                 'min_weight_fraction_leaf': 0.0,
                                 'n_estimators': 50,
                                 'n_jobs': 60,
                                 'oob_score': True,
                                 'random_state': None,
                                 'verbose': 0,
                                 'warm_start': False}

# test model parameters preset
model_parameters["hogs"] = {'bootstrap': True,
                                 'ccp_alpha': 0.0,
                                 'class_weight': 'balanced_subsample',
                                 'criterion': 'gini',
                                 'max_depth': 42,
                                 'max_features': "sqrt",
                                 'max_leaf_nodes': None,
                                 'max_samples': None,
                                 'min_impurity_decrease': 0.0,
                                 'min_impurity_split': None,
                                 'min_samples_leaf': 0.0001,
                                 'min_samples_split': 0.0004537931034482759,
                                 'min_weight_fraction_leaf': 0.0,
                                 'n_estimators': 2000,
                                 'n_jobs': 60,
                                 'oob_score': True,
                                 'random_state': None,
                                 'verbose': 0,
                                 'warm_start': False}

# hogs model parameters preset
model_parameters["hogs+rrlyr"] = {'bootstrap': True,
                                 'ccp_alpha': 0.0,
                                 'class_weight': 'balanced_subsample',
                                 'criterion': 'gini',
                                 'max_depth': 20,
                                 'max_features': "sqrt",
                                 'max_leaf_nodes': None,
                                 'max_samples': None,
                                 'min_impurity_decrease': 0.0,
                                 'min_impurity_split': None,
                                 'min_samples_leaf': 0.0001,
                                 'min_samples_split': 0.0005,
                                 'min_weight_fraction_leaf': 0.0,
                                 'n_estimators': 200,
                                 'n_jobs': 60,
                                 'oob_score': True,
                                 'random_state': None,
                                 'verbose': 0,
                                 'warm_start': False}

# Search parameters
random_grid = {}

## RRLyr
max_features = [x for x in range(10,20)]
max_depth = [x for x in range(60,75)]
min_samples_split = list(np.linspace(0.00001, 0.0001, 30))
min_samples_leaf = list(np.linspace(0.0001, 0.001, 30))
class_weight = ["balanced", "balanced_subsample"]
# Create the random grid
random_grid["rrlyr"] = {'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               "class_weight": class_weight}

## Test
max_features = [x for x in range(10,20)]
max_depth = [x for x in range(10,12)]
min_samples_split = list(np.linspace(0.001, 0.01, 30))
min_samples_leaf = list(np.linspace(0.01, 0.1, 30))
class_weight = ["balanced", "balanced_subsample"]
# Create the random grid
random_grid["test"] = {'max_features': max_features,
                           'max_depth': max_depth,
                           'min_samples_split': min_samples_split,
                           'min_samples_leaf': min_samples_leaf,
                           "class_weight": class_weight}

## HOGS
max_features = ["sqrt"]
max_depth = [x for x in range(10,75)]
min_samples_split = list(np.linspace(0.00001, 0.001, 30))
min_samples_leaf = list(np.linspace(0.00001, 0.001, 30))
class_weight = ["balanced", "balanced_subsample", None]
# Create the random grid
random_grid["hogs"] = {'max_features': max_features,
                       'max_depth': max_depth,
                       'min_samples_split': min_samples_split,
                       'min_samples_leaf': min_samples_leaf,
                       "class_weight": class_weight}

## HOGS + RRLYR
max_features = ["sqrt"]
max_depth = [x for x in range(10,75)]
min_samples_split = list(np.linspace(0.00001, 0.001, 30))
min_samples_leaf = list(np.linspace(0.00001, 0.001, 30))
class_weight = ["balanced", "balanced_subsample", None]
# Create the random grid
random_grid["hogs+rrlyr"] = {'max_features': max_features,
                       'max_depth': max_depth,
                       'min_samples_split': min_samples_split,
                       'min_samples_leaf': min_samples_leaf,
                       "class_weight": class_weight}
