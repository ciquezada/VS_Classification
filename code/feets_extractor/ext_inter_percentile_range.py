import math
import numpy as np
import feets


class InterPercentileRanges(feets.Extractor):
    """
    **FullAmplitude**
    The full amplitude is defined as the difference between the median
    of the maximum 5% and the median of the minimum 5% magnitudes. For a
    sequence of numbers from 0 to 1000 the amplitude should be equal to 475.5.
    References
    ----------
    .. [richards2011machine] Richards, J. W., Starr, D. L., Butler, N. R.,
       Bloom, J. S., Brewer, J. M., Crellin-Quick, A., ... &
       Rischard, M. (2011). On machine-learned classification of variable stars
       with sparse and noisy time-series data.
       The Astrophysical Journal, 733(1), 10. Doi:10.1088/0004-637X/733/1/10.
    """

    data = ["magnitude", "error"]
    features = ["iqr", "mpr20", "mpr35", "mpr50", "mpr65", "mpr80", "Tm"]

    def _mean_mag(self, magnitude, error):
        mag2flux = lambda mag: 10**(mag/-2.5)
        flux2mag = lambda flux: -2.5*np.log10(flux)
        synt_mean_mag_psf = lambda mag, err: flux2mag(np.sum(mag2flux(mag) * (1/mag2flux(err))) / np.sum(1/mag2flux(err)))
        mean_flux = synt_mean_mag_psf(magnitude, error)
        return mean_flux
    
    def _tm(self, magnitude, error, ampl):
        N = len(magnitude)
        sorted_mag = np.sort(magnitude)
        mean_magnitude = self._mean_mag(magnitude, error)
        max5p = np.median(sorted_mag[-int(math.ceil(0.05 * N)) :])
        return (max5p - mean_magnitude) / ampl
    
    def _iqr(self, sorted_mag):
        N = len(sorted_mag)
        max5p = np.median(sorted_mag[-int(math.ceil(0.05 * N)) :])
        min5p = np.median(sorted_mag[0 : int(math.ceil(0.05 * N))])
        return max5p - min5p
    
    def _mpr20(self, sorted_mag):
        q40, q60 = np.percentile(sorted_mag, [40 ,60])
        return (q60-q40)
    
    def _mpr35(self, sorted_mag):
        q32, q67 = np.percentile(sorted_mag, [32.5 ,67.5])
        return (q67-q32)
    
    def _mpr50(self, sorted_mag):
        q25, q75 = np.percentile(sorted_mag, [25 ,75])
        return (q75-q25)
    
    def _mpr65(self, sorted_mag):
        q17, q82 = np.percentile(sorted_mag, [17.5 ,82.5])
        return (q82-q17)

    def _mpr80(self, sorted_mag):
        q10, q90 = np.percentile(sorted_mag, [10 ,90])
        return (q90-q10)
    
    def fit(self, magnitude, error):
        # retrieve the amplitude limits
        sorted_mag = np.sort(magnitude)
        iqr = self._iqr(sorted_mag)
        mpr20 = self._mpr20(sorted_mag)/iqr
        mpr35 = self._mpr35(sorted_mag)/iqr
        mpr50 = self._mpr50(sorted_mag)/iqr
        mpr65 = self._mpr65(sorted_mag)/iqr
        mpr80 = self._mpr80(sorted_mag)/iqr
        Tm = self._tm(magnitude, error, iqr)
        return {"iqr": iqr, "mpr20": mpr20, "mpr35": mpr35,
                "mpr50": mpr50, "mpr65": mpr65, "mpr80": mpr80, 
                "Tm": Tm}