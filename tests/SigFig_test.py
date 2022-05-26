import unittest
import math
from SigFig import SigFig, isnan

class TestSigFit(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(SigFig('50.00'), SigFig('50.00'))

    def test_gt(self):
        self.assertTrue(SigFig('2.00') > SigFig(1.000001, 3))

    def test_gt_close(self):
        self.assertFalse(SigFig(1.0009, 3) > SigFig(1.00, 3))

    def test_float_equal(self):
        self.assertEqual(SigFig(50.00, 4), SigFig('50.00'))

    def test_not_equal(self):
        self.assertNotEqual(SigFig('50.00'), SigFig('50.000'))

    def test_float_not_equal(self):
        self.assertNotEqual(SigFig(50, 4), SigFig(50, 5))

    def test_add(self):
        self.assertEqual(SigFig('10.21') + SigFig('0.8') + SigFig('256'), SigFig('267'))

    def test_mul(self):
        self.assertEqual(SigFig('6.2') * SigFig('14.6'), SigFig('91'))

    def test_multi_step(self):
        self.assertEqual(SigFig('7.87') / (SigFig('16.1') - SigFig('8.44')), SigFig('1.0'))

    def test_squared(self):
        self.assertEqual(SigFig('6.23') **2 * SigFig(math.pi, 8) * SigFig('4.630'), SigFig('565'))

    def test_sub_small(self):
        self.assertEqual(SigFig(0.9982399038924058, 3) - SigFig('0.9978'), SigFig('0.000'))

    def test_sub_lowprec(self):
        self.assertEqual(SigFig('0.4') - SigFig('0.1'), SigFig('0.3'))

    def test_low_prec(self):
        self.assertEqual(SigFig('1')*(SigFig('0.5')-SigFig('0.4')-SigFig('0.1')), SigFig('0.0'))

    def test_negative(self):
        self.assertEqual(SigFig('-4.8').sf, 2)

    def test_abs_neg(self):
        self.assertEqual(abs(SigFig('-4.8')), SigFig('4.8'))

    def test_abs_pos(self):
        self.assertEqual(abs(SigFig('4.8')), SigFig('4.8'))

    def test_inf_add(self):
        self.assertEqual(SigFig(math.inf) + SigFig('4.8'), SigFig(math.inf))

    def test_inf_sub(self):
        self.assertEqual(SigFig(math.inf) - SigFig('4.8'), SigFig(math.inf))

    def test_inf_mul(self):
        self.assertEqual(SigFig(math.inf) * SigFig('4.8'), SigFig(math.inf))

    def test_div_inf(self):
        self.assertEqual(SigFig(math.inf) / SigFig('4.8'), SigFig(math.inf))

    def test_div_inf0(self):
        self.assertEqual(SigFig('4.8') / SigFig(math.inf), SigFig(0, sf=0))

    def test_nan_add(self):
        self.assertEqual(isnan(SigFig(math.nan) + SigFig('4.8')), True)

    def test_nan_sub(self):
        self.assertEqual(isnan(SigFig(math.nan) - SigFig('4.8')), True)

    def test_nan_mul(self):
        self.assertEqual(isnan(SigFig(math.nan) * SigFig('4.8')), True)

    def test_nan_inf(self):
        self.assertEqual(isnan(SigFig(math.nan) / SigFig('4.8')), True)

    def test_bool_num(self):
        self.assertEqual(bool(SigFig('4.8')), True)

    def test_bool_0(self):
        self.assertEqual(bool(SigFig(0, 0)), False)

    def test_bool_nan(self):
        self.assertEqual(bool(SigFig(math.nan)), True)

    def test_bool_nan(self):
        self.assertEqual(bool(SigFig(math.inf)), True)

    def test_mult_int(self):
        self.assertEqual(SigFig('5.00') * 4, SigFig('20.0'))

    def test_div_int(self):
        self.assertEqual(SigFig('5.00') / 5, SigFig('1.00'))

    def test_add_int(self):
        self.assertEqual(SigFig('5.00') + 5, SigFig('10.0'))

    def test_sub_int(self):
        self.assertEqual(SigFig('5.00') - 4 , SigFig('1.00'))




if __name__ == '__main__':
    unittest.main()
