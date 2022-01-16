from typing import Tuple
from manim import *


class BoundNumberPlane(NumberPlane):
    """Creates a cartesian plane like NumberPlane,
    but not restricted to rectangular boundary

    Parameters
    ----------
    boundary_shape:

    """

    def __init__(self, bounday_shape: VMobject, **kwargs):
        self.boundary_shape = bounday_shape
        super().__init__(**kwargs)

    def _get_lines_parallel_to_axis(
        self,
        axis_parallel_to: NumberLine,
        axis_perpendicular_to: NumberLine,
        freq: float,
        ratio_faded_lines: int,
        **kwargs,
    ) -> Tuple[VGroup, VGroup]:

        line = Line(axis_parallel_to.get_start(), axis_parallel_to.get_end())
        if ratio_faded_lines == 0:  # don't show faded lines
            ratio_faded_lines = 1  # i.e. set ratio to 1
        step = (1 / ratio_faded_lines) * freq
        lines1 = VGroup()
        lines2 = VGroup()
        unit_vector_axis_perp_to = axis_perpendicular_to.get_unit_vector()

        # need to unpack all three values
        x_min, x_max, _ = axis_perpendicular_to.x_range

        # account for different axis scalings (logarithmic), where
        # negative values do not exist and [-2 , 4] should output lines
        # similar to [0, 6]
        if axis_perpendicular_to.x_min > 0 and x_min < 0:
            x_min, x_max = (0, np.abs(x_min) + np.abs(x_max))

        # min/max used in case range does not include 0. i.e. if (2,6):
        # the range becomes (0,4), not (0,6).
        ranges = (
            np.arange(0, min(x_max - x_min, x_max), step),
            np.arange(0, max(x_min - x_max, x_min), -step),
        )

        for inputs in ranges:
            for k, x in enumerate(inputs):
                new_line = line.copy()
                new_line.shift(unit_vector_axis_perp_to * x)
                if k % ratio_faded_lines == 0:
                    lines1.add(new_line)
                else:
                    lines2.add(new_line)
        return lines1, lines2
