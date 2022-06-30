from sepal_ui import model as sm
from traitlets import Any


class Geo4lupModel(sm.Model):

    bin_type = Any(None).tag(sync=True)
    "the binning system used for computation"
