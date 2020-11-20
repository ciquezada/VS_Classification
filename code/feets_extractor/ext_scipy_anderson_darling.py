import feets
from scipy import stats


class SciPyAndersonDarling(feets.Extractor):
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
    features = ["AD"]

    def _AD(self, magnitude):
        return stats.anderson(magnitude).statistic
    
    def fit(self, magnitude):
        # retrieve the amplitude limits
        AD = self._AD(magnitude)
        return {"AD": AD}