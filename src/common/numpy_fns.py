import numpy as np


def get_dtype(value):
    """
    Returns the largest numpy value-type capable of representing the passed-in value.
    If the largest float needed, value must be a float. If signed numbers are needed, value must
    be passed as negative (note that floats are always signed).
    :param value: The value to be represented.
    :return:
    """
    np_floats = [np.float16, np.float32, np.float64, np.float128]
    np_uints = [np.uint8, np.uint16, np.uint32, np.uint64]
    np_ints = [np.int8, np.int16, np.int32, np.int64]
    if type(value) is float:
        if value > 0:
            for _float in np_floats:
                if np.finfo(_float).max > value:
                    return _float
        else:
            for _float in np_floats:
                if np.finfo(_float).min < value:
                    return _float
    elif value > 0:
        for _uint in np_uints:
            if np.iinfo(_uint).max > value:
                return _uint
        else:
            for _int in np_ints:
                if np.iinfo(_int).min < value:
                    return _int
