import feets
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression


class StatsmodelTSA(feets.Extractor):
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

    data = ["time", "magnitude"]
    features = ["AC_std", "slope"]

    def _slope(self, time, magnitude):
        mjd2 = time.reshape(-1,1)
        mag2 = magnitude.reshape(-1,1)
        linear_regressor = LinearRegression()
        linear_regressor.fit(mjd2, mag2)
        m = linear_regressor.coef_[0][0]
        return m

    def _AC_std(self, magnitude):
        nobs = len(magnitude)
        lags = min(int(10 * np.log10(nobs)), nobs - 1)
        return np.std(sm.tsa.stattools.acf(magnitude, qstat=False,
                                                    fft=True, nlags=lags))

    def fit(self, time, magnitude):
        # retrieve the amplitude limits
        AC_std = self._AC_std(magnitude)
        slope = self._slope(time, magnitude)
        return {"AC_std": AC_std, "slope": slope}
