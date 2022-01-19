from spectacle import *

import random


def make_random_bezier(start=2 * DL, end=2 * UR, stroke_width=DEFAULT_STROKE_WIDTH):
    x_range = [2 * start[0], 2 * end[0]]
    x_range.sort()

    y_range = [2 * start[1], 2 * end[1]]
    y_range.sort()

    pt1 = point(random.uniform(*x_range), random.uniform(*y_range))
    pt2 = point(random.uniform(*x_range), random.uniform(*y_range))
    return CubicBezier(start, pt1, pt2, end, stroke_width=stroke_width).set_stroke(opacity=0.1)


class Action(Scene):
    def construct(self):
        RAINBOW.reverse()

    def color_for_path(self, path):
        length = path.get_arc_length()
        color_index_partial: float = (len(RAINBOW) - 1) * (
            ((length - self.shortest_path) / (self.longest_path - self.shortest_path)) ** 0.5
        )
        first_index: int = int(np.floor(color_index_partial))
        second_index: int = int(np.ceil(color_index_partial))

        if first_index < 0:
            color = RAINBOW[0]
        elif second_index >= len(RAINBOW):
            color = RAINBOW[-1]
        else:
            color = interpolate_color(
                RAINBOW[first_index], RAINBOW[second_index], second_index - color_index_partial
            )
        return color

    def opacity_for_path(self, path):
        length = path.get_arc_length()
        ratio: float = 0.25 * (
            1
            - (((length - self.shortest_path) / (self.longest_path - self.shortest_path)) ** 0.05)
        )

        if ratio < 0:
            return 0
        elif ratio >= 1:
            return 1
        return ratio

    def scene1(self):
        paths: Iterable[Iterable[CubicBezier]] = []
        self.shortest_path: float = 0.0
        self.longest_path: float = 0.0

        num_paths = 50
        for n in range(num_paths):
            path = make_random_bezier()

    def scene2(self):
        random.seed(54321)
        paths: Iterable[Iterable[CubicBezier]] = []
        self.shortest_path: float = 0.0
        self.longest_path: float = 0.0
        path_descendants = 13

        for n in range(path_descendants):
            next_paths = [
                make_random_bezier(stroke_width=DEFAULT_STROKE_WIDTH / 2) for _ in range(2 ** n)
            ]

            # self.add(*[p for p in next_paths])
            self.play(*[Create(p) for p in next_paths], run_time=0.5)

            paths.append(next_paths)
            for path in next_paths:

                length = path.get_arc_length()
                if n == 0:
                    self.shortest_path = length
                    self.longest_path = length
                else:
                    if length > self.longest_path:
                        self.longest_path = length
                    if length < self.shortest_path:
                        self.shortest_path = length
        self.wait()

        # for path_group in paths:
        self.play(
            *[
                k.animate.set_stroke(opacity=opacity_for_path(k), color=color_for_path(k))
                for n in paths
                for k in n
            ],
            run_time=0.5,
        )

        self.wait()
