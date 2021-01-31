import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools as it
import os
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn import metrics
from classifier import SingleProbRF
import pprint
import sys
import parameters_classifier as P


def custom_plot_confusion_matrix(cm,
                          classes,
                          normalize=True,
                          title = 'Confusion matrix', sub_title = "",
                          cmap=plt.cm.Greens, *args, **kwargs):

    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    title = title + "\n" + sub_title

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
#     plt.title(title)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=16)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45, fontsize = 15)
    plt.yticks(tick_marks, classes, fontsize = 15)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2
    for i, j in it.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, "{}".format(format(cm[i, j], fmt)),
                 fontsize = 15,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('Clase original', size = 17)
    plt.xlabel('Predicción', size = 17)
    plt.tight_layout()

def get_confusion_matrix(y_true, y_pred, labels):
    cnf_matrix_train = confusion_matrix(y_true, y_pred, labels = labels)
    cnf_matrix_train = cnf_matrix_train.astype('float') / cnf_matrix_train.sum(axis=1)[:, np.newaxis]
    cnf_matrix_train = cnf_matrix_train * 100
    return cnf_matrix_train

def get_cl_report(y_true, y_pred, labels):
    get_df = lambda dic: pd.DataFrame([dic.values()], columns = dic.keys())[["precision", "recall", "f1-score"]]
    cl_report = classification_report(y_true, y_pred, labels = labels, output_dict = True)
    return pd.concat([get_df(cl_report[df]) for df in labels], axis = 0, ignore_index = True)/10 * 100

def singleprob_eval_final(model, X, Y, cm_train=False, add_low_prob=False,
                                        cv = 10, output_dir=".", *args, **kwargs):
    if not os.path.exists(output_dir):
        os.system('mkdir {}'.format(output_dir))
    low_prob = []
    if add_low_prob:
        low_prob = ["low_prob"]
    labels = list(np.unique(Y)) + low_prob
    """
    nf = numero de feaaatures
    """
    kf = StratifiedShuffleSplit(n_splits=cv, test_size=0.3, random_state=1)
    kf.get_n_splits(X, Y)

    ## preparacion para la matriz ###
    cm_list = []
    cm_list_train = []
    #################################
    ## Preparacion para el classification report ####
    cl_df = 0
    cl_df_train = 0
    #################################################
    ## Preparacion Feature imnportances ##
    feature_importances = 0
    ######################################

    ## Y_PRED OUTPUT #####################
    y_pred_list = []
    ######################################

    ## ROC ###############################
    if len(labels)==2:
        roc_auc_list = []
        display_list = []
    ######################################

    for train_index, test_index in kf.split(X, Y):
        x_train, x_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = Y.iloc[train_index], Y.iloc[test_index]

        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        y_pred_train = model.predict(x_train)

        ## armamos la matriz de confusion ################
        cm_list += [get_confusion_matrix(y_test, y_pred, labels)]                #testing set
        cm_list_train += [get_confusion_matrix(y_train, y_pred_train, labels)]   #trainning set
        ##################################################

        ## armamos el clasifcaation_report ################
        cl_df += get_cl_report(y_test, y_pred, labels)
        cl_df_train += get_cl_report(y_train, y_pred_train, labels)
        ###################################################

        ## Feature importances ###########################
        feature_importances += model.rf.feature_importances_
        ##################################################
        ## Y_PRED OUTPUT #################################
        y_pred_list.append(model.predict_proba(x_test).set_index([y_test.index]))
        #################################################
        ## Y_PRED_PROBA OUTPUT #################################
        # y_pred_list[-1]["prob"] = model.predict_proba(x_test).set_index([y_test.index]).max(axis=1)
        #################################################
        ## ROC ###############################
        if len(labels)==2 and "RRab" in labels:
            fpr, tpr, thresholds = metrics.roc_curve(y_test.values, model.predict_proba(x_test).RRab.values,
                                                                                     pos_label="RRab")
            roc_auc = metrics.auc(fpr, tpr)
            display = metrics.RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc,
                                              estimator_name='RF')
            roc_auc_list.append(roc_auc)
            display_list.append(display)
        ######################################



    ## plot_confusion #############################
    cm_average = sum(cm_list)/10
    cm_average_train = sum(cm_list_train)/10
    plt.figure(figsize=(12, 8))
    plt.tight_layout()
    custom_plot_confusion_matrix(cm_average, classes = labels, *args ,**kwargs)
    plt.savefig(output_dir + os.sep + "confusion.pdf")
#    plt.show()
    plt.close()
    if cm_train:
        plt.figure(figsize=(12, 8))
        plt.tight_layout()
        custom_plot_confusion_matrix(cm_average_train, classes = labels, *args ,**kwargs)
        plt.savefig(output_dir + os.sep + "confusion_train.pdf")
#        plt.show()
        plt.close()
    ################################################

    ## Terminamos de armar los clasification report ####
    cl_df["label"] = labels
    cl_df_train["label"] = labels
    cl = cl_df.round(1)[["label", "precision", "recall", "f1-score"]]
    cl_train = cl_df_train.round(1)[["label", "precision", "recall", "f1-score"]]
    #####################################################
    with open(output_dir + os.sep + "clasification_report.txt", "w") as fout:
        #print("Classification Report:")
        #print(cl)
        #print("")
        pprint.pprint("Classification Report:", fout)
        pprint.pprint(cl, fout)
        pprint.pprint("", fout)
        if cm_train:
            #print("Classification Report: (Trainning set)")
            #print(cl_train)
            #print("")
            pprint.pprint("Classification Report: (Trainning set)", fout)
            pprint.pprint(cl_train, fout)
            pprint.pprint("", fout)

    #     features_names = ['mediana', 'sigma', 'skewness', 'kurt', 'mv', 'iqr', 'AD', 'period', 'AC_std', 'mpr20', 'mpr35', 'mpr50', 'mpr75', 'mpr80', 'slope', 'mad', 'rcs', "rise_time", "fade_std_rate", "peak_std_rate"]
    feature_importances = feature_importances/feature_importances.size
    features_names = X.columns.values
    plt.figure(figsize=(12,6))
    sorted_idx = np.argsort(feature_importances)[::-1]
    plt.bar(np.arange(feature_importances.size), feature_importances[sorted_idx])
    plt.xticks(np.arange(feature_importances.size), np.asarray(features_names)[sorted_idx], rotation='vertical', size = 15)
    plt.ylabel("Nivel de importancia", size = 17)
    plt.xlabel("Features", size = 17)
    plt.yticks(size = 15)
    plt.tight_layout()
    plt.savefig(output_dir + os.sep + "importance.pdf")
#    plt.show()
    plt.close()
    with open(output_dir + os.sep + "importance_report.txt", "w") as fout:
        pprint.pprint("Importance Report: ", fout)
        importance_out = [{f:v} for f,v in zip(
                                        np.asarray(features_names)[sorted_idx],
                                            feature_importances[sorted_idx])]
        pprint.pprint(importance_out, fout)
    #######################################
    y_pred_output = pd.concat(y_pred_list)
    y_pred_output = y_pred_output.groupby(y_pred_output.index).mean()
    #######################################

    ## ROC ###############################
    fig, ax = plt.subplots(figsize=(10,10))
    if len(labels)==2 and "RRab" in labels:
        roc_auc_mean = sum(roc_auc_list)/10
        for display in display_list:
            display.plot(ax = ax)
        plt.savefig(output_dir + os.sep + "roc_curve.pdf")
#         plt.show()
        plt.close()
    ######################################

    return cl, y_pred_output

if __name__=="__main__":
    # user input
    NUM_PROC = int(sys.argv[1])
    TRAINING_FILE = sys.argv[2]
    OUTPUT_DIR = sys.argv[3]
    if len(sys.argv)>4:
        config_preset = sys.argv[4]
    else:
        config_preset = "default"
    SELECTED_FEATURES = P.selected_features[config_preset]
    MODEL_PARAMS = P.model_parameters[config_preset]

    # Load training feets
    feets_data = pd.read_csv(TRAINING_FILE, sep=" ")
    feets_data = feets_data.replace([np.inf, -np.inf], np.nan)
    feets_data = feets_data.dropna()
    feets_Y = feets_data.label
    feets_X = feets_data[SELECTED_FEATURES]
    # Classifier intance
    model = SingleProbRF(thresh = P.threshold)
    model.MODEL_PARAMS.update(MODEL_PARAMS)
    model.MODEL_PARAMS["n_jobs"] = NUM_PROC
    out_df = singleprob_eval_final(model,
                                         X=feets_X, Y=feets_Y,
                                         cm_train=True, add_low_prob=False,
                                         output_dir=OUTPUT_DIR)
    # Save CV prediction
    out = feets_data[["filename", "label", "period"]].join(out_df[1])
    prob = out.iloc[:,3:].max(axis=1)
    pred = out.iloc[:,3:].idxmax(axis=1)
    out["prob"] = prob
    out["pred"] = pred
    out.to_csv(f"{OUTPUT_DIR}{os.sep}train_cv_prediction.txt",
                                            sep=" ", index=False)
