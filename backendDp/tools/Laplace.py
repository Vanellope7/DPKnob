import numpy as np

class Laplace:
    """
    BoundedSum computes the sum of values in a dataset, in a differentially private manner.

    Incrementally provides a differentially private sum, clamped between upper
    and lower values. Bounds can be manually set or privately inferred.
    """
    def __init__(self, b):
        self.b = b

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

    def Laplace_DV_f(self, x):
        b = self.b
        ret = self.laplace_f(x) / 2 + abs(x) / (4 * b * b) * np.exp(-abs(x) / b)
        return ret

    def Laplace_DV_F(self, x):
        b = self.b
        if x >= 0:
            ret = self.laplace_F(x) / 2 + 0.5 - x / (4 * b) * np.exp(- x / b) - np.exp(-x / b) / 4
        else:
            ret = self.laplace_F(x) / 2 - x / (4 * b) * np.exp(x / b) + np.exp(x / b) / 4
        return ret
