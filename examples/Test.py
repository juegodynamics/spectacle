from typing import Callable, Iterable, NewType, Tuple
from manimlib import *

BG_COLOR = "#0A1929"


def point(*points):
    return np.array([points[0], points[1], 0])


def lorentz_x(x: float, t: float, v: float):
    gamma = 1 / np.sqrt(1 - (v ** 2))
    return point(
        gamma * (x - v * t),
        gamma * (t - v * x),
    )


class FTLError(Exception):
    def __init__(self, speed: float, *args: object) -> None:
        super().__init__(f"Attempted shift into speed {speed}c; cannot go faster than light")


class LogisticEase:
    def __init__(
        self,
        start: float,
        end: float,
        run_time: float,
        set_from_value: Callable[[float], None] = lambda _: None,
    ):
        self.xa = start
        self.xb = end
        self.t_mid = run_time / 2
        self.rate = 10 / run_time
        self.set_from_value = set_from_value
        self.t = 0

    def get_value(self, t: float):
        return self.xa + (self.xb - self.xa) / (1 + np.exp(-1 * (self.rate) * (t - self.t_mid)))

    def updater(self, dt: float):
        self.t += dt
        self.set_from_value(self.get_value(self.t))


class LorentzFrame(NumberPlane):
    def __init__(self, x_range=[0, 5, 1], y_range=[0, 5, 1], **kwargs):
        super().__init__(x_range, y_range, **kwargs)

    def get_x_axis_label(self, label_tex, **kwargs) -> Tex:
        return super().get_x_axis_label(label_tex, **kwargs)

    def get_y_axis_label(self, label_tex, **kwargs) -> Tex:
        return super().get_y_axis_label(label_tex, **kwargs)

    def get_origin(self) -> np.ndarray:
        return super().get_origin()

    def get_boundary_point(self, direction: np.ndarray) -> np.ndarray:
        return super().get_boundary_point(direction)

    def p2c(self, p: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return super().p2c(p)

    def c2p(self, *coords) -> np.ndarray:
        return super().c2p(*coords)


class WorldlineEvent(Dot):
    def __init__(self, point=ORIGIN, point_to_coordinates=None, **kwargs):
        self.point_to_coordinates = point_to_coordinates
        super().__init__(point, **kwargs)
        f_always(self.set_coords, self.calculate_coords)

    def calculate_coords(self):
        return self.point_to_coordinates(self.get_center())

    def set_coords(self, coords):
        self.coords = coords

    def get_coords(self):
        return self.coords


class Composer(Scene):
    def __init__(self, **kwargs):
        self.updaters = []
        super().__init__(**kwargs)

    def add_updater(self, updater):
        self.updaters.append(updater)

    def remove_updater(self, updater):
        self.updaters = [f for f in self.updaters if f is not updater]

    def update_frame(self, dt=0, ignore_skipping=False):
        for updater in self.updaters:
            updater(dt)
        return super().update_frame(dt, ignore_skipping)

    def show(self, *mobjects: Mobject, run_time=0.2, skip_wait=True, AnimMethod=ShowCreation):
        self.play(*[AnimMethod(n) for n in mobjects], run_time=run_time)
        if skip_wait:
            return
        self.wait()

    def hide(self, *mobjects: Mobject, run_time=1, AnimMethod=Uncreate, skip_wait=True):
        self.play(*[AnimMethod(n) for n in mobjects], run_time=run_time)
        for n in mobjects:
            n.clear_updaters()
        if skip_wait:
            return
        self.wait()

    def show_series(self, *mobjects: Mobject, run_time=1, AnimMethod=FadeIn, skip_wait=True):
        for n in mobjects:
            self.play(AnimMethod(n), run_time=run_time)
        if skip_wait:
            return
        self.wait()

    def flash(self, *mobjects: Mobject, skip_wait=True):
        for n in mobjects:
            dl_corner = n.get_corner(DL)
            ur_corner = n.get_corner(UR)
            radius = np.linalg.norm(ur_corner - dl_corner) / 2 + SMALL_BUFF
            self.play(Flash(n, flash_radius=radius))
        self.wait()


class LorentzScene(Composer):
    def construct(self):
        bg = Rectangle(color=BG_COLOR, height=10, width=20, fill_opacity=1)
        self.add(bg)
        self.setup_frame()
        self.create_wline_from_speed(0.5)
        # self.create_wline_from_bezier(2, 2, 2, 3, 3.5, 5)
        self.add_wline_event("event1", 0.4)
        self.add_wline_event("event2", 0.8)
        self.create_wline_event_link("event1", "event2")
        self.show_wline_event_link_calculations("event1", "event2")
        self.embed()

    def setup_frame(self):
        self.setup_frame_core()
        self.setup_frame_extras()

    def setup_frame_core(self):
        """setup_frame_core:

        All the objects that show constantly
        """
        self._is_prime = False
        self._frame: LorentzFrame = self.make_base_frame()

        self._frame_x_label: Tex = Tex("")
        f_always(
            self._frame_x_label.become,
            lambda: (
                Tex("x^\prime" if self._is_prime else "x")
                .set_color(self._frame.get_stroke_color())
                .move_to(self._frame.x_axis.get_end())
                .shift(RIGHT * 0.5)
            ),
        )

        self._frame_ct_label: Tex = Tex("")
        f_always(
            self._frame_ct_label.become,
            lambda: (
                Tex("ct^\prime" if self._is_prime else "ct")
                .set_color(self._frame.get_stroke_color())
                .move_to(self._frame.y_axis.get_end())
                .shift(UP * 0.5)
            ),
        )

        self._frame_velocity = 0

        self.show(self._frame, self._frame_x_label, self._frame_ct_label)

    def setup_frame_extras(self):
        """setup_frame_extras:

        Interactive objects that display conditionally
        """
        self._light_horizon = DashedLine()
        f_always(
            self._light_horizon.become,
            lambda: DashedLine(
                self._frame.get_origin(), self._frame.get_boundary_point(UR), color=GOLD
            ),
        )

        self._light_horizon_area = VGroup()
        f_always(
            self._light_horizon_area.become,
            lambda: Polygon(
                self._frame.get_origin(),
                self._frame.get_boundary_point(UR),
                self._frame.x_axis.get_end(),
                color=GOLD,
                fill_opacity=0.8,
            ),
        )

        self._wline: Union[None, CubicBezier, Line] = None
        self._wline_event_alphas: dict[str, float] = {}
        self._wline_events: dict[str, WorldlineEvent] = {}
        self._wline_event_coordinates: dict[str, np.ndarray] = {}
        self._wline_event_coords: dict[str, VGroup] = {}
        self._wline_event_links: dict[str, Tuple[Line, Line]] = {}
        self._wline_event_link_labels: dict[str, Tuple[VGroup, VGroup]] = {}
        self._wline_event_link_calcs: dict[str, VGroup] = {}

    def make_base_frame(self) -> LorentzFrame:
        return LorentzFrame(
            x_range=[0, 5, 1],
            y_range=[0, 5, 1],
            width=5,
            height=5,
            background_line_style={"stroke_color": BLACK},
            x_axis_config={"include_ticks": False},
            y_axis_config={"include_ticks": False},
        )

    def emphasize_frame_labels(self):
        self.flash(self._frame_x_label, self._frame_ct_label)

    def create_wline(self, new_wline, **kwargs):
        if self._wline is not None:
            self.play(self._wline.animate.become(new_wline), **kwargs)
        else:
            if new_wline is not None:
                self._wline = new_wline
            self.play(ShowCreation(self._wline), **kwargs)

    def create_wline_from_speed(self, speed: float, **kwargs):
        origin = self._frame.get_origin()
        boundary = self._frame.y_axis.get_length()
        self.create_wline(
            Line(
                start=origin,
                end=origin + point(speed * boundary, boundary),
                color=YELLOW,
            ),
            **kwargs,
        )

    def create_wline_from_bezier(self, x1, y1, x2, y2, x3, y3, **kwargs):
        origin = self._frame.get_origin()
        wline_points = [
            origin,
            origin + point(x1, y1),
            origin + point(x2, y2),
            origin + point(x3, y3),
        ]

        self.create_wline(CubicBezier(*wline_points, color=YELLOW), **kwargs)

    def hide_wline(self, **kwargs):
        self.hide(self._wline, **kwargs)

    def show_light_horizon(self, **kwargs):
        self.show(self._light_horizon, self._light_horizon_area, **kwargs)

    def hide_light_horizon(self, **kwargs):
        self.hide(self._light_horizon, self._light_horizon_area, **kwargs)

    def add_wline_event(self, name: string, alpha: float, **kwargs):
        self._wline_event_alphas[name] = alpha
        self._wline_events[name] = WorldlineEvent(
            color=RED, point_to_coordinates=self.point_to_coords
        )
        f_always(
            self._wline_events[name].move_to,
            lambda: self._wline.point_from_proportion(self._wline_event_alphas[name]),
        )

        self._wline_event_coords[name] = DecimalMatrix([[0], [0]]).scale(0.5)
        f_always(
            self._wline_event_coords[name].mob_matrix[0][0].set_value,
            lambda: self._wline_events[name].get_coords()[1],
        )
        f_always(
            self._wline_event_coords[name].mob_matrix[1][0].set_value,
            lambda: self._wline_events[name].get_coords()[0],
        )

        self.show(self._wline_events[name], **kwargs)

    # def get_frame_velocity(self):
    #     return self._frame_velocity

    def get_frame_velocity(self):
        # Calculate velocity from axis angle for smooth transition
        start, end = self._frame.x_axis.get_start_and_end()
        diff = end - start
        return diff[1] / diff[0]

    def point_to_coords(self, p: np.ndarray):
        coord_on_rest_frame = self.make_base_frame().p2c(p)
        to_coord_on_moving_frame = self.lorentz_transformation(self.get_frame_velocity())
        return to_coord_on_moving_frame(coord_on_rest_frame)

    def coords_to_point(self, *coords):
        to_coord_on_rest_frame = self.lorentz_transformation(-1 * self.get_frame_velocity())
        coords_on_rest_frame = to_coord_on_rest_frame(point(*coords))
        return self.make_base_frame().c2p(*coords_on_rest_frame)

    def update_wline_event(self, name: string, target_alpha: float, run_time=1):
        current_alpha = self._wline_event_alphas[name]

        def set_from_value(alpha: float):
            self._wline_event_alphas[name] = alpha

        easer = LogisticEase(current_alpha, target_alpha, run_time, set_from_value=set_from_value)

        self.add_updater(easer.updater)
        self.wait(run_time)
        self.remove_updater(easer.updater)

    def hide_wline_event(self, name: string):
        self.hide(self._wline_events[name])

    def show_wline_event_coords(self, name: string, **kwargs):
        event_coordinates = self._wline_event_coords[name]

        f_always(
            event_coordinates.move_to,
            lambda: self._wline_events[name].get_center()
            + event_coordinates.get_width() * LEFT * 0.6
            + event_coordinates.get_height() * UP * 0.6,
        )

        self.show(event_coordinates, **kwargs)

    def hide_wline_event_coords(self, name: string, **kwargs):
        event_coordinates = self._wline_event_coords[name]
        self.hide(event_coordinates, **kwargs)
        event_coordinates.clear_updaters()

    def get_event_coordinates(self, name1: string, name2: string):
        e1 = self._wline_events[name1].get_coords()
        e2 = self._wline_events[name2].get_coords()
        return e1, e2

    def get_events_dx(self, name1: string, name2: string):
        e1, e2 = self.get_event_coordinates(name1, name2)
        return e2[0] - e1[0]

    def get_events_dt(self, name1: string, name2: string):
        e1, e2 = self.get_event_coordinates(name1, name2)
        return e2[1] - e1[1]

    def create_wline_event_link(self, name1: string, name2: string, **kwargs):
        def get_events_intersection():
            e1, e2 = self.get_event_coordinates(name1, name2)
            return self.coords_to_point(e2[0], e1[1])

        horizontal = Line(color=RED)
        f_always(
            horizontal.put_start_and_end_on,
            self._wline_events[name1].get_center,
            get_events_intersection,
        )

        vertical = Line(color=RED)
        f_always(
            vertical.put_start_and_end_on,
            get_events_intersection,
            self._wline_events[name2].get_center,
        )

        horizontal_label = (
            VGroup(
                Tex(r"\Delta x", color=RED),
                DecimalNumber(0, num_decimal_places=2),
            )
            .arrange(DOWN)
            .scale(0.7)
        )

        always(horizontal_label.next_to, horizontal, DOWN)
        f_always(horizontal_label[1].set_value, lambda: self.get_events_dx(name1, name2))

        vertical_label = (
            VGroup(
                Tex(r"c \Delta t", color=RED),
                DecimalNumber(0, num_decimal_places=2),
            )
            .arrange(DOWN)
            .scale(0.7)
        )

        always(vertical_label.next_to, vertical, RIGHT)
        f_always(vertical_label[1].set_value, lambda: self.get_events_dt(name1, name2))

        velocity_calc = DecimalNumber(0, num_decimal_places=2, unit="c")
        interval_calc = DecimalNumber(0, num_decimal_places=2)

        link_calcs = VGroup(
            VGroup(
                Tex(r"\frac{\Delta x}{\Delta t} =", color=RED),
                velocity_calc,
            ).arrange(RIGHT),
            VGroup(
                Tex(r"\left( c\Delta t \right)^2 - \left( \Delta x \right)^2", color=RED),
                VGroup(Tex("=", color=RED), interval_calc).arrange(RIGHT),
            )
            .arrange(DOWN)
            .scale(0.9),
        ).arrange(DOWN, buff=LARGE_BUFF)

        f_always(link_calcs.move_to, self.get_left_panel_center)
        f_always(
            velocity_calc.set_value,
            lambda: self.get_events_dx(name1, name2) / self.get_events_dt(name1, name2),
        )
        f_always(
            interval_calc.set_value,
            lambda: (self.get_events_dt(name1, name2) ** 2)
            - (self.get_events_dx(name1, name2) ** 2),
        )

        # Index by each name to avoid link conflicts with multiple events
        cleanup_animations = []
        link_name = self.get_link_name(name1, name2)

        if link_name in self._wline_event_links:
            for link in self._wline_event_links[link_name]:
                cleanup_animations.append(Uncreate(link))
        if link_name in self._wline_event_link_labels:
            for link_label in self._wline_event_links[link_name]:
                cleanup_animations.append(Uncreate(link_label))

        self._wline_event_links[link_name] = [horizontal, vertical]
        self._wline_event_link_labels[link_name] = [horizontal_label, vertical_label]

        self._wline_event_link_calcs[link_name] = link_calcs
        if len(cleanup_animations) > 0:
            self.play(*cleanup_animations)
        self.show(horizontal, vertical, horizontal_label, vertical_label, **kwargs)

    def show_wline_event_link_calculations(self, name1: string, name2: string, **kwargs):
        self.show(self._wline_event_link_calcs[self.get_link_name(name1, name2)], **kwargs)

    def hide_wline_event_link_interval(self, name1: string, name2: string, **kwargs):
        self.hide(self._wline_event_link_calcs[self.get_link_name(name1, name2)], **kwargs)

    def get_link_name(self, name1: string, name2: string):
        return name1 + "-->" + name2

    def get_right_panel_center(self):
        right_end = RIGHT * FRAME_X_RADIUS
        frame_right_end = self._frame.get_right()
        return midpoint(frame_right_end, right_end)

    def get_left_panel_center(self):
        left_end = LEFT * FRAME_X_RADIUS
        frame_left_end = self._frame.get_left()
        return midpoint(left_end, frame_left_end)

    def lorentz_transformation(self, v: float):
        gamma = 1 / np.sqrt(1 - (v ** 2))
        return lambda p: point(
            gamma * (p[0] - v * p[1]),
            gamma * (p[1] - v * p[0]),
        )

    def boost_frame(self, target_velocity: float, run_time=1, **kwargs):
        if abs(target_velocity) > 1:
            raise FTLError(target_velocity)
        self._is_prime = False if target_velocity == 0 else True
        # current_velocity =
        relative_velocity = self.get_frame_velocity() - target_velocity

        new_frame = self._frame.copy()
        new_frame.apply_function(self.lorentz_transformation(relative_velocity))
        origin_offset = self._frame.get_boundary_point(DL) - new_frame.get_boundary_point(DL)
        new_frame.shift(origin_offset)

        # def set_from_value(transition_value):
        #     self._frame_velocity = transition_value

        # boost_easer = LogisticEase(
        #     current_velocity, target_velocity, run_time=run_time, set_from_value=set_from_value
        # )
        # self.add_updater(boost_easer.updater)
        self.play(
            self._frame.animate.become(new_frame),
            run_time=run_time,
            **kwargs,
        )
        # self.remove_updater(boost_easer.updater)

    def get_all_frame_objects(self):
        return [
            self._frame,
            self._wline,
        ]

    def scale_frame(self, scale: float, run_time=1):
        self.play(
            *[
                n.animate.apply_points_function_about_point(
                    lambda p: scale * p, about_point=ORIGIN
                )
                for n in self.get_all_plot_objects()
            ],
            run_time=run_time,
        )

    def shift_frame(self, shift: np.ndarray, run_time=1):
        self.play(
            *[n.animate.shift(shift) for n in self.get_all_plot_objects()],
            run_time=run_time,
        )
