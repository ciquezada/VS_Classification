import feets
import pandas as pd
import numpy as np
from george import kernels
import george
import emcee
from scipy.signal import find_peaks
from scipy import optimize
from functools import reduce
from loess_smoother import smooth_curve_data_with_loess


class FitGP(feets.Extractor):
    """
    **AC_std**
    ACF is an (complete) auto-correlation function
    which gives us values of auto-correlation of
    any series with its lagged values. We plot
    these values along with the confidence band and
    tada! We have an ACF plot. In simple terms,
    it describes how well the present value of the
    series is related with its past values. A time
    series can have components like trend, seasonality,
    cyclic and residual. ACF considers all these
    components while finding correlations hence
    it’s a ‘complete auto-correlation plot’.
    """

    data = ["time", "magnitude", "error"]
    features = ["GP_RiseRatio", "GP_DownRatio",
                    "GP_RiseDownRatio", "GP_Skew"]
    params = {"period": 1, "gamma": 0.1}

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
        return 1 - (max_x - x0)

    def _gaussian_process(self, time, magnitude, error, period, gamma):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)

        best_gamma = gamma #0.1
        lnl = 0

        kernel = kernels.ConstantKernel(np.median(magnitude)) + kernels.ExpSine2Kernel(gamma=best_gamma, log_period=0.)
        gp = george.GP(kernel)
        gp.compute(phase, error)
        return gp, best_gamma

    @smooth_curve_data_with_loess
    def fit(self, time, magnitude, error, period, gamma):
        # retrieve the amplitude limits
        fit, best_gamma = self._gaussian_process(time, magnitude, error, period, gamma)
        gp_down_ratio = self._gp_down_ratio(magnitude, fit)
        gp_rise_ratio = self._gp_rise_ratio(magnitude, fit)
        gp_rise_down = gp_rise_ratio / gp_down_ratio
        gp_skew = self._gp_skew(magnitude, fit)

        return {"GP_RiseRatio": gp_rise_ratio, "GP_DownRatio": gp_down_ratio,
                    "GP_RiseDownRatio": gp_rise_down, "GP_Skew": gp_skew}
