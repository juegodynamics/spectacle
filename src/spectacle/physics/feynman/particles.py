from typing import Iterable
from manim import *
from spectacle.manim_extension.mobject.geometry import WavyLine
from spectacle.manim_extension.utils.paths import point

# __all__ = [
#     "ELECTRON",
#     "PHOTON",
#     "Fermion",
#     "ArcFermion",
#     "Photon",
#     "MidpointNormalLabel",
# ]

ELECTRON = "e"
PHOTON = "\gamma"
GLUON = "g"
QUARK = "q"


class Particle(VGroup):
    def __init__(self, *particle_objects: list, label="", label_color, **kwargs):
        self.particle_objects = list(particle_objects)
        if not (label == ""):
            self.particle_objects.append(
                MidpointNormalLabel(label, line=self.line, color=label_color)
            )
        super().__init__(*self.particle_objects, **kwargs)

    def get_interact_animation(self):
        return AnimationGroup(*[Create(n) for n in self.particle_objects])


class Fermion(Particle):
    def __init__(
        self,
        start: np.ndarray = LEFT,
        end=RIGHT,
        color=WHITE,
        angle=0,
        label="",
        label_color=WHITE,
        tip_alpha=0.5,
        **kwargs,
    ):
        self.line = Line(start=ORIGIN, end=RIGHT, color=color, **kwargs)

        # print({"start": start, "end": end, "angle": angle})
        self.arc = ArcBetweenPoints(start, end, angle=angle)
        self.line.apply_function(lambda p: self.arc.point_from_proportion(p[0]))

        # linear_angle = self.line.get_angle()
        # perp = point(-np.sin(linear_angle), np.cos(linear_angle))
        # normal = self.rad * perp / np.linalg.norm(perp)

        # def transform_arc(p):
        #     x, y = p[0], p[1]
        #     new_p = self.arc.point_from_proportion(x)
        #     vec_to_center = new_p - self.arc.get_center()
        #     return new_p + y * ((1 - 2 * angle / PI) * normal + (2 * angle / PI) * vec_to_center)

        tip_scale = tip_alpha
        if tip_alpha > 0.5:
            tip_scale = 1 - tip_alpha

        self.midarrow_tip = (
            Triangle(color=color, fill_opacity=1)
            .move_to(self.line.point_from_proportion(tip_alpha))
            .scale(0.035 * self.line.get_length() * (tip_scale * 2))
            .rotate(angle_of_vector(self.line.get_vector()) - PI / 2)
        )

        super().__init__(
            *[self.line, self.midarrow_tip], label=label, label_color=label_color, **kwargs
        )


class Electron(Fermion):
    def __init__(
        self,
        show_label=False,
        **kwargs,
    ):
        label = ""
        if show_label:
            label = ELECTRON

        super().__init__(label=label, **kwargs)

    def interact_animation(self):
        return super().interact_animation()


FLAVOR_UP = "up"
FLAVOR_DOWN = "down"
FLAVOR_TOP = "top"
FLAVOR_BOTTOM = "bottom"
FLAVOR_CHARM = "charm"
FLAVOR_STRANGE = "strange"


class Quark(Fermion):
    def __init__(
        self,
        show_label=False,
        flavor=FLAVOR_UP,
        color=RED,
        color_charge=RED,
        tip_alpha=0.5,
        **kwargs,
    ):
        self.flavor = flavor
        self.color_charge = color_charge
        label = ""
        if show_label:
            label = QUARK

        super().__init__(label=label, color=color, tip_alpha=tip_alpha, **kwargs)

    def interact_animation(self):
        return super().interact_animation()


# class ArcFermion(VGroup):
# def __init__(
#     self,
#     start: np.ndarray = LEFT,
#     end=RIGHT,
#     angle=0,
#     stroke=0.01,
#     color=WHITE,
#     label="",
#     label_color=WHITE,
#     **kwargs,
# ):
#     self.rad = stroke / 2
#     self.line = Line(start=start, end=end, color=color, **kwargs)
#     self.arc = ArcBetweenPoints(start, end, angle=angle)
#     linear_angle = self.line.get_angle()
#     perp = point(-np.sin(linear_angle), np.cos(linear_angle))
#     normal = self.rad * perp / np.linalg.norm(perp)

#     def transform_arc(p):
#         x, y = p[0], p[1]
#         new_p = self.arc.point_from_proportion(x)
#         vec_to_center = new_p - self.arc.get_center()
#         return new_p + y * ((1 - 2 * angle / PI) * normal + (2 * angle / PI) * vec_to_center)

#     self.body = Polygon(
#         point(0, -self.rad),
#         point(0, self.rad),
#         point(1, self.rad),
#         point(1, -self.rad),
#         color=color,
#         fill_opacity=1,
#     ).apply_function(transform_arc)

#     vec_to_center = self.arc.point_from_proportion(0.5) - self.line.get_midpoint()
#     actual_arc_midpoint = self.arc.point_from_proportion(0.5) - vec_to_center * stroke * 4

#     self.midarrow_tip = (
#         Triangle(color=color, fill_opacity=1)
#         .move_to(actual_arc_midpoint)
#         .scale(0.035 * self.line.get_length())
#         .rotate(angle_of_vector(self.line.get_vector()) - PI / 2)
#     )
#     self.union = Union(self.body, self.midarrow_tip, color=color, fill_opacity=1)
#     # self.union = self.body

#     particle_objects = [self.union]

#     if not (label == ""):
#         particle_objects.append(
#             MidpointNormalLabel(label, line=self.line, color=label_color, **kwargs)
#         )

#     super().__init__(*particle_objects, **kwargs)


class Photon(Particle):
    def __init__(
        self,
        start=LEFT,
        end=RIGHT,
        waves=4,
        width=0.5,
        angle=0,
        color=WHITE,
        show_label=False,
        label_color=WHITE,
        **kwargs,
    ):
        self.line = Line(start=start, end=end)
        self.curve = WavyLine(
            start=ORIGIN,
            end=RIGHT,
            waves=waves * int(np.ceil(np.linalg.norm(end - start))),
            width=width,
            color=color,
        )

        self.arc = ArcBetweenPoints(start, end, angle=angle)

        def transform_arc(p):
            x, y = p[0], p[1]
            new_p = self.arc.point_from_proportion(x)
            vec_to_center = new_p - self.arc.get_center()

            linear_angle = self.line.get_angle()
            perp = point(-np.sin(linear_angle), np.cos(linear_angle))
            normal = perp / np.linalg.norm(perp)

            return new_p + y * ((1 - 2 * angle / PI) * normal + (2 * angle / PI) * vec_to_center)

        self.curve.apply_function(transform_arc)

        label = {True: PHOTON}.get(show_label, "")

        super().__init__(*[self.curve], label=label, label_color=label_color, **kwargs)


class Gluon(Particle):
    def __init__(
        self,
        start=LEFT,
        end=RIGHT,
        angle=0,
        color=WHITE,
        anti_color=WHITE,
        show_label=False,
        label_color=WHITE,
        waves_per_unit=8,
        **kwargs,
    ):
        self.line = Line(start=start, end=end)
        self.waves_per_unit = waves_per_unit

        self.curve = ParametricFunction(
            self.gluon_parametric_func, t_range=np.array([0, self.line.get_length()])
        ).set_color_by_gradient([color, anti_color, color, anti_color, color])

        # self.arc = ArcBetweenPoints(start, end, angle=angle)

        # def transform_arc(p):
        #     x, y = p[0], p[1]
        #     if x > 1:
        #         x = 1
        #     new_p = self.arc.point_from_proportion(x)
        #     vec_to_center = new_p - self.arc.get_center()

        #     linear_angle = self.line.get_angle()
        #     perp = point(-np.sin(linear_angle), np.cos(linear_angle))
        #     normal = perp / np.linalg.norm(perp)

        #     return new_p + y * ((1 - 2 * angle / PI) * normal + (2 * angle / PI) * vec_to_center)

        # self.curve.apply_function(transform_arc)

        label = {True: GLUON}.get(show_label, "")

        super().__init__(*[self.curve], label=label, label_color=label_color, **kwargs)

    def gluon_parametric_func(self, t):
        length = self.line.get_length()
        theta = self.line.get_angle()

        wave_freq = (2 * np.floor(self.waves_per_unit * length) - 1) * PI / length
        stretch = 15

        x = (1 + stretch * t - np.cos(wave_freq * t)) / 1.03
        y = np.sin(wave_freq * t)

        amp = 1 / ((1 / length) + stretch)
        base_path = amp * np.matmul(rotation_about_z(theta), np.array([x, y, 0]))
        return base_path + self.line.get_start()


class Boson(VGroup):
    def __init__(
        self,
        start: np.ndarray = LEFT,
        end=RIGHT,
        color=WHITE,
        label="",
        label_color=WHITE,
        **kwargs,
    ):

        self.line = DashedLine(start=start, end=end, color=color, **kwargs)
        super().__init__(self.line, label=label, label_color=label_color, **kwargs)


class Chain(VGroup):
    def __init__(self, vmobject, *points, **kwargs):
        self.particle_objects = []
        for index in range(len(points) - 1):
            self.particle_objects.append(
                vmobject(start=points[index], end=points[index + 1], **kwargs)
            )
        super().__init__(*self.particle_objects)

    def interact_animation(self):
        return AnimationGroup(*[n.get_interact_animation() for n in self.particle_objects])

    def get_interact_animation(self):
        return AnimationGroup(*[n.get_interact_animation() for n in self.particle_objects])


class MidpointNormalLabel(MathTex):
    def __init__(self, *text_strings, line: VMobject, **kwargs):
        super().__init__(*text_strings, **kwargs)
        angle = line.get_angle()
        midpoint = line.get_midpoint()
        normal_point = np.array([-np.sin(angle), np.cos(angle), 0])
        if np.abs(midpoint[0] - normal_point[0]) < np.abs(midpoint[0] + normal_point[0]):
            normal_point = -1 * normal_point
        self.next_to(midpoint, normal_point)
