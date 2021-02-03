from classifier import SingleProbRF
import parameters_classifier as P
import pandas as pd
import numpy as np
import sys
import os


def classify(model, data, selected_features):
    predict_proba = model.predict_proba(data[selected_features]).set_index([data.index])
    y_pred = predict_proba.idxmax(axis=1)
    y_prob = predict_proba.max(axis=1)
    y_classification = data[["filename"]].copy()
    y_classification["pred"] = y_pred
    y_classification["prob"] = y_prob
    y_classification = pd.concat([y_classification, predict_proba], axis=1)
    return y_classification

if __name__=="__main__":
    # USER INPUT
    NUM_PROC = int(sys.argv[1]) #numero dep rocesos
    TRAINING_FILE = sys.argv[2] #vvv_tset_features.csv
    DATA_FILE = sys.argv[3] #vvv_all_features.csv
    OUTPUT_FILE = sys.argv[4] #vvv_results.csv
    if len(sys.argv)>5:
        config_preset = sys.argv[5]
    else:
        config_preset = "default"
    SELECTED_FEATURES = P.selected_features[config_preset]
    MODEL_PARAMS = P.model_parameters[config_preset]

    # Load training set
    feets_data = pd.read_csv(TRAINING_FILE, sep=" ")
    feets_data = feets_data.replace([np.inf, -np.inf], np.nan)
    feets_data = feets_data.dropna()
    feets_Y = feets_data.label
    feets_X = feets_data[SELECTED_FEATURES]
    # Model training
    model = SingleProbRF(thresh = P.threshold)
    model.MODEL_PARAMS.update(MODEL_PARAMS)
    model.MODEL_PARAMS["n_jobs"] = NUM_PROC
    model.fit(feets_X, feets_Y)
    # Load data features
    data_features = pd.read_csv(DATA_FILE, sep=" ")
    data_features = data_features.replace([np.inf, -np.inf], np.nan).dropna()

    # Classify data
    classification_result = classify(model, data_features, SELECTED_FEATURES)
    classification_result.to_csv(OUTPUT_FILE, sep=" ", index=False)
