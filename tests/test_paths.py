from spectacle import *


def test_point():
    p = point([1, 1, 0])
    assert p == np.array([1, 1, 0])
