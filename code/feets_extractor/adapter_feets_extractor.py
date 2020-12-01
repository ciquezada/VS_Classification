from ext_fit_fourier import FitFourier
from ext_fit_gp import FitGP
from ext_fit_template import FitTemplate
from ext_inter_percentile_range import InterPercentileRanges
from ext_magnitude_distribution import MagnitudeDistribution
from ext_scipy_anderson_darling import SciPyAndersonDarling
from ext_stats_model_tsa import StatsmodelTSA
from ext_fit_braga_template import FitBragaTemplate
import feets
import numpy as np
import pandas as pd
import sys
import os
import parameters_feets_extractor as P


'''
Adapter of feets routines by Cabral (search reference) to work with
VS_Classification files and pipelines.
Extract features from the curves in the input curve file and return a
features Dataframe file.
    Args:
        input_file: path to Curves DataFrame file ["vvv", "period", "ks_path"]
                                ("vvv":curve_id, "ks_path": ks curve file path)
        output_file: path to output features Datafreme
        features_preset: name of the features set selection (see in parameters_feets_extractor.py)

    Raises:
        None

    Returns:
        curves_features (DataFrame): ["filename", "period", ...(features)]
    '''

feets.register_extractor(InterPercentileRanges)
feets.register_extractor(SciPyAndersonDarling)
feets.register_extractor(MagnitudeDistribution)
feets.register_extractor(StatsmodelTSA)
feets.register_extractor(FitGP)
feets.register_extractor(FitTemplate)
feets.register_extractor(FitFourier)
feets.register_extractor(FitBragaTemplate)

def drop_err(star_data):
    emed = star_data.emag.median()
    esig = star_data.emag.std()
    e95 = min(np.percentile(star_data.emag.values, [95])[0], emed+2.5*esig)
    return star_data.query("emag < {}".format(e95))

def get_feets_extra_params(selected_features, curve_period):
    params = {}
    if not set(selected_features).isdisjoint(P.gp_dependent_features):
        params["FitGP"] = {"period": curve_period, "gamma": P.FitGP_gamma}
    if not set(selected_features).isdisjoint(P.template_dependent_features):
        params["FitTemplate"] = {"period": curve_period}
    if not set(selected_features).isdisjoint(P.braga_template_dependent_features):
        params["FitBragaTemplate"] = {"period": curve_period}
    if not set(selected_features).isdisjoint(P.fcomponents_dependent_features):
        params["FitFourier"] = {"period": curve_period, "gamma": P.FitFourier_gamma}
    return params

def extract_curve_features(curve_data, selected_features):
    curve_id, curve_period = curve_data.vvv, curve_data.period
    curve_ks_path = curve_data.ks_path
    ks_star_data = pd.read_csv(curve_ks_path,
                                names=["mjd", "mag", "emag"],
                                        delim_whitespace=True)
    ks_star_data = drop_err(ks_star_data)
    params = get_feets_extra_params(selected_features, curve_period)
    fs = feets.FeatureSpace(data=["time", "magnitude", "error"],
                        only=selected_features,
                        **params
                       )
    extracted_features = fs.extract(time=ks_star_data.mjd,
                                    magnitude=ks_star_data.mag,
                                    error=ks_star_data.emag)
    features_dict = dict(zip(*extracted_features))
    features_dict["filename"] = curve_id
    features_dict["period"] = curve_period
    if "label" in curve_data:
        features_dict["label"] = curve_data.label
    # extr = list(pd.DataFrame([extr])[selected_features].values[0])
    return features_dict

def extract_features(curves_data, selected_features):
    features = []
    for i, row in curves_data.iterrows():
        if not os.path.exists(row["ks_path"]):
            print("The curve dont exists: {}".format(row["vvv"]))
            continue
        features.append(
                        extract_curve_features(row, selected_features)
                        )
    extractor_output = pd.DataFrame(features)
    if "label" in curves_data:
        curve_info = ["filename", "label", "period"] + selected_features
    else:
        curve_info = ["filename", "period"] + selected_features
    return extractor_output[curve_info]

if __name__=="__main__":
    # user input
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    features_preset = sys.argv[3]
    # load curve file and save features
    curves_data = pd.read_csv(input_file, sep=" ")
    curves_features = extract_features(curves_data,
                                        P.selected_features[features_preset])
    curves_features.to_csv(output_file, sep=" ", index=False)
