from spectacle import *


def test__3d():
    p = _3d([1, 1, 0])
    assert p == np.array([1, 1, 0])
