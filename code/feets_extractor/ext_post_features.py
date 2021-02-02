import feets
import pandas as pd
import numpy as np
import math
from ext_fit_braga_template_rrab import FitBragaTemplateRRab
from ext_fit_braga_template_rrc import FitBragaTemplateRRc
from george import kernels
import george
import emcee
from scipy.signal import find_peaks
from scipy import optimize
from functools import reduce
from loess_smoother import smooth_curve_data_with_loess
from sklearn.metrics import mean_squared_error
from drop_sigma import drop_sigma_loess, drop_sigma_gp


class PostFeatures(feets.Extractor):
    """
    """

    data = ["time", "magnitude", "error"]
    features = ["post_mseRRab", "post_mseRRc",
                "post_GP_mse", "post_sigma", "post_rho",
                "post_GP_RiseRatio", "post_GP_DownRatio",
                "post_GP_RiseDownRatio", "post_GP_Skew", "post_SN_ratio",
                "post_N_peaks", "post_alias_score"]
    params = {"period": 1, "gamma": 0.1}

    def _iqr(self, magnitude):
        N = len(magnitude)
        sorted_mag = np.sort(magnitude)
        max5p = np.median(sorted_mag[-int(math.ceil(0.05 * N)) :])
        min5p = np.median(sorted_mag[0 : int(math.ceil(0.05 * N))])
        return max5p - min5p

    def _gp_skew(self, magnitude, fit):
        xdata = np.linspace(0, 1)
        ydata, cov = fit.predict(magnitude, xdata)

        phase_df = pd.DataFrame(xdata, columns = ["x"])
        phase_df["y"] = -ydata+max(ydata)

        xdata = np.linspace(phase_df.loc[phase_df.y.idxmin()].x, phase_df.loc[phase_df.y.idxmin()].x + 1, 100)
        ydata, cov = fit.predict(magnitude, xdata)

        phase_df = pd.DataFrame(xdata, columns = ["x"])
        phase_df["y"] = -ydata+max(ydata)

        phase_dist = reduce(lambda x, y: x + y, map(lambda x, y: [x]*int(y*1000), phase_df.x.values, phase_df.y.values))
        phase_dist = pd.DataFrame(phase_dist, columns = ["x"])
        #phase_dist.hist(bins = 100)
        return phase_dist.x.skew()

    def _gp_rise_ratio(self, magnitude, fit):
        xdata = np.linspace(0, 1)
        ydata, cov = fit.predict(magnitude, xdata)

        phase_df = pd.DataFrame(xdata, columns = ["x"])
        phase_df["y"] = -ydata+max(ydata)

        x0_candidate = phase_df.loc[phase_df.y.idxmin()].x
        x0 = optimize.fmin(lambda x: -fit.predict(magnitude, x)[0], x0_candidate, disp = 0)[0]

        xdata = np.linspace(x0, x0 + 1)
        ydata, cov = fit.predict(magnitude, xdata)
        phase_df = pd.DataFrame(xdata, columns = ["x"])
        phase_df["y"] = -ydata+max(ydata)

        peaks, _ = find_peaks(phase_df["y"], height=0)
        max_x_candidate = phase_df.x.iloc[peaks[0]]

        max_x = optimize.fmin(lambda x: fit.predict(magnitude, x)[0], max_x_candidate, disp = 0)[0]
        return max_x - x0

    def _gp_down_ratio(self, magnitude, fit):
        xdata = np.linspace(0, 1)
        ydata, cov = fit.predict(magnitude, xdata)

        phase_df = pd.DataFrame(xdata, columns = ["x"])
        phase_df["y"] = -ydata+max(ydata)

        x0_candidate = phase_df.loc[phase_df.y.idxmin()].x
        x0 = optimize.fmin(lambda x: -fit.predict(magnitude, x)[0], x0_candidate, disp = 0)[0]

        xdata = np.linspace(x0, x0 + 1)
        ydata, cov = fit.predict(magnitude, xdata)
        phase_df = pd.DataFrame(xdata, columns = ["x"])
        phase_df["y"] = -ydata+max(ydata)

        peaks, _ = find_peaks(phase_df["y"], height=0)
        max_x_candidate = phase_df.x.iloc[peaks[-1]]

        max_x = optimize.fmin(lambda x: fit.predict(magnitude, x)[0], max_x_candidate, disp = 0)[0]
        return 1 - (max_x - x0), len(peaks)

    def _sigma(self, mag):
        return np.std(mag)

    def _gp_mse(self, time, magnitude, period, fit):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)
        gp_mag, cov = fit.predict(magnitude, phase)
        mse = mean_squared_error(magnitude, gp_mag,
                                      sample_weight=None, squared=False)
        return mse

    def _gaussian_process(self, time, magnitude, error, period, gamma):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)

        best_gamma = gamma #0.1
        lnl = 0

        kernel = kernels.ConstantKernel(np.median(magnitude)) + kernels.ExpSine2Kernel(gamma=best_gamma, log_period=0.)
        gp = george.GP(kernel)
        gp.compute(phase, error)
        return gp, best_gamma

    def _alias_score(self, time, period):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)
        bins = np.histogram(phase, bins=75, range=(0, 1))[0]
        return len(bins[bins==0])

    # @drop_sigma_loess
    # @drop_sigma_gp
    def fit(self, time, magnitude, error, period, gamma):
        fit, best_gamma = self._gaussian_process(time, magnitude, error, period, gamma)
        gp_down_ratio, n_peaks = self._gp_down_ratio(magnitude, fit)
        gp_rise_ratio = self._gp_rise_ratio(magnitude, fit)
        gp_rise_down = gp_rise_ratio / gp_down_ratio
        gp_skew = self._gp_skew(magnitude, fit)
        gp_mse = self._gp_mse(time, magnitude, period, fit)
        alias_score = self._alias_score(time, period)

        sigma = self._sigma(magnitude)
        rho = sigma/gp_mse
        amplitud = self._iqr(magnitude)
        sn_ratio = amplitud*np.sqrt(len(time))/gp_mse
        post_features = {"post_GP_mse":gp_mse,
                            "post_sigma":sigma,
                            "post_rho":rho,
                            "post_GP_RiseRatio": gp_rise_ratio,
                            "post_GP_DownRatio": gp_down_ratio,
                            "post_GP_RiseDownRatio": gp_rise_down,
                            "post_GP_Skew": gp_skew,
                            "post_SN_ratio": sn_ratio,
                            "post_N_peaks": n_peaks,
                            "post_alias_score": alias_score
                            }

        fit_ab = FitBragaTemplateRRab()
        fit_c = FitBragaTemplateRRc()
        params = fit_ab.fit(time, magnitude, error, period)
        params_c = fit_c.fit(time, magnitude, error, period, params["t_sync"])
        params.update(params_c)

        post_features["post_mseRRab"] = params["MseBragaTemplateRRab"]
        post_features["post_mseRRc"] = params["MseBragaTemplateRRc"]
        return post_features
