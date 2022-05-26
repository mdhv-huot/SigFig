# Copyright (c) 2022 Mitchell Huot.
# All rights reserved.

# Written by Mitchell Huot <mitchell.huot at mcgill.ca>

'''
Name
    SigFig
Description
    The purpose of this module is to support arithmetic using Significant Figures rules. The values will be kept as
    python floats but will get rounded to the appropriate number of significant figures. The Significant figures will
    be propagated when calculation steps take place.
'''

import math
import statistics


class StrictInt(int):
    """Subclass of int that refuses to coerce non-integer values.
    from https://codereview.stackexchange.com/questions/195375/strictint-python-object-class-that-prohibits-casting-numbers-with-non-integer"""
    def __new__(cls, value):
        if isinstance(value, str):
            for converter in (int, float, complex):
                try:
                    value = converter(value)
                    break
                except ValueError:
                    pass
            else:
                raise ValueError(f"invalid literal for {cls.__name__}(): "
                                 f"{value!r}")
        if value.imag:
            raise ValueError("could not convert value due to non-zero "
                             f"imaginary part: {value!r}")
        quotient, remainder = divmod(value.real, 1)
        if remainder:
            raise ValueError("could not convert value due to non-zero "
                             f"fractional part: {value!r}")
        return super(StrictInt, cls).__new__(cls, int(quotient))


def find_sigfigs_lsf(x: str) -> (int, int):
    '''Returns the number of significant digits and position of the least significant figure (lsf) in a number.
        This takes into account strings formatted in 1.23e+3 format and even strings such as 123.450
       adapted from https://stackoverflow.com/questions/8142676/python-counting-significant-digits'''
    # change all the 'E' to 'e'
    x = x.lower()
    #x = x.replace('-', '')
    if ('e' in x):
        # return the length of the numbers before the 'e'
        string_figure = x.split('e')
        # Remove the negative sign
        string_figure[0] = string_figure[0].replace('-', '')
        # determine significant figures (sf) from length of string, subtract 1 because of decimal
        sf = len(string_figure[0]) - 1
        # Check if there are  digits after decimal
        if len(string_figure[0].split('.')[1]) > 0:
            # find lsf by adding the negative length of the decimal portion plus the exponent
            lsf = -len(string_figure[0].split('.')[1]) + int(string_figure[1])
        # If there are no digits after the decimal lsf is equal to the exponent
        else:
            lsf = int(string_figure[1])
        return sf, lsf
    else:
        # If the value is 0 get significant figures and lsf directly
        if float(x) == 0:
            return len(x.strip('-').replace('.', '')), -len(x.split('.')[1])
        else:
            # Put number into e notation and split at the e
            # NOTE: because of the 8 below, it may do crazy things when it parses 9 sigfigs
            n = f'{float(x):.8e}'.split('e')

            # remove and count the number of removed user added zeroes. (these are sig figs)
            if '.' in x:
                s = x.replace('.', '')
                # number of zeroes to add back in
                l = len(s) - len(s.rstrip('0'))
                # strip off the python added zeroes and add back in the ones the user added
                n[0] = n[0].rstrip('0') + ''.join(['0' for num in range(l)])
            else:
                # the user had no trailing zeroes so just strip them all
                n[0] = n[0].rstrip('0')

        # pass it back to the beginning to be parsed
        return find_sigfigs_lsf('e'.join(n))


class SigFig():
    """Number type that keeps track of significant figures and returns math results according to significant
    figures rules"""
    def __init__(self, value, sf=None, exponent=None):
        """If the value is a string we will determine sig figs and convert to float. If the value is a float
        we need to know how many significant figures take the number of significant figures"""
        if isinstance(value, str):
            if value == '':
                self.value = math.nan
                self.sf = math.inf
                self.lsf = '.'
            if float(value) == 0:
                self.value = float(value)
                _, self.lsf = find_sigfigs_lsf(value)
                self.sf = 0
            else:
                self.value = float(value)
                if sf == math.inf:
                    self.sf = sf
                else:
                    self.sf, self.lsf = find_sigfigs_lsf(value)
        else:
            # check if value in nan
            if type(value) is float and math.isnan(value):
                self.value = math.nan
                self.sf = math.inf
                self.lsf = 'n'
            # check if value is inf
            elif type(value) is float and math.isinf(value):
                self.value = math.inf
                self.sf = math.inf
                self.lsf = 'n'
            else:
                if sf is not None:
                    self.value = value
                    self.sf = sf
                    if exponent:
                        self.lsf = exponent
                    else:
                        self.lsf = find_sigfigs_lsf(f"{self.value:#.{self.sf}g}")[1]
                else:
                    raise ValueError('If input value is a float or int need to specify significant figures explicitly')

    def __repr__(self):
        return f"SigFig({self.value}, {self.sf})"

    def __str__(self):
        # Check if inf
        if self.sf == math.inf:
            return f"{self.value}"
        # Check if 0
        elif self.sf == 0:
            # use abs to prevent showing -0
            return f'{abs(self.value):.{-self.lsf}f}'
        else:
            return f"{self.value:#.{self.sf}g}"

    def __truediv__(self, other):
        if isinstance(other, SigFig):
            result = self.value / other.value
            sig_fig = min(self.sf, other.sf)
            # Check if value is 0
            if sig_fig == 0:
                return SigFig(result, 0, min(self.lsf, other.lsf))
            else:
                return SigFig(result, sig_fig)
        # If overloaded with float or integer take sf from SigFig
        elif isinstance(other, float) or isinstance(other, int):
            result = self.value / other
            sig_fig = self.sf
        else:
            raise TypeError(f"can't multiply SigFig by type {type(other)}")
        return SigFig(result, sig_fig)

    def __rtruediv__(self, other):
        if isinstance(other, SigFig):
            result = other.value / self.value
            sig_fig = min(self.sf, other.sf)
            # Check if value is 0
            if sig_fig == 0:
                return SigFig(result, 0, min(self.lsf, other.lsf))
            else:
                return SigFig(result, sig_fig)
        # If overloaded with float or integer take sf from SigFig
        elif isinstance(other, float) or isinstance(other, int):
            result = other / self.value
            sig_fig = self.sf
        else:
            raise TypeError(f"can't divide SigFig by type {type(other)}")
        return SigFig(result, sig_fig)

    def __floordiv__(self, other):
        if isinstance(other, SigFig):
            result = self.value // other.value
            sig_fig = min(self.sf, other.sf)
            if sig_fig == 0:
                return SigFig(result, 0, min(self.lsf, other.lsf))
            else:
                return SigFig(result, sig_fig)
        # If overloaded with float or integer take sf from SigFig
        elif isinstance(other, float) or isinstance(other, int):
            result = self.value // other
            sig_fig = self.sf
        else:
            raise TypeError(f"can't multiply SigFig by type {type(other)}")

        return SigFig(result, sig_fig)

    def __mod__(self, other):
        if isinstance(other, SigFig):
            result = self.value % other.value
            sig_fig = min(self.sf, other.sf)
        # If overloaded with float or integer take sf from SigFig
        elif isinstance(other, float) or isinstance(other, int):
            result = self.value % other
            sig_fig = self.sf
        else:
            raise TypeError(f"can't multiply SigFig by type {type(other)}")
        return SigFig(result, sig_fig)

    def __mul__(self, other):
        if isinstance(other, SigFig):
            result = self.value * other.value
            sig_fig = min(self.sf, other.sf)
            if sig_fig == 0:
                return SigFig(result, 0, min(self.lsf, other.lsf))
            else:
                return SigFig(result, sig_fig)
        # If overloaded with float or integer take sf from SigFig
        elif isinstance(other, float) or isinstance(other, int):
            result = self.value * other
            sig_fig = self.sf
        else:
            raise TypeError(f"can't multiply SigFig by type {type(other)}")
        return SigFig(result, sig_fig)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, SigFig):
            result = self.value + other.value
            # check if special case (inf or nan)
            if self.lsf == 'n' or other.lsf == 'n':
                return SigFig(result)
            # Get the precision from exponent and round to that precision
            precision = max(self.lsf, other.lsf)
            if precision < 0:
                rounded = f'{result:.{-precision}f}'

                return SigFig(result, find_sigfigs_lsf(rounded)[0])
            else:
                rounded = round(result, -precision)
                try:
                    strict_rounded = StrictInt(rounded)
                    return SigFig(result, find_sigfigs_lsf(str(strict_rounded))[0])
                except ValueError:
                    try:
                        return SigFig(result, find_sigfigs_lsf(str(rounded))[0])
                    except RecursionError:
                        return SigFig(math.nan, math.inf)
        # If overloaded with float or integer take sf from SigFig
        elif isinstance(other, float) or isinstance(other, int):
            result = self.value + other
            sig_fig = self.sf
            return SigFig(result, sig_fig)
        else:
            raise TypeError(f"can't add SigFig by type {type(other)}")

    def __sub__(self, other):
        if isinstance(other, SigFig):
            result = self.value - other.value
            # check if special case (inf or nan)
            if self.lsf == 'n' or other.lsf == 'n':
                return SigFig(result)
            # Get the precision from exponent and round to that precision
            precision = max(self.lsf, other.lsf)
            if precision < 0:
                rounded = f'{result:.{-precision}f}'
                # Check if all values are 0
                check0 = []
                for value in rounded.replace('.', '').replace('-', ''):
                    check0.append(int(value))
                if any(check0):
                    return SigFig(result, find_sigfigs_lsf(rounded)[0])
                else:
                    return SigFig(result, 0, -len(rounded.split('.')[1]))
            else:
                rounded = round(result, -precision)
                try:
                    strict_rounded = StrictInt(rounded)
                    return SigFig(result, find_sigfigs_lsf(str(strict_rounded))[0])
                except ValueError:
                    try:
                        return SigFig(result, find_sigfigs(str(rounded))[0])
                    except RecursionError:
                        return SigFig(math.nan, math.inf)
        # If overloaded with float or integer take sf from SigFig
        elif isinstance(other, float) or isinstance(other, int):
            result = self.value - other
            sig_fig = self.sf
            return SigFig(result, sig_fig)
        else:
            raise TypeError(f"can't subtract SigFig by type {type(other)}")

    def __lt__(self, other):
        return float(str(self)) < float(str(other))

    def __gt__(self, other):
        return float(str(self)) > float(str(other))

    def __ge__(self, other):
        return float(str(self)) >= float(str(other))

    def __le__(self, other):
        return float(str(self)) <= float(str(other))

    def __eq__(self, other):
        # for equality only equal if value and sf are equal
        if self.value == 0 and other.value == 0:
            return True
        elif math.isnan(self.value) or math.isnan(other.value):
            return False
        else:
            return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __pow__(self, power, modulo=None):
        return SigFig(self.value ** power, self.sf)

    def __hash__(self):
        return hash(self.value)

    def __bool__(self):
        return bool(self.value)

    def __neg__(self):
        return SigFig(-self.value, self.sf)

    def __abs__(self):
        if self.value < 0:
            return -SigFig(self.value, self.sf)
        else:
            return self

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def log(self, base=math.e):
        value = math.log(self.value, base)
        return SigFig(value, self.sf + 1)

    def sqrt(self):
        value = math.sqrt(self.value)
        return SigFig(value, self.sf)

    def set_sf(self, value):
        self.sf = value

def isnan(SF):
    if math.isnan(SF.value):
        return True
    else:
        return False


def mean(numbers):
    values = [num.value for num in numbers]
    min_sf = min([num.sf for num in numbers])

    return SigFig(statistics.mean(values), min_sf)



