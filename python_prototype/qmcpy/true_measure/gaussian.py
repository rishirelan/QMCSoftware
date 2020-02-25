""" Definition of Gaussian, a concrete implementation of TrueMeasure """

from ._true_measure import TrueMeasure
from ..util import TransformError
from numpy import array, sqrt, eye, inner,dot
from numpy.linalg import cholesky
from scipy.stats import norm


class Gaussian(TrueMeasure):
    """ Gaussian (Normal) TrueMeasure """

    parameters = ['mean', 'covariance']

    def __init__(self, distribution, mean=0, covariance=1):
        """
        Args:
            distribution (DiscreteDistribution): DiscreteDistribution instance
            mean (float): mu for Normal(mu,sigma^2)
            covariance (float/ndarray): sigma^2 for Normal(mu,sigma^2)
                Note: an ndarray should be of shape dimension x dimension
                      a float value is equivalent to float_val*eye(dimension)
        """
        self.distribution = distribution
        self.mean = array(mean)
        self.covariance = array(covariance)
        d = distribution.dimension
        cov_d = self.covariance if self.covariance.shape==(d,d) else self.covariance*eye(d)
        self.sigma = cholesky(cov_d)
        super().__init__()
    
    def gen_samples(self, *args, **kwargs):
        """
        Generate samples from the DiscreteDistribution object
        and transform them to mimic TrueMeasure samples
        
        Args:
            *args (tuple): Ordered arguments to self.distribution.gen_samples
            **kwrags (dict): Keyword arguments to self.distribution.gen_samples
        
        Returns:
            tf_samples (ndarray): samples from the DiscreteDistribution object transformed
                                  to appear like the TrueMeasure object
        """
        samples = self.distribution.gen_samples(*args,**kwargs)
        if self.distribution.mimics == 'StdGaussian':
            # shift and stretch
            tf_samples = self.mean + inner(samples,self.sigma)
        elif self.distribution.mimics == "StdUniform":
            # inverse CDF then shift and stretch
            tf_samples = self.mean + inner(norm.ppf(samples),self.sigma)
        else:
            raise TransformError(\
                'Cannot transform samples mimicing %s to Gaussian'%self.distribution.mimics)
        return tf_samples

    def transform_g_to_f(self, g):
        """
        Transform the g, the origianl integrand, to f,
        the integrand after transforming DiscreteDistribution samples
        to mimic the TrueMeasure object. 
        
        Args:
            g (method): original integrand
        
        Returns:
            f (method): transformed integrand
        """
        if self.distribution.mimics in ['StdUniform','StdGaussian']:
            # no weight
            f = lambda tf_samples: g(tf_samples)
        else:
            raise TransformError(\
                'Cannot transform samples mimicing %s to Gaussian'%self.distribution.mimics)
        return f
