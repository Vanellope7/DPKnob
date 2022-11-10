import numpy as np

np.chararray
class Laplace:
    """
    BoundedSum computes the sum of values in a dataset, in a differentially private manner.

    Incrementally provides a differentially private sum, clamped between upper
    and lower values. Bounds can be manually set or privately inferred.
    """
    def __init__(self, u, b):
        self.b = b
        self.u = u

    def laplace_f(self, x):
        """
        计算拉普拉斯概率密度

        Parameters
        ----------
        x : float
            the point to be calculated

        Returns
        -------
        fVal : float
            Laplace probability density in x point
        """
        b = self.b
        return 1 / (2 * b) * np.exp(-np.abs(x) / b)

    def laplace_F(self, x):
        """
        计算拉普拉斯累计分布

        Parameters
        ----------
        x : float
            the point to be calculated

        Returns
        -------
        fVal : float
            Laplace probability density in x point
        """
        b = self.b
        return 1 / 2 + np.sign(x) / 2 * (1 - np.exp(-np.abs(x) / b))
