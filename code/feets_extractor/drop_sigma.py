from loess_smoother import loess_smoother
import numpy as np
from george import kernels
import george
import emcee


def drop_err_sigma_gp(drop_err):
    def drop_err_wrapper(star_data, period):
        star_data = drop_err(star_data)
        fit, best_gamma = gaussian_process(star_data.mjd, star_data.mag, star_data.emag, period, 0.1)

        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(star_data.mjd, period)
        gp_mag, cov = fit.predict(star_data.mag, phase)

        sig = np.std(star_data.mag)
        lim_up = (gp_mag+sig*1.5)
        lim_down = (gp_mag-sig*1.5)
        f_lim_up = star_data.mag<lim_up
        f_lim_down = star_data.mag>lim_down

        star_data = star_data[f_lim_up & f_lim_down]

        return star_data
    return drop_err_wrapper

def drop_sigma_gp(extractor_fit):
    def fit_wrapper(self, time, magnitude, error, period, gamma):
        fit, best_gamma = gaussian_process(time, magnitude, error, period, 0.1)

        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)
        gp_mag, cov = fit.predict(magnitude, phase)

        sig = np.std(magnitude)
        lim_up = (gp_mag+sig*1.5)
        lim_down = (gp_mag-sig*1.5)
        f_lim_up = magnitude<lim_up
        f_lim_down = magnitude>lim_down

        time = time[f_lim_up & f_lim_down]
        magnitude = magnitude[f_lim_up & f_lim_down]
        error = error[f_lim_up & f_lim_down]

        return extractor_fit(self, time, magnitude, error, period, gamma)
    return fit_wrapper

def drop_sigma_loess(extractor_fit):
    def fit_wrapper(self, time, magnitude, error, period, gamma):
        #loess_smoother
        loess_mjd, loess_mag, loess_emag = loess_smoother(time, magnitude, error, period)
        fit, best_gamma = gaussian_process(loess_mjd, loess_mag, loess_emag, period, 0.1)

        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time, period)
        gp_mag, cov = fit.predict(loess_mag, phase)

        sig = np.std(magnitude)
        lim_up = (gp_mag+sig*1.5)
        lim_down = (gp_mag-sig*1.5)
        f_lim_up = magnitude<lim_up
        f_lim_down = magnitude>lim_down

        time = time[f_lim_up & f_lim_down]
        magnitude = magnitude[f_lim_up & f_lim_down]
        error = error[f_lim_up & f_lim_down]

        return extractor_fit(self, time, magnitude, error, period, gamma)
    return fit_wrapper

def gaussian_process(time, magnitude, error, period, gamma):
    phaser = lambda mjd, P: (mjd/P)%1.
    phase = phaser(time, period)

    best_gamma = gamma #0.1
    lnl = 0

    kernel = kernels.ConstantKernel(np.median(magnitude)) + kernels.ExpSine2Kernel(gamma=best_gamma, log_period=0.)
    gp = george.GP(kernel)
    gp.compute(phase, error)
    return gp, best_gamma
