from spectacle import *


def test_as_point():
    p = as_point([1, 1, 0])
    assert p == np.array([1, 1, 0])
