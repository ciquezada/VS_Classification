import feets
import math
import numpy as np
import pandas as pd
from symfit import Parameter, parameters, variables, sin, cos, Fit
from symfit.core.minimizers import DifferentialEvolution
from sklearn.metrics import mean_squared_error


class FitBragaTemplateRRc(feets.Extractor):
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
    features = ["R2BragaTemplateRRc", "MseBragaTemplateRRc"]
    params = {"period": 1}

    def _template_inspect(self, time, magnitude, error, period, fit):
        fig = plt.figure(figsize=(8,4), dpi=72)

        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)

        plt.errorbar(phase, magnitude, yerr=error, fmt="*", ecolor="r")
        plt.errorbar(phase+1, magnitude, yerr=error, fmt="*", ecolor="r")

        xdata = np.linspace(0,2)
        ydata = fit(xdata)
        plt.plot(xdata, ydata, "cyan", lw=4, zorder=10)

        plt.gca().invert_yaxis()
        plt.show()
        plt.close()

    def _iqr(self, magnitude):
        N = len(magnitude)
        sorted_mag = np.sort(magnitude)
        max5p = np.median(sorted_mag[-int(math.ceil(0.05 * N)) :])
        min5p = np.median(sorted_mag[0 : int(math.ceil(0.05 * N))])
        return max5p - min5p

    def _get_template_params(self, period):
        params_data = pd.read_csv("Braga_templates.table", delim_whitespace = True)
        return params_data.iloc[3, 1:-1].to_dict()

    def _normalize_star_data(self, time, magnitude, error, period, t_sync, mag_mean, ampl, **params):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period) + t_sync
        magnitude = (magnitude-mag_mean)/ampl
        error = error/ampl
        return phase, magnitude, error

    @staticmethod
    def _fourier_template(t, t_sync, mag_mean, P, N, A, a0, a1, a2, a3, a4, a5, a6, a7,
                                    phi_1, phi_2, phi_3, phi_4, phi_5, phi_6, phi_7):
        """
        Returns a symbolic fourier series of order `n`.

        :param n: Order of the fourier series.
        :param x: Independent variable
        :param f: Frequency of the fourier series
        """

        a0, *a_list = [a0, a1, a2, a3, a4, a5, a6, a7]
        phi_list = [phi_1, phi_2, phi_3, phi_4, phi_5, phi_6, phi_7]

        # Construct the series
        series = a0 + sum(a_n * cos(2*np.pi*n * (t + t_sync)/P + phi_n)
                          for n, (a_n, phi_n) in enumerate(zip(a_list, phi_list), start=1))

        return series * A + mag_mean

    def fit(self, time, magnitude, error, period):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)
        # retrieve the amplitude limits
        template_params = self._get_template_params(period)
        guess_ampl = self._iqr(magnitude)

        # START FIT ##################
        t_sync = Parameter('t_sync', value=0, min=0, max=1, fixed=False)
        mag_mean = Parameter('mag_mean', value=14, min=10, max=20, fixed=False)
        fit_ampl  = Parameter('ampl', value=guess_ampl, min=guess_ampl*.7, max=guess_ampl*1.3, fixed=True)

        t, y = variables('t, y')
        model_dict = {y: self._fourier_template(t, t_sync, mag_mean, P=1, N=7, A=fit_ampl, **template_params)}
        fit = Fit(model_dict, t=phase, y=magnitude, sigma_y = error, minimizer=DifferentialEvolution)

        fit_result = fit.execute()
        params = fit_result.params
        # END FIT ####################

        ## INSPECT
        # template_fit = self._fourier_template(t, t_sync=params["t_sync"], mag_mean=params["mag_mean"],
        #                                          P=1, N=7, A=params["ampl"], **template_params)
        # self._template_inspect(time, magnitude, error, period, template_fit)
        ##
        R2Template = fit_result.r_squared

        normal_time, normal_magnitude, normal_error = self._normalize_star_data(time, magnitude, error, period, **params)
        normal_template = lambda x: self._fourier_template(t, t_sync=0, mag_mean=0, P=1, N=7, A = 1, **template_params)(x)
        ## INSPECT NORMAL
        # self._template_inspect(normal_time, normal_magnitude, normal_error, 1, normal_template)
        ##
        MseTemplate = mean_squared_error(normal_magnitude, normal_template(normal_time),
                                              sample_weight=None, squared=False)

        return {"R2BragaTemplateRRc": R2Template, "MseBragaTemplateRRc": MseTemplate}
