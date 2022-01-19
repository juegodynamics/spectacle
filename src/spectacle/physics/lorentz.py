from manim import *
from spectacle.manim_extension.utils.paths import point

# from typing import NewType

# FourVector = NewType('FourVector', [float,float,float,float])
# ThreeVector = NewType('ThreeVector', [float,float,float])

# class FourVector():
#     def __init__(self, four_vector: FourVector):
#         self.t = four_vector[0]
#         self.x = four_vector[1]
#         self.y = four_vector[2]
#         self.z = four_vector[3]


def lorentz_x(t: float, x: float, v: float):
    gamma = 1 / np.sqrt(1 - (v ** 2))
    return point(
        gamma * (t - v * x),
        gamma * (x - v * t),
    )


# def lorentz(position: FourVector, velocity: ThreeVector) -> FourVector:
