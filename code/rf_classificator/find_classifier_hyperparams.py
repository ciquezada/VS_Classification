from pprint import pprint
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np


NUM_PROC = int(sys.argv[1])
TRAINING_FILE = sys.argv[2]
OUTPUT_DIR = sys.argv[3]



# Load training feets
feets_data = pd.read_csv(TRAINING_FILE, sep=" ")
feets_data = feets_data.replace([np.inf, -np.inf], np.nan)
feets_data = feets_data.dropna()
feets_Y = feets_data.label
feets_X = feets_data[SELECTED_FEATURES]


# Number of trees in random forest
n_estimators = [225, 250, 275]
max_features = [x for x in range(10,20)]
max_depth = [x for x in range(60,75)]
min_samples_split = list(np.linspace(0.0001, 0.001, 10))
min_samples_leaf = [0.001029069612159517]

# Method of selecting samples for training each tree
bootstrap = [True]
#class_weight
class_weight = ["balanced", "balanced_subsample"]
# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap,
              "class_weight": class_weight}


model = RandomForestClassifier()
model_random = RandomizedSearchCV(estimator = model, param_distributions = random_grid, n_iter = 40, cv = 10,
                                                  verbose=2, random_state=42, n_jobs = NUM_PROC)

        model_random.fit(X, Y)

best_params = model_random.best_params_
best_params["n_jobs"] = NUM_PROC
best_params["bootstrap"] = True

new_model = RandomForestClassifier(**best_params)
pprint(new_model.get_params())
with open("file_out_1.txt", "w") as fout:
    pprint(new_model.get_params(), stream=fout)

param_grid = {'bootstrap': [True],
             'class_weight': class_weight,
             'max_depth': np.random.normal(best_params["max_depth"], best_params["max_depth"]/10, 5),
             'min_samples_leaf': np.random.normal(best_params['min_samples_leaf'], best_params['min_samples_leaf']/10, 5),
             'min_samples_split': np.random.normal(best_params['min_samples_split'], best_params['min_samples_split']/10, 5),
             'n_estimators': [best_params['n_estimators']-1, best_params['n_estimators']-2,
                                 best_params['n_estimators']-1, best_params['n_estimators'],
                                         best_params['n_estimators']+1, best_params['n_estimators']+2],
             'n_jobs': [NUM_PROC],}

grid_search = GridSearchCV(estimator = model, param_grid = param_grid,
                          cv = 3, n_jobs = NUM_PROC, verbose = 2)
grid_search.fit(X, Y)

best_params_2 = grid_search.best_params_
best_params_2["class_weight"] = {"RRab": RRab_w, "RRc": RRc_w,"ECL c": ECL_c_w, "ECL nc": ECL_nc_w, "ELL": ELL_w}

new_model_2 = RandomForestClassifier(**best_params_2)
pprint(new_model_2.get_params())

with open("best_param.txt", "wt") as fil:
    pprint(new_model_2.get_params(), stream = fil)
