import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools as it
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedShuffleSplit
from classifier import SingleProbRF
import pprint
import sys


TRAINING_FILE = sys.argv[1] #vvv_tset_features.csv

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

def singleprob_eval_final(model, X, Y, cm_train=False, add_low_prob=False, cv = 10, *args, **kwargs):
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
        y_pred_list.append(pd.DataFrame(y_pred, columns=["y_pred"]).set_index([y_test.index]))
        #################################################
        ## Y_PRED_PROBA OUTPUT #################################
        y_pred_list[-1]["prob"] = model.predict_proba(x_test).set_index([y_test.index]).max(axis=1)
        #################################################


    ## plot_confusion #############################
    cm_average = sum(cm_list)/10
    cm_average_train = sum(cm_list_train)/10
    plt.figure(figsize=(12, 8))
    plt.tight_layout()
    custom_plot_confusion_matrix(cm_average, classes = labels, *args ,**kwargs)
    plt.savefig("confusion.pdf")
#    plt.show()
    plt.close()
    if cm_train:
        plt.figure(figsize=(12, 8))
        plt.tight_layout()
        custom_plot_confusion_matrix(cm_average_train, classes = labels, *args ,**kwargs)
        plt.savefig("confusion_train.pdf")
#        plt.show()
        plt.close()
    ################################################

    ## Terminamos de armar los clasification report ####
    cl_df["label"] = labels
    cl_df_train["label"] = labels
    cl = cl_df.round(1)[["label", "precision", "recall", "f1-score"]]
    cl_train = cl_df_train.round(1)[["label", "precision", "recall", "f1-score"]]
    #####################################################
    with open("clasification_report.txt", "w") as fout:
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
    plt.savefig("importance.pdf")
#    plt.show()
    plt.close()

    #######################################
    y_pred_output = pd.concat(y_pred_list)
    #######################################
    return cl, y_pred_output

if __name__=="__main__":
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
    feets_data = pd.read_csv(TRAINING_FILE, sep=" ")
    feets_data = feets_data.dropna()
    feets_Y, feets_X = feets_data.iloc[:,1], feets_data.iloc[:,2:]

    model = SingleProbRF(tresh = 0.0)
    out_df = singleprob_eval_final(model,
                     X = feets_X[selected_features], Y = feets_Y,
                     cm_train = False, add_low_prob=False)
