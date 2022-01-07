from manim import *

RAINBOW = [PURPLE, PURE_BLUE, PURE_GREEN, YELLOW, ORANGE, PURE_RED]


def shift_discrete_gradient(colors, delta: int):
    return list(map(lambda n: colors[(n + delta) % (len(colors) - 1)], range(len(colors))))
