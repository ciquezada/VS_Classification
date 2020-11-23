import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

class SingleProbRF():
    MODEL_PARAMS = {'bootstrap': True,
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


    def __init__(self, thresh = 0.0):
        self.rf = None
        self.thresh = thresh

    def fit(self, X, Y):
        model_params = self.MODEL_PARAMS

        classes = np.unique(Y)
        model_params["class_weight"] = { cl:Y[Y == classes[0]].count()/Y[Y == cl].count() for cl in classes  }


        self.rf = RandomForestClassifier(**model_params)
        self.rf.fit(X, Y)

    def predict(self, x_data):

        model = self.rf
        pred_union = pd.DataFrame(model.predict_proba(x_data), columns=[x for x in model.classes_])

        pred_df = pd.DataFrame([],columns = ["label", "prob"])
        pred_df["label"] = pred_union.idxmax(axis=1)
        pred_df["prob"] = pred_union.max(axis=1)
        df_out = pred_df.apply(lambda row: row.label if row.prob >= self.thresh else "low_prob", axis = 1)
        return df_out

    def predict_proba(self, x_data):
        model = self.rf
        pred_union = pd.DataFrame(model.predict_proba(x_data), columns=[x for x in model.classes_])
        return pred_union
