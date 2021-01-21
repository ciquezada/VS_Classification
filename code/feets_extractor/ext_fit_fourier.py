import feets
import pandas as pd
import numpy as np
from george import kernels
import george
import emcee
from symfit import Parameter, parameters, variables, sin, cos, Fit
from loess_smoother import smooth_curve_data_with_loess
from normalizer import normalize_curve_data


class FitFourier(feets.Extractor):
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
    features = ['a0', 'a1', 'a2', 'a3',
                  'a4', 'a5', 'a6', 'a7',
                  'phi_1', 'phi_2', 'phi_3',
                  'phi_4', 'phi_5', 'phi_6',
                  'phi_7', 'a21', 'a31', 'a41',
                  'p21', 'p31', 'p41',]
    params = {"period": 1, "gamma": 0.1}

    def _get_template_params(self, period):
        params_data = pd.read_csv("Braga_templates.table", delim_whitespace = True)
        return params_data.iloc[0, 1:-1].to_dict()

    @staticmethod
    def _fourier_series(t, P, N, a0, a1, a2, a3, a4, a5, a6, a7,
                                    phi_1, phi_2, phi_3, phi_4, phi_5, phi_6, phi_7):
        """
        Returns a symbolic fourier series of order `n`.

        :param n: Order of the fourier series.
        :param x: Independent variable
        :param f: Frequency of the fourier series
        """
        # Make the parameter objects for all the terms
    #     a0, *a_list = parameters(','.join(['a{}'.format(i) for i in range(0, N + 1)]))
    #     phi_list = parameters(','.join(['phi_{}'.format(i) for i in range(1, N + 1)]))

        a0, *a_list = [a0, a1, a2, a3, a4, a5, a6, a7]
        phi_list = [phi_1, phi_2, phi_3, phi_4, phi_5, phi_6, phi_7]

        # Construct the series
        series = a0 + sum(a_n * sin(2*np.pi*n * t/P + phi_n)
                          for n, (a_n, phi_n) in enumerate(zip(a_list, phi_list), start=1))

        return series


    def _gaussian_process(self, time, magnitude, error, period, gamma):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)

        best_gamma = gamma
        lnl = 0

        kernel = kernels.ConstantKernel(np.median(magnitude)) + kernels.ExpSine2Kernel(gamma=best_gamma, log_period=0.)
        gp = george.GP(kernel)
        gp.compute(phase, error)
        return gp, best_gamma

    # @normalize_curve_data
    # @smooth_curve_data_with_loess
    def fit(self, time, magnitude, error, period, gamma):
        # retrieve the amplitude limits
        fit, best_gamma = self._gaussian_process(time, magnitude, error, period, gamma)
        gp_xdata = np.linspace(0, 2, 1000)
        gp_ydata, cov = fit.predict(magnitude, gp_xdata)

        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)

        template_params = self._get_template_params(period)

        # START FIT ##################
        guess_params = {}
        for k in template_params:
            guess_params[k] = Parameter(k, value=template_params[k], fixed=False)


        t, y = variables('t, y')
        model_dict = {y: self._fourier_series(t, P=1, N=7, **guess_params)}
        fit = Fit(model_dict, t=phase, y=magnitude, sigma_y = error)
        fit_result = fit.execute()
        params = fit_result.params
        # END FIT ####################

        # START FIT ##################
        guess_params = {}
        for k in template_params:
            guess_params[k] = Parameter(k, value=params[k], fixed=False)

        t, y = variables('t, y')
        model_dict = {y: self._fourier_series(t, P=1, N=7, **guess_params)}
        fit = Fit(model_dict, t=gp_xdata, y=gp_ydata, sigma_y = cov[1])
        fit_result = fit.execute()
        params = fit_result.params
        # END FIT ####################

        fourier_params = {}
        for k in template_params:
            fourier_params[k] = params[k]

        for i in [1,2,3,4,5,6,7]:
            fourier_params["phi_{}".format(i)] = fourier_params["phi_{}".format(i)] if fourier_params["a{}".format(i)]>=0 else fourier_params["phi_{}".format(i)]+np.pi
            fourier_params["a{}".format(i)] = np.abs(fourier_params["a{}".format(i)])

        fourier_params["a21"] = np.abs(fourier_params["a2"] / fourier_params["a1"])
        fourier_params["a31"] = np.abs(fourier_params["a3"] / fourier_params["a1"])
        fourier_params["a41"] = np.abs(fourier_params["a4"] / fourier_params["a1"])
        fourier_params["p21"] = phaser(fourier_params["phi_2"] - 2*fourier_params["phi_1"], 2*np.pi)*2*np.pi
        fourier_params["p31"] = phaser(fourier_params["phi_3"] - 3*fourier_params["phi_1"], 2*np.pi)*2*np.pi
        fourier_params["p41"] = phaser(fourier_params["phi_4"] - 4*fourier_params["phi_1"], 2*np.pi)*2*np.pi

        return fourier_params
