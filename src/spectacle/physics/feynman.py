from manim import *
from ..manim_extension.mobject.geometry import WavyLine

__all__ = [
    "ELECTRON",
    "PHOTON",
    "ChargedParticle",
    "SolidChargedParticle",
    "Photon",
    "MidpointNormalLabel",
]

ELECTRON = "e^{-}"
PHOTON = "\gamma"


class ChargedParticle(VGroup):
    def __init__(
        self,
        start: np.ndarray = LEFT,
        end=RIGHT,
        color=WHITE,
        label="",
        label_color=WHITE,
        **kwargs,
    ):
        self.line = Line(start=start, end=end, color=color, **kwargs)
        self.midarrow_tip = (
            Triangle(color=color, fill_opacity=1)
            .move_to(self.line.get_midpoint())
            .scale(0.035 * self.line.get_length())
            .rotate(angle_of_vector(self.line.get_vector()) - PI / 2)
        )

        vmobjects = [self.line, self.midarrow_tip]

        if not (label == ""):
            vmobjects.append(
                MidpointNormalLabel(label, line=self.line, color=label_color, **kwargs)
            )

        super().__init__(*vmobjects, **kwargs)


class SolidChargedParticle(VGroup):
    def __init__(
        self,
        start=LEFT,
        end=RIGHT,
        stroke=0.01,
        color=WHITE,
        label="",
        label_color=WHITE,
        **kwargs,
    ):
        self.line = Line(start=start, end=end, color=color, **kwargs)

        base_rect = Rectangle(height=self.line.get_length(), width=stroke)
        self.rect = self.align_with_line(base_rect).rotate(PI)

        self.midarrow_tip = self.align_with_line(Triangle()).scale(0.035 * self.line.get_length())

        vmobjects = [Union(self.rect, self.midarrow_tip, fill_opacity=1, color=color)]

        if not (label == ""):
            vmobjects.append(
                MidpointNormalLabel(label, line=self.line, color=label_color, **kwargs)
            )

        super().__init__(*vmobjects, **kwargs)

    def align_with_line(self, mobject: Mobject):
        return mobject.move_to(self.line.get_midpoint()).rotate(
            angle_of_vector(self.line.get_vector()) - PI / 2
        )


class Photon(VGroup):
    def __init__(
        self,
        start=LEFT,
        end=RIGHT,
        waves=4,
        width=0.5,
        color=WHITE,
        label="",
        label_color=WHITE,
        **kwargs,
    ):
        self.line = WavyLine(start=start, end=end, waves=waves, width=width, color=color, **kwargs)
        vmobjects = [self.line]
        if not (label == ""):
            vmobjects.append(
                MidpointNormalLabel(label, line=self.line, color=label_color, **kwargs)
            )
        super().__init__(*vmobjects, **kwargs)


class MidpointNormalLabel(MathTex):
    def __init__(self, *text_strings, line: VMobject, **kwargs):
        super().__init__(*text_strings, **kwargs)
        angle = line.get_angle()
        midpoint = line.get_midpoint()
        self.next_to(midpoint, np.array([-np.sin(angle), np.cos(angle), 0]))
