import feets
from ext_fit_braga_template_rrab import FitBragaTemplateRRab
from ext_fit_braga_template_rrc import FitBragaTemplateRRc
from sklearn.metrics import mean_squared_error
from george import kernels
import george
import emcee
import numpy as np


class PostFeatures(feets.Extractor):
    """
    """

    data = ["time", "magnitude", "error"]
    features = ["Post_MseRRab", "Post_MseRRc",
                "Post_GP_Mse", "Post_Sigma", "Post_Rho"]
    params = {"period": 1, "gamma": 0.1}

    def _sigma(self, mag):
        return np.std(mag)

    def _gp_mse(self, time, magnitude, period, fit):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)
        gp_mag, cov = fit.predict(magnitude, phase)
        mse = mean_squared_error(magnitude, gp_mag,
                                      sample_weight=None, squared=False)
        return mse

    def _drop_sigma(self, time, magnitude, error, period, fit):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)
        gp_mag, cov = fit.predict(magnitude, phase)

        sig = np.std(magnitude)
        lim_up = (gp_mag+sig*1.5)
        lim_down = (gp_mag-sig*1.5)
        f_lim_up = gp_mag<lim_up
        f_lim_down = gp_mag>lim_down
        return (time[f_lim_up & f_lim_down],
                magnitude[f_lim_up & f_lim_down],
                error[f_lim_up & f_lim_down])

    def _gaussian_process(self, time, magnitude, error, period, gamma):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)

        best_gamma = gamma #0.1
        lnl = 0

        kernel = kernels.ConstantKernel(np.median(magnitude)) + kernels.ExpSine2Kernel(gamma=best_gamma, log_period=0.)
        gp = george.GP(kernel)
        gp.compute(phase, error)
        return gp, best_gamma

    def fit(self, time, magnitude, error, period, gamma):
        # retrieve the amplitude limits
        fit, best_gamma = self._gaussian_process(time, magnitude, error, period, gamma)
        time, magnitude, error = self._drop_sigma(time, magnitude, error, period, fit)
        fit, best_gamma = self._gaussian_process(time, magnitude, error, period, gamma)

        gp_mse = self._gp_mse(time, magnitude, period, fit)
        sigma = self._sigma(magnitude)
        rho = sigma/gp_mse
        post_features = {"Post_GP_Mse":gp_mse, "Post_Sigma":sigma,
                                                            "Post_Rho":rho}

        fit_ab = FitBragaTemplateRRab()
        fit_c = FitBragaTemplateRRc()
        params = fit_ab.fit(time, magnitude, error, period)
        params_c = fit_c.fit(time, magnitude, error, period, params["t_sync"])
        params.update(params_c)

        post_features["Post_MseRRab"] = params["MseBragaTemplateRRab"]
        post_features["Post_MseRRab"] = params["MseBragaTemplateRRc"]
        return post_features
