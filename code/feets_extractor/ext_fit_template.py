import feets
import math
import numpy as np
import pandas as pd
from symfit import Parameter, parameters, variables, sin, cos, Fit
from sklearn.metrics import mean_squared_error


class FitTemplate(feets.Extractor):
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
    features = ["R2Template", "MseTemplate", "A1A2_ratio"]
    params = {"period": 1}
    
    def _iqr(self, magnitude):
        N = len(magnitude)
        sorted_mag = np.sort(magnitude)
        max5p = np.median(sorted_mag[-int(math.ceil(0.05 * N)) :])
        min5p = np.median(sorted_mag[0 : int(math.ceil(0.05 * N))])
        return max5p - min5p
    
    def _get_template_params(self, period):
        params_data = pd.read_csv("Kband_models_Inno.table", delim_whitespace = True)
        if period < 3:
            return params_data.iloc[0, 1:-1].to_dict()
        elif 3 <= period and period < 5:
            return params_data.iloc[1, 1:-1].to_dict()
        elif 5 <= period and period < 7:
            return params_data.iloc[2, 1:-1].to_dict()
        elif 7 <= period and period < 9.5:
            return params_data.iloc[3, 1:-1].to_dict()
        elif 9.5 <= period and period < 10.5:
            return params_data.iloc[4, 1:-1].to_dict()
        elif 10.5 <= period and period < 13.5:
            return params_data.iloc[5, 1:-1].to_dict()
        elif 13.5 <= period and period < 15.5:
            return params_data.iloc[6, 1:-1].to_dict()
        elif 15.5 <= period and period < 20:
            return params_data.iloc[7, 1:-1].to_dict()
        elif 20 <= period and period < 30:
            return params_data.iloc[8, 1:-1].to_dict()
        elif 30 <= period:
            return params_data.iloc[9, 1:-1].to_dict()
    
    def _normalize_star_data(self, time, magnitude, error, period, t_sync, mag_mean, ampl, **params):
        star_x = time + t_sync
        star_y = (magnitude - mag_mean) / ampl
        star_y_err = (error) / ampl
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(star_x, period)
        return pd.DataFrame([*zip(phase, star_y, star_y_err)], columns=["mjd", "mag", "emag"])

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
        # retrieve the amplitude limits
        template_params = self._get_template_params(period)
        guess_ampl = self._iqr(magnitude)

        # START FIT ##################
        t_sync = Parameter('t_sync', value=0, fixed=False)
        mag_mean = Parameter('mag_mean', value=14, fixed=False)
        fit_ampl  = Parameter('ampl', value=guess_ampl, min=guess_ampl*.1, fixed=True)

        t, y = variables('t, y')
        model_dict = {y: self._fourier_template(t, t_sync, mag_mean, P=period, N=7, A=fit_ampl, **template_params)}
        fit = Fit(model_dict, t=time, y=magnitude, sigma_y = error)
        fit_result = fit.execute()
        params = fit_result.params
        # END FIT ####################
        
        R2Template = fit_result.r_squared
        
        normal_star_data = self._normalize_star_data(time, magnitude, error, period, **params)
        normal_template = lambda x: self._fourier_template(t, t_sync, mag_mean, P=1, N=7, A = 1, **template_params)(x, 0, 0)
        MseTemplate = mean_squared_error(normal_star_data.mag, normal_template(normal_star_data.mjd),
                                              sample_weight=None, squared=False)
        
        normal_star_data = self._normalize_star_data(time, magnitude, error, 2*period,
                                                     t_sync=params["t_sync"], mag_mean=0, ampl=1)
        phase1_star_data = normal_star_data.query("mjd < 0.5")
        phase2_star_data = normal_star_data.query("mjd >= 0.5")
        A1A2_ratio = self._iqr(phase1_star_data.mag) / self._iqr(phase2_star_data.mag)
            
        return {"R2Template": R2Template, "MseTemplate": MseTemplate, 
                "A1A2_ratio": A1A2_ratio}