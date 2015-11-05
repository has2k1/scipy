"""
Test series for loess routines.

:author: Pierre GF Gerard-Marchant
:contact: pierregm_at_uga_edu
:date: $Date$
:version: $Id$
"""
__author__ = "Pierre GF Gerard-Marchant ($Author$)"
__version__ = '1.0'
__revision__ = "$Revision$"
__date__     = '$Date$'

import os

import nose
import numpy as np
from numpy.testing import *

from scipy.smooth.loess import loess, loess_anova

data_path, _ = os.path.split(__file__)


class TestLoess2d(TestCase):
    "Test class for lowess."

    def __init__(self, *args, **kwds):
        TestCase.__init__(self, *args, **kwds)
        dfile = os.path.join(data_path, 'madeup_data')
        rfile = os.path.join(data_path, 'madeup_result')

        with open(dfile, 'r') as f:
            f.readline()
            x = np.fromiter(
                (float(v) for v in f.readline().rstrip().split()),
                np.float_).reshape(-1, 2)
            f.readline()
            y = np.fromiter(
                (float(v) for v in f.readline().rstrip().split()),
                np.float_)

        results = []
        with open(rfile, 'r') as f:
            for i in range(8):
                f.readline()
                z = np.fromiter(
                    (float(v) for v in f.readline().rstrip().split()),
                    np.float_)
                results.append(z)

        newdata1 = np.array([[-2.5, 0.0, 2.5], [0., 0., 0.]])
        newdata2 = np.array([[-0.5, 0.5], [0., 0.]])
        madeup = loess(x, y)
        self.d = (x, y, results, newdata1, newdata2, madeup)

    def test_2dbasic(self):
        "2D standard"
        (x, y, results, _, _, madeup) = self.d
        madeup = loess(x, y)
        madeup.model.span = 0.5
        madeup.model.normalize = True
        madeup.fit()
        assert_almost_equal(madeup.outputs.fitted_values, results[0], 5)
        assert_almost_equal(madeup.outputs.enp, 14.9, 1)
        assert_almost_equal(madeup.outputs.residual_scale, 0.9693, 4)

    def test_2d_modflags(self):
        "2D - modification of model flags"
        (x, y, results, _, _, madeup) = self.d
        madeup = loess(x, y)
        madeup.model.span = 0.8
        madeup.model.drop_square_flags = [True, False]
        madeup.model.parametric_flags = [True, False]
        assert_equal(madeup.model.parametric_flags[:2], [1, 0])
        madeup.fit()
        assert_almost_equal(madeup.outputs.fitted_values, results[1], 5)
        assert_almost_equal(madeup.outputs.enp, 6.9, 1)
        assert_almost_equal(madeup.outputs.residual_scale, 1.4804, 4)

    def test_2d_modfamily(self):
        "2D - family modification"
        (_, _, results, _, _, madeup) = self.d
        madeup.model.span = 0.8
        madeup.model.drop_square_flags = [True, False]
        madeup.model.parametric_flags = [True, False]
        madeup.model.family = "symmetric"
        madeup.fit()
        assert_almost_equal(madeup.outputs.fitted_values, results[2], 5)
        assert_almost_equal(madeup.outputs.enp, 6.9, 1)
        assert_almost_equal(madeup.outputs.residual_scale, 1.0868, 4)

    def test_2d_modnormalize(self):
        "2D - normalization modification"
        (_, _, results, _, _, madeup) = self.d
        madeup.model.span = 0.8
        madeup.model.drop_square_flags = [True, False]
        madeup.model.parametric_flags = [True, False]
        madeup.model.family = "symmetric"
        madeup.model.normalize = False
        madeup.fit()
        assert_almost_equal(madeup.outputs.fitted_values, results[3], 5)
        assert_almost_equal(madeup.outputs.enp, 6.9, 1)
        assert_almost_equal(madeup.outputs.residual_scale, 1.0868, 4)

    def test_2d_pred_nostderr(self):
        "2D prediction - no stderr"
        (_, _, results, newdata1, _, madeup) = self.d
        madeup.model.span = 0.5
        madeup.model.normalize = True
        madeup.predict(newdata1, stderror=False)
        assert_almost_equal(madeup.predicted.values, results[4], 5)
        #
        madeup_pred = madeup.predict(newdata1, stderror=False)
        assert_almost_equal(madeup_pred.values, results[4], 5)

    def test_2d_pred_nodata(self):
        "2D prediction - nodata"
        (_, _, _, _, _, madeup) = self.d
        try:
            madeup.predict(None)
        except ValueError:
            pass
        else:
            raise AssertionError, "The test should have failed"

    def test_2d_pred_stderr(self):
        "2D prediction - w/ stderr"
        (_, _, results, _, newdata2, madeup) = self.d
        madeup.model.span = 0.5
        madeup.model.normalize = True
        madeup_pred = madeup.predict(newdata2, stderror=True)
        assert_almost_equal(madeup_pred.values, results[5], 5)
        assert_almost_equal(madeup_pred.stderr, [0.276746, 0.278009], 5)
        assert_almost_equal(madeup_pred.residual_scale, 0.969302, 6)
        assert_almost_equal(madeup_pred.df, 81.2319, 4)
        # Direct access
        madeup.predict(newdata2, stderror=True)
        assert_almost_equal(madeup.predicted.values, results[5], 5)
        assert_almost_equal(madeup.predicted.stderr, [0.276746, 0.278009], 5)
        assert_almost_equal(madeup.predicted.residual_scale, 0.969302, 6)
        assert_almost_equal(madeup.predicted.df, 81.2319, 4)

    def test_2d_pred_confinv(self):
        "2D prediction - confidence"
        (_, _, results, _, newdata2, madeup) = self.d
        madeup.model.span = 0.5
        madeup.model.normalize = True
        madeup.predict(newdata2, stderror=True)
        madeup.predicted.confidence(coverage=0.99)
        assert_almost_equal(madeup.predicted.confidence_intervals.lower,
                            results[6][::3], 5)
        assert_almost_equal(madeup.predicted.confidence_intervals.fit,
                            results[6][1::3], 5)
        assert_almost_equal(madeup.predicted.confidence_intervals.upper,
                            results[6][2::3], 5)
        # Direct access
        confinv = madeup.predicted.confidence(coverage=0.99)
        assert_almost_equal(confinv.lower, results[6][::3], 5)
        assert_almost_equal(confinv.fit, results[6][1::3], 5)
        assert_almost_equal(confinv.upper, results[6][2::3], 5)


class TestLoessGas(TestCase):
    "Test class for lowess."

    def __init__(self, *args, **kwds):
        TestCase.__init__(self, *args, **kwds)
        NOx = np.array([4.818, 2.849, 3.275, 4.691, 4.255, 5.064, 2.118, 4.602,
                        2.286, 0.970, 3.965, 5.344, 3.834, 1.990, 5.199, 5.283,
                        3.752, 0.537, 1.640, 5.055, 4.937, 1.561])
        E = np.array([0.831, 1.045, 1.021, 0.970, 0.825, 0.891, 0.71, 0.801,
                      1.074, 1.148, 1.000, 0.928, 0.767, 0.701, 0.807, 0.902,
                      0.997, 1.224, 1.089, 0.973, 0.980, 0.665])
        gas_fit_E = np.array([0.665, 0.949, 1.224])
        newdata = np.array([0.6650000, 0.7581667, 0.8513333, 0.9445000,
                            1.0376667, 1.1308333, 1.2240000])
        coverage = 0.99

        rfile = os.path.join(data_path, 'gas_result')
        results = []
        with open(rfile, 'r') as f:
            for i in range(8):
                f.readline()
                z = np.fromiter(
                    (float(v) for v in f.readline().rstrip().split()),
                    np.float_)
                results.append(z)
        self.d = (E, NOx, gas_fit_E, newdata, coverage, results)

    def test_1dbasic(self):
        "Basic test 1d"
        (E, NOx, _, _, _, results) = self.d
        gas = loess(E, NOx)
        gas.model.span = 2./3.
        gas.fit()
        assert_almost_equal(gas.outputs.fitted_values, results[0], 6)
        assert_almost_equal(gas.outputs.enp, 5.5, 1)
        assert_almost_equal(gas.outputs.residual_scale, 0.3404, 4)

    def test_1dbasic_alt(self):
        "Basic test 1d - part #2"
        (E, NOx, _, _, _, results) = self.d
        gas_null = loess(E, NOx)
        gas_null.model.span = 1.0
        gas_null.fit()
        assert_almost_equal(gas_null.outputs.fitted_values, results[1], 6)
        assert_almost_equal(gas_null.outputs.enp, 3.5, 1)
        assert_almost_equal(gas_null.outputs.residual_scale, 0.5197, 4)

    def test_1dpredict(self):
        "Basic test 1d - prediction"
        (E, NOx, gas_fit_E, _, _, results) = self.d
        gas = loess(E, NOx, span=2./3.)
        gas.fit()
        gas.predict(gas_fit_E, stderror=False)
        assert_almost_equal(gas.predicted.values, results[2], 6)

    def test_1dpredict_2(self):
        "Basic test 1d - new predictions"
        (E, NOx, _, newdata, _, results) = self.d
        gas = loess(E, NOx, span=2./3.)
        gas.predict(newdata, stderror=True)
        gas.predicted.confidence(0.99)
        assert_almost_equal(gas.predicted.confidence_intervals.lower,
                            results[3][0::3], 6)
        assert_almost_equal(gas.predicted.confidence_intervals.fit,
                            results[3][1::3], 6)
        assert_almost_equal(gas.predicted.confidence_intervals.upper,
                            results[3][2::3], 6)

    def test_anova(self):
        "Tests anova"
        (E, NOx, _, _, _, results) = self.d
        gas = loess(E, NOx, span=2./3.)
        gas.fit()
        gas_null = loess(E, NOx, span=1.0)
        gas_null.fit()
        gas_anova = loess_anova(gas, gas_null)
        gas_anova_theo = results[4]
        assert_almost_equal(gas_anova.dfn, gas_anova_theo[0], 5)
        assert_almost_equal(gas_anova.dfd, gas_anova_theo[1], 5)
        assert_almost_equal(gas_anova.F_value, gas_anova_theo[2], 5)
        assert_almost_equal(gas_anova.Pr_F, gas_anova_theo[3], 5)

    def test_failures(self):
        "Tests failures"
        (E, NOx, gas_fit_E, _, _, _) = self.d
        gas = loess(E, NOx, span=2./3.)
        # This one should fail (all parametric)
        gas.model.parametric_flags = True
        self.assertRaises(ValueError, gas.fit)
        # This one also (all drop_square)
        gas.model.drop_square_flags = True
        self.assertRaises(ValueError, gas.fit)
        gas.model.degree = 1
        self.assertRaises(ValueError, gas.fit)
        # This one should not (revert to std)
        gas.model.parametric_flags = False
        gas.model.drop_square_flags = False
        gas.model.degree = 2
        gas.fit()
        # Now, for predict .................
        gas.predict(gas_fit_E, stderror=False)
        # This one should fail (extrapolation & blending)
        self.assertRaises(ValueError,
                          gas.predict, gas.predicted.values, stderror=False)
        # But this one should not ..........
        gas.predict(gas_fit_E, stderror=False)


########################################################################
if __name__ == '__main__':
    nose.run(argv=['', __file__])
