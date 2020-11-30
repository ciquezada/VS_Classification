from pprint import pprint
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import parameters_classifier as P
import pandas as pd
import numpy as np
import sys


def save_params(file_path, params):
    new_model = RandomForestClassifier(**params)
    pprint(new_model.get_params())
    with open(file_path, "a") as fout:
        pprint(new_model.get_params(), stream=fout)
    return 0

def starter_params(config_preset):
    # Random parameters
    return P.random_grid[config_preset]

def first_search(X, Y, NUM_PROC, config_preset):
    random_grid = starter_params(config_preset)
    ### SOLO PARA TEST ###
    if config_preset=="test":
        n_iter = 2
        cv = 2
        random_grid["max_features"] = list(range(3,6))
    else:
        n_iter = 75
        cv = 10
    ############################
    model = RandomForestClassifier(n_estimators=200)
    model_random = RandomizedSearchCV(estimator=model,
                                        param_distributions=random_grid,
                                            n_iter=n_iter, cv=cv, verbose=2,
                                                random_state=42,
                                                    n_jobs=NUM_PROC)
    model_random.fit(X, Y)
    best_params = model_random.best_params_
    return best_params

def second_params(best_params):
    # Random parameters
    if type(best_params['max_features'])==str:
        max_features = [best_params['max_features']]
    else:
        max_features = [x for x in range(best_params['max_features']-1,
                                                best_params['max_features']+1)]
    max_depth = [x for x in range(best_params['max_depth']-2,
                                                best_params['max_depth']+2)]
    min_samples_split = np.random.normal(best_params['min_samples_split'],
                                        best_params['min_samples_split']/10, 5)
    min_samples_leaf = np.random.normal(best_params['min_samples_leaf'],
                                        best_params['min_samples_leaf']/10, 5)
    # Create the random grid
    params_grid = {'max_features': max_features,
                   'max_depth': max_depth,
                   'min_samples_split': min_samples_split,
                   'min_samples_leaf': min_samples_leaf}
    return params_grid

def second_search(X, Y, NUM_PROC, best_params, config_preset):
    params_grid = second_params(best_params)
    ### SOLO PARA TEST ###
    if config_preset=="test":
        cv = 2
        params_grid = {'max_features': list(range(3,6))}
    else:
        cv = 10
    #######################
    model = RandomForestClassifier(n_estimators=200,
                                    class_weight=best_params["class_weight"])
    grid_search = GridSearchCV(estimator=model, param_grid=params_grid,
                                    cv=cv, n_jobs=NUM_PROC, verbose=2)
    grid_search.fit(X, Y)
    best_params_2 = grid_search.best_params_
    return best_params_2

if __name__=="__main__":
    # USER INPUT
    NUM_PROC = int(sys.argv[1])
    TRAINING_FILE = sys.argv[2]
    OUTPUT_FILE = sys.argv[3]
    config_preset = sys.argv[4]
    SELECTED_FEATURES = P.selected_features[config_preset]
    # Load training feets
    feets_data = pd.read_csv(TRAINING_FILE, sep=" ")
    feets_data = feets_data.replace([np.inf, -np.inf], np.nan)
    feets_data = feets_data.dropna()
    feets_Y = feets_data.label
    feets_X = feets_data[SELECTED_FEATURES]
    # First search
    best_params = first_search(feets_X, feets_Y, NUM_PROC, config_preset)
    best_params["n_estimators"] = 20000
    best_params["n_jobs"] = NUM_PROC
    best_params["bootstrap"] = True
    # Save first Params
    save_params(OUTPUT_FILE, best_params)
    # Second search
    best_params_2 = second_search(feets_X, feets_Y, NUM_PROC, best_params, config_preset)
    best_params_2["class_weight"] = best_params["class_weight"]
    best_params_2["n_estimators"] = 20000
    best_params_2["n_jobs"] = NUM_PROC
    best_params_2["bootstrap"] = True
    # Save second Params
    save_params(OUTPUT_FILE, best_params_2)
