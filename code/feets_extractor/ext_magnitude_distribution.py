import feets
import numpy as np
from scipy.stats import skew, kurtosis


class MagnitudeDistribution(feets.Extractor):
    """
    **AD**
    The Anderson–Darling test is a statistical test of 
    whether a given sample of data is drawn from a given 
    probability distribution. In its basic form, the test 
    assumes that there are no parameters to be estimated 
    in the distribution being tested, in which case the test 
    and its set of critical values is distribution-free.
    """

    data = ["magnitude"]
    features = ["mediana", "sigma", "mv", "skewness", 
                "kurtosis", "mad", "Rcs", "Beyond3Std",
		"Beyond5Std"]

    def _mediana(self, mag):
        return np.median(mag)
    
    def _sigma(self, mag):
        return np.std(mag)
    
    def _skewness(self, mag):
        return skew(mag)
    
    def _kurtosis(self, mag):
        return kurtosis(mag)
    
    def _mad(self, mag):
        return np.median(np.abs(mag - np.median(mag)))
    
    def _Rcs(self, mag):
        return np.sum(mag - np.median(mag))/(len(mag)*np.std(mag))

    def _Beyond3Std(self, mag, med, sig):
        return len(mag[mag > med+3*sig]) + len(mag[mag < med-3*sig])
    
    def _Beyond5Std(self, mag, med, sig):
        return len(mag[mag > med+5*sig]) + len(mag[mag < med-5*sig])

    def fit(self, magnitude):
        # retrieve the amplitude limits
        mediana = self._mediana(magnitude)
        sigma = self._sigma(magnitude)
        mv = sigma/mediana
        skewness = self._skewness(magnitude)
        kurtosis = self._kurtosis(magnitude)
        mad = self._mad(magnitude)
        Rcs = self._Rcs(magnitude)
        Beyond3Std = self._Beyond3Std(magnitude, mediana, sigma)
        Beyond5Std = self._Beyond5Std(magnitude, mediana, sigma)
        return {"mediana": mediana, "sigma": sigma, "mv": mv,
                "skewness": skewness, "kurtosis": kurtosis, 
                "mad": mad, "Rcs": Rcs, "Beyond3Std": Beyond3Std,
                "Beyond5Std": Beyond5Std}
