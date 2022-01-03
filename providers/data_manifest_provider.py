import numpy as np


class DataManifestProvider:
    """
    Static final attributes which informs any functionality of the excepted data to be received.

    Attributes
    ----------
        DIMENSIONS                Specify the dimensions used in the algorithms in general
        PARAMETERS                Specify the number of parameters used in the algorithms
    """

    DIMENSIONS = [10, 30, 50, 100]
    PARAMETERS = np.arange(14)
