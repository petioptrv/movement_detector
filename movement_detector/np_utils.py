import numpy as np


def get_dtype(value: np.number):
    """
    Returns the largest numpy value-type capable of representing the passed-in
    value. If the largest float needed, value must be a float. If signed numbers
    are needed, value must be passed as negative (note that floats are always
    signed).

    Parameters
    ----------
    value : numeric value
        The value to be represented.

    Returns
    -------
    NumPy dtype
    """
    np_floats = [np.float16, np.float32, np.float64, np.float128]
    np_uints = [np.uint8, np.uint16, np.uint32, np.uint64]
    np_ints = [np.int8, np.int16, np.int32, np.int64]
    if isinstance(value, float):
        if value > 0:
            for float_ in np_floats:
                if np.finfo(float_).max > value:
                    return float_
        else:
            for float_ in np_floats:
                if np.finfo(float_).min < value:
                    return float_
    elif value > 0:
        for uint_ in np_uints:
            if np.iinfo(uint_).max > value:
                return uint_
    else:
        for int_ in np_ints:
            if np.iinfo(int_).min < value:
                return int_
