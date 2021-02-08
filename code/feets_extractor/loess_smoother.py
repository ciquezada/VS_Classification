import scipy.stats as stats
import statsmodels.api as sm
import numpy as np


#revisar los errores
def smooth_curve_data_with_loess(extractor_fit):
    def fit_wrapper(self, time, magnitude, error, period, gamma):
        #loess_smoother
        loess_mjd, loess_mag, loess_emag = loess_smoother(time, magnitude, error, period)
        return extractor_fit(self, loess_mjd, loess_mag, loess_emag, period, gamma)
    return fit_wrapper

def loess_smoother(time, magnitude, error, period):
    phaser = lambda mjd, P: (mjd/P)%1.
    phase = phaser(time, period)
    lowess = sm.nonparametric.lowess
    w = lowess(np.concatenate((magnitude, magnitude)),
               np.concatenate((phase, phase+1)),
               frac=1/6, it=50, delta=0.0)

    loess_mjd = w[(w[:,0]>0.5) & (w[:,0]<1.5),0]
    loess_mag = w[(w[:,0]>0.5) & (w[:,0]<1.5),1]
    loess_emag = np.full(loess_mag.shape[0], 0.001) #revisar esto
    return loess_mjd*period, loess_mag, loess_emag
