import feets
from ext_fit_braga_template_rrab import FitBragaTemplateRRab
from ext_fit_braga_template_rrc import FitBragaTemplateRRc


class FitBragaTemplate(feets.Extractor):
    """
    """

    data = ["time", "magnitude", "error"]
    features = ["R2BragaTemplateRRab", "MseBragaTemplateRRab",
                    "R2BragaTemplateRRc", "MseBragaTemplateRRc"]
    params = {"period": 1}

    def fit(self, time, magnitude, error, period):
        fit_ab = FitBragaTemplateRRab()
        fit_c = FitBragaTemplateRRc()
        params = fit_ab.fit(time, magnitude, error, period)
        params_c = fit_c.fit(time, magnitude, error, period, params["t_sync"])
        params.update(params_c)
        del params['t_sync']
        return params
