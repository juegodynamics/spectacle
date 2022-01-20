from colour import Color
from typing import Callable, Sequence, Tuple
from manim import *

from ...manim_extension.utils.paths import _3d
from ...manim_extension.utils.consts import BOLD_STROKE_WIDTH


class FTLError(Exception):
    def __init__(self, speed: float) -> None:
        super().__init__(f"Attempted shift into speed {speed}c; cannot go faster than light")


def make_gamma(v: float):
    return 1 / np.sqrt(1 - (v ** 2))


def make_lorentz_transformation(v: float) -> Callable[[np.ndarray], np.ndarray]:
    if abs(v) >= 1:
        raise FTLError(abs(v))
    gamma = make_gamma(v)
    return lambda p: _3d(
        gamma * (p[0] - v * p[1]),
        gamma * (p[1] - v * p[0]),
    )


class SpacetimeAxes(NumberPlane):
    """Creates a (2D) Minkowski plane with background lines and supports Lorentz transformations.

    Parameters
    ----------
    x_range
        The ``[x_min, x_max, x_step]`` values of the plane in the horizontal direction.
    y_range
        The ``[y_min, y_max, y_step]`` values of the plane in the vertical direction.
    x_length
        The width of the plane.
    y_length
        The height of the plane.
    background_line_style
        Arguments that influence the construction of the background lines of the plane.
    faded_line_style
        Similar to :attr:`background_line_style`, affects the construction of the scene's background lines.
    faded_line_ratio
        Determines the number of boxes within the background lines: :code:`2` = 4 boxes, :code:`3` = 9 boxes.
    make_smooth_after_applying_functions
        Currently non-functional.
    kwargs : Any
        Additional arguments to be passed to :class:`Axes`.

    .. note::

        If :attr:`x_length` or :attr:`y_length` are not defined, the plane automatically adjusts its lengths based
        on the :attr:`x_range` and :attr:`y_range` values to set the ``unit_size`` to 1.

    Examples
    --------

    .. manim:: NumberPlaneExample
        :save_last_frame:

        class SpacetimeAxesDemo(Scene):
            def construct(self):
                spacetime = (
                    Spacetime()
                    .add_worldline_from_coords("main", [0, 0], [3, 5])
                    .add_event_to_worldline("event1", "main", 0.4)
                    .add_event_to_worldline("event2", "main", 0.8)
                    .add_event_projection("event1")
                    .add_event_projection("event2")
                    .apply_lorentz_transformation(-0.2)
                )

                shifted_spacetime = (
                    spacetime.copy()
                    .apply_lorentz_transformation(0.2)
                    .set_axis_labels(r"x^\prime", r"ct^\prime")
                )

                self.add(spacetime)
                self.play(Transform(spacetime, shifted_spacetime), run_time=8)
    """

    def __init__(
        self,
        x_range: Optional[Sequence[float]] = (
            -5,
            5,
            1,
        ),
        y_range: Optional[Sequence[float]] = (
            0,
            5,
            1,
        ),
        x_length: Optional[float] = None,
        y_length: Optional[float] = None,
        background_line_style: Optional[dict] = None,
        faded_line_style: Optional[dict] = None,
        faded_line_ratio: int = 1,
        make_smooth_after_applying_functions: bool = True,
        transform_tolerance: float = 0.01,
        **kwargs,
    ):
        self.__velocity__ = 0
        self.__prior_velocity__ = 0
        self.__lorentz_transformation__ = make_lorentz_transformation(self.get_relative_velocity())
        self.__lorentz_transformation_to_rest__ = make_lorentz_transformation(
            -1 * self.get_relative_velocity()
        )
        self.__called_from__: Union[str, None] = None
        self.__transform_tolerance__ = transform_tolerance
        self.__rest_axes__ = None
        super().__init__(
            x_range=x_range,
            y_range=y_range,
            x_length=x_length,
            y_length=y_length,
            background_line_style=background_line_style,
            faded_line_style=faded_line_style,
            faded_line_ratio=faded_line_ratio,
            make_smooth_after_applying_functions=make_smooth_after_applying_functions,
            **kwargs,
        )
        self.__rest_axes__ = self.copy()

    def lorentz_transformation(self, point: Sequence[float]):
        return self.__lorentz_transformation__(point)

    def lorentz_transformation_to_rest(self, point: Sequence[float]):
        return self.__lorentz_transformation_to_rest__(point)

    def __update_velocity__(self, new_velocity: float):
        self.__prior_velocity__ = self.__velocity__
        self.__velocity__ = new_velocity
        self.__lorentz_transformation__ = make_lorentz_transformation(self.get_relative_velocity())
        self.__lorentz_transformation_to_rest__ = make_lorentz_transformation(self.__velocity__)
        return self

    def get_velocity(self):
        return self.__velocity__

    def get_relative_velocity(self):
        v = self.__prior_velocity__
        u = -self.__velocity__
        return (v + u) / (1 + v * u)

    def apply_lorentz_transformation(self, velocity: float):

        self.__update_velocity__(velocity)

        # prior_origin = .get_origin()
        # new_origin = self..get_origin()
        # return self.shift(new_origin - prior_origin)
        return self.apply_function(self.lorentz_transformation)

    @override_animate(apply_lorentz_transformation)
    def _apply_lorentz_transformation_animation(self, velocity: float, anim_args=None):
        anim_args = anim_args if anim_args is not None else {}
        original = self.copy()
        self.apply_lorentz_transformation(velocity)
        return original.become(self)

    def apply_function(self, function):
        self.__called_from__ = self.apply_function.__name__
        out = super().apply_function(function)
        self.__called_from__ = None
        return out

    def get_rest_axes(self):
        return self.__rest_axes__

    def shift(self, *vectors: np.ndarray):
        if self.__rest_axes__ is not None:
            self.__rest_axes__.shift(*vectors)
        return super().shift(*vectors)

    def apply_points_function_about_point(self, func, about_point=None, about_edge=None):
        if self.__rest_axes__ is not None and self.__called_from__ != self.apply_function.__name__:
            self.__rest_axes__.apply_points_function_about_point(func, about_point, about_edge)
        if self.__called_from__ == self.apply_function.__name__:
            about_point = self.get_origin()
        return super().apply_points_function_about_point(func, about_point, about_edge)

    def point_to_coords(self, point: Sequence[float]) -> Tuple[float]:
        if abs(self.get_velocity()) < self.__transform_tolerance__:
            return super().point_to_coords(point)
        untransformed_coords_from_point = self.get_rest_axes().point_to_coords(point)

        transformed_from_untransformed_coords = self.lorentz_transformation_to_rest(
            untransformed_coords_from_point
        )

        return (
            transformed_from_untransformed_coords[0],
            transformed_from_untransformed_coords[1],
        )

    def coords_to_point(self, *coords: Sequence[float]) -> np.ndarray:
        if abs(self.get_velocity()) < self.__transform_tolerance__:
            point = super().coords_to_point(*coords)
            return point

        untransformed_from_transformed_coords = self.lorentz_transformation(coords)

        point_from_untransformed_coords = self.get_rest_axes().coords_to_point(
            *untransformed_from_transformed_coords
        )

        return point_from_untransformed_coords

    def c2p(self, *coords):
        return self.coords_to_point(*coords)

    def p2c(self, point):
        return self.point_to_coords(point)

    def get_line_from_axis_to_point(
        self,
        index: int,
        point: Sequence[float],
        line_func: Line = DashedLine,
        line_config: Optional[Dict] = None,
        color: Color = LIGHT_GREY,
        stroke_width: float = 2,
    ) -> "Line":
        line_config = line_config if line_config is not None else {}
        line_config["color"] = color
        line_config["stroke_width"] = stroke_width
        x_coord, y_coord = self.p2c(point)

        axis_pt = [lambda: self.c2p(x_coord, 0), lambda: self.c2p(0, y_coord)][index]()
        line = line_func(axis_pt, point, **line_config)
        return line


class Spacetime(VGroup):
    def __init__(
        self,
        worldline_style_func: Callable[
            [TipableVMobject], TipableVMobject
        ] = lambda ob: ob.set_color_by_gradient([PINK, MAROON_B]),
        event_style_func: Callable[[Dot], Dot] = lambda ob: ob.set_color_by_gradient(
            [YELLOW, ORANGE]
        ),
        **kwargs,
    ):
        self.worldline_style_func = worldline_style_func
        self.event_style_func = event_style_func

        self.axes = SpacetimeAxes(**kwargs)
        self.ghost_axes = None
        self.axis_labels = self.axes.get_axis_labels("x", "ct")
        self.worldlines: dict[str, TipableVMobject] = {}
        self.events: dict[str, Dot] = {}
        self.event_alphas: dict[str, float] = {}
        self.intervals: dict[str, VGroup] = {}
        self.projections: dict[str, Tuple[Line, Line]] = {}
        super().__init__(*[self.axes, *self.axis_labels])

    def get_all_spacetime_objects(self):
        return [
            self.axes,
            *self.axis_labels,
            *self.worldlines.values(),
            *self.events.values(),
        ]

    def add_worldline(self, name: str, path: TipableVMobject):
        self.worldlines[name] = self.worldline_style_func(path)
        self.add(self.worldlines[name])
        return self

    @override_animate(add_worldline)
    def _add_worldline_animation(self, name: str, path: TipableVMobject, anim_args=None):
        anim_args = anim_args if anim_args is not None else {}
        self.add_worldline(name, path)
        return Create(self.worldlines[name], **anim_args)

    def _make_worldline_from_coords(
        self, start_coord: Sequence[float], end_coord: Sequence[float]
    ):
        start, end = [self.axes.coords_to_point(*coords) for coords in [start_coord, end_coord]]
        return Line(start=start, end=end, stroke_width=BOLD_STROKE_WIDTH, color=YELLOW)

    def add_worldline_from_coords(
        self, name: str, start_coord: Sequence[float], end_coord: Sequence[float]
    ):
        return self.add_worldline(name, self._make_worldline_from_coords(start_coord, end_coord))

    @override_animate(add_worldline_from_coords)
    def _add_worldline_from_coords_animation(self, name: str, *args, anim_args=None):
        anim_args = anim_args if anim_args is not None else {}
        return self._add_worldline_animation(
            name, self._make_worldline_from_coords(*args), anim_args
        )

    def add_event(self, name: str, *coords: Sequence[float]):
        self.events[name] = self.event_style_func(
            Dot(
                point=self.axes.c2p(*coords),
            )
        )
        self.add(self.events[name])
        return self

    @override_animate(add_event)
    def _add_event_animation(self, name: str, *args, anim_args=None):
        anim_args = anim_args if anim_args is not None else {}
        self.add_event(name, *args)
        return Create(self.events[name], **anim_args)

    def add_event_to_worldline(self, event_name: str, worldline_name: str, alpha: float):
        if worldline_name not in self.worldlines:
            raise Exception(f"No worldline found for name {worldline_name}")
        worldline = self.worldlines[worldline_name]

        self.event_alphas[event_name] = alpha
        self.events[event_name] = self.event_style_func(
            Dot(worldline.point_from_proportion(self.event_alphas[event_name]))
        )
        self.add(self.events[event_name])
        return self

    @override_animate(add_event_to_worldline)
    def _add_event_to_worldline_animation(self, event_name: str, *args, anim_args=None):
        anim_args = anim_args if anim_args is not None else {}
        self.add_event_to_worldline(event_name, *args)
        return Create(self.events[event_name], **anim_args)

    def add_event_projection(self, event_name: str):
        event_point = self.events[event_name].get_center()
        x_project = self.axes.get_line_from_axis_to_point(0, event_point)
        y_project = self.axes.get_line_from_axis_to_point(1, event_point)
        self.projections[event_name] = (x_project, y_project)
        self.add(x_project, y_project)
        return self

    @override_animate(add_event_projection)
    def _add_event_projection_animation(self, event_name: str, anim_args=None):
        anim_args = anim_args if anim_args is not None else {}
        self.add_event_projection(event_name)
        return AnimationGroup(
            *[Create(projection) for projection in self.projections[event_name]],
            **anim_args,
        )

    def set_axis_labels(self, xlabel: str, ylabel: str):
        new_axis_labels = self.axes.get_axis_labels(xlabel, ylabel)
        for index in [0, 1]:
            new_axis_labels[index].move_to(self.axis_labels[index])
            new_axis_labels[index].set_color(self.axis_labels[index].get_color())
            self.axis_labels[index].become(new_axis_labels[index])
        return self

    def apply_lorentz_transformation(self, velocity: float):
        self.axes.apply_lorentz_transformation(velocity)

        for index in [0, 1]:
            axis = self.axes.get_axes()[index]
            self.axis_labels[index].move_to(
                ([1.05, 1.1])[index] * (axis.get_end() - axis.get_start()) + axis.get_start()
            )
        for event_name, (x_project, y_project) in self.projections.items():
            event_point = self.events[event_name].get_center()
            new_x_project = self.axes.get_line_from_axis_to_point(0, event_point)
            new_y_project = self.axes.get_line_from_axis_to_point(1, event_point)

            x_project.become(new_x_project)
            y_project.become(new_y_project)

        return self
