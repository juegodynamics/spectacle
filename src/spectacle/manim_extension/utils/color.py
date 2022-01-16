from manim import *
import colorsys

RAINBOW = [PURPLE, PURE_BLUE, PURE_GREEN, YELLOW, ORANGE, PURE_RED]


def shift_discrete_gradient(colors, delta: int):
    return list(map(lambda n: colors[(n + delta) % (len(colors) - 1)], range(len(colors))))


class ColorUpdater:
    def __init__(self) -> None:
        self.time_state = 0

    def rotate_color(self, c, t):
        [r, g, b] = hex_to_rgb(c)
        [h, s, v] = colorsys.rgb_to_hsv(r, g, b)

        new_c = colorsys.hsv_to_rgb((h + t) % 1, s, v)
        return rgb_to_hex(new_c)

    def update_color(self, sq, dt):
        self.time_state = self.time_state + (dt / 60)
        sq.set_color_by_gradient([self.rotate_color(n, self.time_state) for n in RAINBOW])
