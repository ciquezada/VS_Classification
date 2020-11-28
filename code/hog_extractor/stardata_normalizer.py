from symfit import Parameter, parameters, variables, sin, cos, Fit
import numpy as np
import pandas as pd
import math


def iqr(magnitude):
    N = len(magnitude)
    sorted_mag = np.sort(magnitude)
    max5p = np.median(sorted_mag[-int(math.ceil(0.05 * N)) :])
    min5p = np.median(sorted_mag[0 : int(math.ceil(0.05 * N))])
    return max5p - min5p

def fourier_template(t, t_sync, mag_mean, P, N, A, a0, a1, phi_1):
    """
    Returns a symbolic fourier series of order `n`.

    :param n: Order of the fourier series.
    :param x: Independent variable
    :param f: Frequency of the fourier series
    """
    a0, *a_list = [a0, a1]
    phi_list = [phi_1]

    # Construct the series
    series = a0 + sum(a_n * cos(2*np.pi*n * (t + t_sync)/P + phi_n)
                      for n, (a_n, phi_n) in enumerate(zip(a_list, phi_list), start=1))

    return series * A + mag_mean

def normalize_star_data(time, magnitude, error, period, t_sync, mag_mean, ampl, **params):
    star_x = time + t_sync
    star_y = (magnitude - mag_mean) / ampl
    star_y_err = (error) / ampl
    phaser = lambda mjd, P: (mjd/P)%1.*P
    phase = phaser(star_x, period)
    return pd.DataFrame([*zip(phase, star_y, star_y_err)], columns=["mjd", "mag", "emag"])

def fit(time, magnitude, error, period):
    # retrieve the amplitude limits
#         template_params = self._get_template_params(period)
    guess_ampl = iqr(magnitude)

    # START FIT ##################
    t_sync = Parameter('t_sync', value=0, fixed=False)
    mag_mean = Parameter('mag_mean', value=14, fixed=False)
    fit_ampl  = Parameter('ampl', value=guess_ampl, min=guess_ampl*.1, fixed=True)

    t, y = variables('t, y')
    model_dict = {y: fourier_template(t, t_sync, mag_mean, P=period, N=7, A=fit_ampl, a0=0, a1=1, phi_1=0)}
    fit = Fit(model_dict, t=time, y=magnitude, sigma_y = error)
    print(fit)
    fit_result = fit.execute()
    params = fit_result.params
    # END FIT ####################

    return params

def normalize(time, magnitude, error, period):
    params = fit(time.values, magnitude.values, error.values, period)
    normal_star_data = normalize_star_data(time, magnitude, error, period, **params)
    return normal_star_data
