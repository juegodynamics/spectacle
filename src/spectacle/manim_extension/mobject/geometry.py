from manim import *
from manim.mobject.opengl_compatibility import ConvertToOpenGL
from spectacle.manim_extension.utils.paths import *
import random


class WavyLine(VMobject, metaclass=ConvertToOpenGL):
    def __init__(self, start=LEFT, end=RIGHT, waves=4, width=0.5, **kwargs):
        self.base_line = Line(start=start, end=end)
        super().__init__(**kwargs)
        self.add_curves(start, end, waves, width)

    def add_curves(self, start, end, waves, width):
        for u in range(waves):
            vec = end - start
            one_wavelength = get_wavy_curve_points(
                start=start + vec * (u / waves),
                end=start + vec * ((u + 1) / waves),
                width=width,
            )
            if u == 0:
                self.add_cubic_bezier_curve(*one_wavelength)
            else:
                self.add_cubic_bezier_curve_to(*one_wavelength[1:])

    def get_angle(self):
        return self.base_line.get_angle()


class PerturbedLine(VMobject):
    def __init__(self, start=LEFT, end=RIGHT, disruption=0.2, seed=12345, **kwargs):
        self.base_line = Line(start=start, end=end)
        self.disruption = disruption
        self.seed = seed
        super().__init__(**kwargs)
        self.add_curves()

    def add_curves(self):
        num_subsections = np.floor(self.base_line.get_length() / self.disruption).astype("int")
        random.seed(self.seed)
        for sec in range(num_subsections):
            v = self.base_line
            section_start = v.start + v.get_vector() * (sec / num_subsections)
            section_end = v.start + v.get_vector() * ((sec + 1) / num_subsections)
            angle = self.base_line.get_angle()

            partway_x_alphas = [random.random() * (0.5 + n / 2) for n in range(2)]
            partway_x_points = [
                interpolate_points(section_start, section_end, partway_x_alphas[n])
                for n in range(2)
            ]
            partway_points = [
                partway_x_points[n]
                + (random.random() - 0.5) * self.disruption * get_unit_for_angle(angle + PI / 2)
                for n in range(2)
            ]

            all_perturbed_points = [section_start] + partway_points + [section_end]

            if sec == 0:
                self.add_cubic_bezier_curve(*all_perturbed_points)
            else:
                self.add_cubic_bezier_curve_to(*all_perturbed_points[1:])
