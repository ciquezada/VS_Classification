import numpy as np
import pandas as pd
import sys
import os
from stardata_normalizer import normalize
from hog_extractor import HogExtractor


'''
HOG extractor
    Args:
        input_file: path to Curves DataFrame file ["vvv", "period", "ks_path"]
                                ("vvv":curve_id, "ks_path": ks curve file path)
        output_file: path to output features Datafreme
        hog_preset:

    Raises:
        None

    Returns:
        curves_features (DataFrame): ["filename", "period", ...(features)]
    '''

def drop_err(star_data):
    emed = star_data.emag.median()
    esig = star_data.emag.std()
    e95 = min(np.percentile(star_data.emag.values, [95])[0], emed+2.5*esig)
    return star_data.query("emag < {}".format(e95))

def extract_curve_features(curve_data, hog_preset):
    curve_id, curve_period = curve_data.vvv, curve_data.period
    curve_ks_path = curve_data.ks_path
    ks_star_data = pd.read_csv(curve_ks_path,
                                names=["mjd", "mag", "emag"],
                                        delim_whitespace=True)
    ks_star_data = drop_err(ks_star_data)
    ks_star_data = normalize(ks_star_data.mjd, ks_star_data.mag,
                                        ks_star_data.emag, curve_period)

    hog_extractor = HogExtractor() #poner aqui hog_preset
    extracted_features = hog_extractor.extract(time=ks_star_data.mjd,
                                                magnitude=ks_star_data.mag,
                                                error=ks_star_data.emag,
                                                period=curve_period)
    features_dict = extracted_features
    features_dict["filename"] = curve_id
    if "label" in curve_data:
        features_dict["label"] = curve_data.label
    features_dict["period"] = curve_period
    return features_dict

def extract_features(curves_data, hog_preset):
    features = []
    for i, row in curves_data.iterrows():
        if not os.path.exists(row["ks_path"]):
            print("The curve dont exists: {}".format(row["vvv"]))
            continue
        features.append(extract_curve_features(row, hog_preset))
    head_features = ["filename", "period"]
    if "label" in row:
        head_features += ["label"]
    extractor_output = pd.DataFrame(features)[
                                    head_features+[f"{x}" for x in range(3780)]
                                                ]
    return extractor_output

if __name__=="__main__":
    # user input
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    hog_preset = sys.argv[3]
    # load curve file and save features
    curves_data = pd.read_csv(input_file, sep=" ")
    curves_features = extract_features(curves_data, hog_preset)
    curves_features.to_csv(output_file, sep=" ", index=False)
