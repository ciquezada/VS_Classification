import numpy as np
import pandas as pd
import math
from symfit import Parameter, parameters, variables, sin, cos, Fit
from symfit.core.minimizers import DifferentialEvolution, BFGS


def normalize_curve_data(extractor_fit):
    def fit_wrapper(self, time, magnitude, error, period, gamma):
        #loess_smoother
        normalized_mjd, normalized_mag, normalized_emag = normalizer(time, magnitude, error, period)
        return extractor_fit(self, normalized_mjd, normalized_mag, normalized_emag, period, gamma)
    return fit_wrapper

def get_template_params():
    params_data = pd.read_csv("Braga_templates.table", delim_whitespace = True)
    return params_data.iloc[0, 1:-1].to_dict()

def iqr(magnitude):
    N = len(magnitude)
    sorted_mag = np.sort(magnitude)
    max5p = np.median(sorted_mag[-int(math.ceil(0.05 * N)) :])
    min5p = np.median(sorted_mag[0 : int(math.ceil(0.05 * N))])
    return max5p - min5p

def normalize_data(time, magnitude, error, period, t_sync, mag_mean, ampl, **params):
    phaser = lambda mjd, P: (mjd/P)%1.*P
    phase = phaser(time, period) + t_sync
    magnitude = (magnitude-mag_mean)/ampl
    error = error/ampl
    return phase, magnitude, error

def fourier_template(t, t_sync, mag_mean, P, A, a0, a1, a2, a3, a4, a5, a6, a7,
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

def normalizer(time, magnitude, error, period):
    phaser = lambda mjd, P: (mjd/P)%1.*P
    phase = phaser(time, period)
    # retrieve the amplitude limits
    template_params = get_template_params()
    guess_ampl = iqr(magnitude)

    # START FIT ##################
    t_sync = Parameter('t_sync', value=0, min=0, max=period, fixed=False)
    mag_mean = Parameter('mag_mean', value=14, min=10, max=20, fixed=False)
    fit_ampl = guess_ampl

    t, y = variables('t, y')
    model_dict = {y: fourier_template(t, t_sync, mag_mean, P=period, A=fit_ampl, **template_params)}
    fit = Fit(model_dict, t=phase, y=magnitude, sigma_y = error, minimizer=[DifferentialEvolution, BFGS]) # secuential minimizer

    fit_result = fit.execute()
    params = fit_result.params
    params["ampl"] = guess_ampl # THIS IS FOR SECUENTIAL MINIMIZER TO WORK RIGHT
    # END FIT ####################

    normal_time, normal_magnitude, normal_error = normalize_data(time, magnitude, error, period, **params)
    return normal_time, normal_magnitude, normal_error
