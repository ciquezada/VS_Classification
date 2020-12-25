## PARAMETERS

FitGP_gamma = 0.1
FitFourier_gamma = 0.1
# Extractor feature dependence
gp_dependent_features = ["RiseRatio", "DownRatio",
                         "RiseDownRatio", "Tm"]
template_dependent_features = ["R2Template", "MseTemplate",
                               "A1A2ratio"]
# braga_template_rrab_dependent_features = ["R2BragaTemplateRRab", "MseBragaTemplateRRab"]
# braga_template_rrc_dependent_features = ["R2BragaTemplateRRc", "MseBragaTemplateRRc"]
braga_template_dependent_features = ["R2BragaTemplateRRab", "MseBragaTemplateRRab",
                                        "R2BragaTemplateRRc", "MseBragaTemplateRRc"]
fcomponents_dependent_features = ['a0', 'a1', 'a2', 'a3',
                                  'a4', 'a5', 'a6', 'a7',
                                  'phi_1', 'phi_2', 'phi_3',
                                  'phi_4', 'phi_5', 'phi_6',
                                  'phi_7', 'a21', 'a31', 'a41',
                                  'p21', 'p31', 'p41']
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
         # 'MseBragaTemplate',
         # 'R2BragaTemplate',
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
                                 'p41',
                                 'MseBragaTemplateRRc'
                                    ]

# onlybraga features preset
selected_features["onlybraga"] = [
                                'MseBragaTemplateRRab',
                                'R2BragaTemplateRRab',
                                'MseBragaTemplateRRc',
                                'R2BragaTemplateRRc',
                                    ]
