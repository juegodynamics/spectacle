from spectacle import *

import random

BG_COLOR = "#0A1929"


def get_horizontal_brace(p1, p2):
    return BraceBetweenPoints(p1, point(p2[0], p1[1]))


def get_vertical_brace(p1, p2):
    return BraceBetweenPoints(point(p2[0], p1[1]), p2)


class Composer(Scene):
    def show(self, *mobjects, run_time=1, skip_wait=False, AnimMethod=Create):
        self.play(*[AnimMethod(n) for n in mobjects], run_time=run_time)
        if skip_wait:
            return
        self.wait()

    def hide(self, *mobjects, run_time=1, AnimMethod=Uncreate):
        self.play(*[AnimMethod(n) for n in mobjects], run_time=run_time)
        self.wait()

    def show_series(self, *mobjects, run_time=1, AnimMethod=Create, skip_wait=False):
        for n in mobjects:
            self.play(AnimMethod(n), run_time=run_time)
        if skip_wait:
            return
        self.wait()

    def flash(self, *mobjects):
        for n in mobjects:
            dl_corner = n.get_corner(DL)
            ur_corner = n.get_corner(UR)
            radius = np.linalg.norm(ur_corner - dl_corner) / 2 + SMALL_BUFF
            self.play(Flash(n, flash_radius=radius))
        self.wait()


class ShootingStar(Star):
    def __init__(
        self,
        n: int = 5,
        *,
        outer_radius: float = 1,
        inner_radius: Optional[float] = None,
        density: int = 2,
        start_angle: Optional[float] = TAU / 4,
        **kwargs,
    ):
        self.vtime = 0
        super().__init__(
            n,
            outer_radius=outer_radius,
            inner_radius=inner_radius,
            density=density,
            start_angle=start_angle,
            **kwargs,
        )

    def update_time(self, dt):
        self.vtime += dt


class Chapter2_Intervals(Composer):
    def construct(self):
        bg = Rectangle(color=BG_COLOR, height=10, width=20, fill_opacity=1)

        self.show(bg)
        self.scene_explain_lorentz()
        # self.scene_derive_interval()

    def scene_starry_space(self):
        random.seed(4242424242)
        self.stars: Iterable[ShootingStar] = []

        x_range = [config.left_side[0] + 0.1, config.right_side[0] - 0.1]
        y_range = [-4, 4]
        radius_range = [0.001, 0.05]
        points = [4, 5, 6, 7, 8, 9]
        top_cutoff = 1
        bottom_cutoff = -1

        for _ in range(100):
            radii = [random.uniform(*radius_range), random.uniform(*radius_range)]
            radii.sort()
            x = random.uniform(*x_range)
            y = random.uniform(*y_range)
            while abs(y - top_cutoff) < 0.1 or abs(y - bottom_cutoff) < 0.1:
                y = random.uniform(*y_range)

            star = ShootingStar(
                random.choice(points),
                inner_radius=radii[0],
                outer_radius=radii[1],
                color=interpolate_color(WHITE, GOLD, random.random()),
                fill_opacity=1,
            ).move_to(point(x, y))
            self.stars.append(star)

        self.add(*self.stars)

        top_line = Line(
            start=config.left_side + UP * top_cutoff,
            end=config.right_side + UP * top_cutoff,
            color=DARKER_GRAY,
        )
        bottom_line = Line(
            start=config.left_side + UP * bottom_cutoff,
            end=config.right_side + UP * bottom_cutoff,
            color=DARKER_GRAY,
        )

        self.add(top_line, bottom_line)

        def update_star(star: ShootingStar, dt):
            star.update_time(dt)
            ease_factor = 1 / (1 + np.exp(-(star.vtime - 1)))
            y_factor = 0
            y = star.get_center()[1]
            if y > top_cutoff:
                y_factor = 1

                if star.get_right()[0] < config.left_side[0]:
                    color = star.get_color()
                    star.set_color(BLACK)
                    star.shift(config.right_side - config.left_side + RIGHT * 0.1)
                    star.set_color(color)
            if y < bottom_cutoff:
                y_factor = -1
                if star.get_left()[0] > config.right_side[0]:
                    color = star.get_color()
                    star.set_color(BLACK)
                    star.shift(-1 * (config.right_side - config.left_side + RIGHT * 0.1))
                    star.set_color(color)

            star.shift(ease_factor * y_factor * LEFT * dt * 2)

        for star in self.stars:
            star.add_updater(update_star)

        for _ in range(8):
            self.photon_top = Photon(
                start=config.left_side, end=config.right_side, color=YELLOW
            ).shift(UP * 2)
            self.photon = Photon(start=config.left_side, end=config.right_side, color=YELLOW)
            self.photon_bottom = Photon(
                start=config.left_side, end=config.right_side, color=YELLOW
            ).shift(DOWN * 2)
            self.play(
                Create(self.photon_top),
                Create(self.photon),
                Create(self.photon_bottom),
                run_time=0.5,
            )
            self.photon_top.rotate_about_origin(PI)
            self.photon.rotate_about_origin(PI)
            self.photon_bottom.rotate_about_origin(PI)
            self.play(
                Uncreate(self.photon_top),
                Uncreate(self.photon),
                Uncreate(self.photon_bottom),
                run_time=0.5,
            )
            self.wait()

        self.hide(*self.stars, run_time=2, AnimMethod=FadeOut)

    def scene_explain_lorentz(self):
        self.setup_frame()
        self.emphasize_axis_labels()

        self.apply_lorentz_transform()
        self.apply_lorentz_transform(gamma=0.2, color=BLUE)

        self.show_light_cone()
        self.show_ftl_area()
        self.hide_ftl_area()
        self.apply_lorentz_transform()
        self.apply_lorentz_transform(gamma=0.2, color=BLUE)
        self.hide_light_cone()

        self.hide_frame_background_lines()
        self.show_worldline()

        x0 = "x0"
        x1 = "x1"
        self.put_event_on_worldline(x0, 0.3)
        self.put_event_on_worldline(x1, 0.7)

        self.show_events()
        self.project_events_onto_axes(self.main_frame)
        self.show_event_projection_braces(x0, x1)

        demo_gamma = 0.3

        self.apply_lorentz_transform(keep_ghost=True, gamma=-1 * demo_gamma)
        self.project_events_onto_axes(self.main_frame)
        self.show_event_projection_braces(x0, x1, color=RED, is_prime=True)
        self.wait()

        self.apply_lorentz_transform(keep_ghost=True, gamma=demo_gamma)

        self.hide(
            *[
                *self.get_all_event_projection_objects(),
                *self.get_all_projection_brace_objects(),
                self.ghost,
                self.x_label,
                self.ct_label,
            ],
            run_time=2,
        )

        self.scale_plot(scale=3, run_time=3)
        self.shift_plot()

        p0 = self.events[x0].get_center()
        p1 = self.events[x1].get_center()

        main_triangle = Polygon(p0, p1, point(p1[0], p0[1]), fill_opacity=0.5)

        [event1_x_projection, event1_y_projection] = self.event_projections[x0 + "'"]
        [event2_x_projection, event2_y_projection] = self.event_projections[x1 + "'"]

        primed_point = event1_x_projection.get_end() + (
            event2_x_projection.get_start() - event1_x_projection.get_start()
        )

        shift_triangle = Polygon(p0, p1, primed_point, color=RED, fill_opacity=0.5)

        self.show(main_triangle, shift_triangle)

        lorentz_eqs = (
            VGroup(
                MathTex("t^\prime = \gamma \left(t - { v x \over c^2 } \\right)"),
                MathTex("x^\prime = \gamma \left( x - v t \\right)"),
            )
            .arrange(DOWN)
            .shift(RIGHT * 4)
        )

        self.show(lorentz_eqs[0], lorentz_eqs[1])

        substitution = (
            MathTex("ct \mapsto x_{0},\quad x \mapsto x_{1}", color=BLUE)
            .scale(0.7)
            .next_to(lorentz_eqs, UP * 3)
        )

        self.show(substitution, skip_wait=True)
        self.flash(substitution)

        lorentz_eqs_sub1 = (
            VGroup(
                MathTex("x_0^\prime = \gamma \left( x_0 - { v x_1 \over c } \\right)"),
                MathTex("x_1^\prime = \gamma \left( x_1 - { v x_0 \over c } \\right)"),
            )
            .arrange(DOWN)
            .shift(RIGHT * 4)
        )

        for eq in range(len(lorentz_eqs)):
            self.play(TransformMatchingShapes(lorentz_eqs[eq], lorentz_eqs_sub1[eq]))

        self.wait()

        lorentz_eqs_sub2 = (
            VGroup(
                MathTex("{x_0^\prime}^2 = \gamma^2 \left( x_0 - { v x_1 \over c } \\right)^2"),
                MathTex("{x_1^\prime}^2 = \gamma^2 \left( x_1 - { v x_0 \over c } \\right)^2"),
            )
            .arrange(DOWN)
            .shift(RIGHT * 4)
        )

        for eq in range(len(lorentz_eqs)):
            self.play(TransformMatchingShapes(lorentz_eqs_sub1[eq], lorentz_eqs_sub2[eq]))

        self.wait()

        lorentz_eqs_sub3 = (
            VGroup(
                MathTex(
                    "{x_0^\prime}^2 = \gamma^2 \left( x_0^2 - {2 v x_0 x_1 \over c } + {v^2 \over c^2} x_1^2 \\right)"
                ),
                MathTex(
                    "{x_1^\prime}^2 = \gamma^2 \left( x_1^2 - {2 v x_0 x_1 \over c } + {v^2 \over c^2} x_0^2 \\right)"
                ),
            )
            .arrange(DOWN)
            .shift(RIGHT * 3)
            .scale(0.9)
        )

        for eq in range(len(lorentz_eqs)):
            self.play(TransformMatchingShapes(lorentz_eqs_sub2[eq], lorentz_eqs_sub3[eq]))

        self.wait()

        lorentz_eqs_diffs = [
            MathTex(
                "{x_0^\prime}^2 - {x_1^\prime}^2 = \gamma^2 \left( 1 + {v^2 \over c^2} \\right) \left( x_0^2 - x_1^2 \\right)"
            ).shift(RIGHT * 3),
            MathTex(
                "{x_0^\prime}^2 - {x_1^\prime}^2 = \gamma^2 {1 \over \gamma^2} \left( x_0^2 - x_1^2 \\right)"
            ).shift(RIGHT * 3.5),
            MathTex("{x_0^\prime}^2 - {x_1^\prime}^2 = x_0^2 - x_1^2").shift(RIGHT * 4),
        ]

        for eq_index in range(len(lorentz_eqs_diffs)):
            diff_eq = lorentz_eqs_diffs[eq_index]
            if eq_index == 0:
                self.play(
                    TransformMatchingShapes(lorentz_eqs_sub3[0], diff_eq),
                    TransformMatchingShapes(lorentz_eqs_sub3[1], diff_eq),
                )
                self.wait()
            else:
                last_diff_eq = lorentz_eqs_diffs[eq_index - 1]
                self.play(TransformMatchingShapes(last_diff_eq, diff_eq))
                self.wait()

    def setup_frame(self):
        self.is_prime = False
        self.main_frame = NumberPlane(
            x_range=[0, 5, 0.5],
            y_range=[0, 5, 0.5],
        )
        self.x_label, self.ct_label = self.make_labels(self.main_frame)

        self.show(self.main_frame, run_time=2)
        self.show(self.x_label, self.ct_label)

        self.light_cone = None
        self.ftl_area = None
        self.wordline = None
        self.events = {}
        self.event_projections = {}
        self.event_braces = {}
        self.rel_speed = 0
        self.ghost = None

    def make_x_label(self):
        if self.is_prime:
            return "x^\prime"
        return "x"

    def make_ct_label(self):
        if self.is_prime:
            return "ct^\prime"
        return "ct"

    def make_labels(self, frame, color=WHITE):
        x_label = frame.get_x_axis_label(self.make_x_label(), direction=DR).set_color(color)
        ct_label = frame.get_y_axis_label(self.make_ct_label(), direction=UL).set_color(color)
        return x_label, ct_label

    def emphasize_axis_labels(self):
        self.flash(self.x_label, self.ct_label)

    def get_frame_corner(self, frame):
        return point(frame.get_right()[0], frame.get_top()[1])

    def show_light_cone(self):
        self.light_cone = DashedLine(
            self.main_frame.get_origin(), self.get_frame_corner(self.main_frame), color=GOLD
        )
        self.show(self.light_cone)

    def hide_light_cone(self):
        if self.light_cone is not None:
            self.hide(self.light_cone)
            self.light_cone = None

    def make_ftl_area(self, frame: NumberPlane):
        return Polygon(
            frame.get_origin(),
            self.get_frame_corner(frame),
            frame.x_axis.get_end(),
            color=GOLD,
            fill_opacity=0.8,
        )

    def show_ftl_area(self):
        self.ftl_area = self.make_ftl_area(self.main_frame)
        self.show(self.ftl_area)

    def hide_ftl_area(self):
        if self.ftl_area is not None:
            self.hide(self.ftl_area)
            self.ftl_area = None

    def show_worldline(self):
        origin = self.main_frame.get_origin()
        wordline_points = [
            origin,
            origin + point(2, 2),
            origin + point(2, 3),
            origin + point(3.5, 5),
        ]

        self.worldline = CubicBezier(*wordline_points, color=YELLOW)
        self.show(self.worldline)

    def hide_worldline(self):
        if self.wordline is not None:
            self.hide(self.wordline)
            self.worldline = None

    def make_event(self, event_pt):
        return Dot(point=event_pt, color=RED)

    def put_event_on_worldline(self, name, alpha):
        event_pt = self.worldline.point_from_proportion(alpha)
        event = self.make_event(event_pt)
        self.events[name] = event

    def project_events_onto_axes(self, axes: Axes):
        for name, event in self.events.items():
            if (
                abs(self.rel_speed) > 0.01
                and len(self.event_projections[name]) > 0
                and self.is_prime
            ):
                tmp_frame, _, _ = self.make_lorentz_transformed_frame(
                    self.main_frame.copy(), -2 * self.rel_speed
                )
                x_line = tmp_frame.get_line_from_axis_to_point(0, event.get_center())
                x_intersect = line_intersection(
                    list(x_line.get_start_and_end()),
                    list(self.main_frame.x_axis.get_start_and_end()),
                )
                x_line = DashedLine(start=x_intersect, end=x_line.get_end(), color=RED)

                y_line = tmp_frame.get_line_from_axis_to_point(1, event.get_center()).set_color(
                    RED
                )
                y_intersect = line_intersection(
                    list(y_line.get_start_and_end()),
                    list(self.main_frame.y_axis.get_start_and_end()),
                )
                y_line = DashedLine(start=y_intersect, end=y_line.get_end(), color=RED)

                self.event_projections[name + "'"] = [x_line, y_line]

                self.show(x_line, y_line, run_time=0.5)
            else:
                x_line = axes.get_line_from_axis_to_point(0, event.get_center())
                y_line = axes.get_line_from_axis_to_point(1, event.get_center())
                self.event_projections[name] = [x_line, y_line]
                self.show(*self.event_projections[name], run_time=0.5)

    def show_event_projection_braces(self, name1, name2, is_prime=False, color=WHITE):
        projection_name_1 = name1 + {True: "'"}.get(is_prime, "")
        projection_name_2 = name2 + {True: "'"}.get(is_prime, "")
        [event1_x_projection, event1_y_projection] = self.event_projections[projection_name_1]
        [event2_x_projection, event2_y_projection] = self.event_projections[projection_name_2]
        x_brace = get_horizontal_brace(
            event1_x_projection.get_start(), event2_x_projection.get_start()
        ).set_color(color)
        # if is_prime:
        #     x_brace.shift(DOWN)
        x_brace_label = (
            x_brace.get_tex("\Delta x" + {True: "^\prime"}.get(is_prime, ""))
            .scale(0.7)
            .shift(UP * 0.2)
            .set_color(color)
        )

        y_brace = get_vertical_brace(
            event2_y_projection.get_start(), event1_y_projection.get_start()
        ).set_color(color)
        # if is_prime:
        #     y_brace.shift(LEFT)
        y_brace_label = (
            y_brace.get_tex("c \Delta t" + {True: "^\prime"}.get(is_prime, ""))
            .scale(0.7)
            .shift(RIGHT * 0.3)
            .set_color(color)
        )

        if name1 + "-" + name2 in self.event_braces:
            brace_ob = self.event_braces[name1 + "-" + name2]
            [old_x_brace, old_y_brace] = brace_ob["braces"]
            [old_x_brace_label, old_y_brace_label] = brace_ob["labels"]

            self.play(
                old_x_brace.animate.become(x_brace),
                old_y_brace.animate.become(y_brace),
                old_x_brace_label.animate.become(x_brace_label),
                old_y_brace_label.animate.become(y_brace_label),
            )
        else:
            self.show(x_brace, x_brace_label, y_brace, y_brace_label)

            self.event_braces[name1 + "-" + name2] = {
                "braces": [x_brace, y_brace],
                "labels": [x_brace_label, y_brace_label],
            }

        # if (name1 + "'" in self.event_projections) and (name2 + "'" in self.event_projections):
        #     self.show_event_projection_braces(name1 + "'", name2 + "'", is_prime=True)

    def hide_event_projection_braces(self, name1, name2):
        self.hide(
            *[
                brace_ob
                for brace_set in self.event_braces[name1 + "-" + name2].values()
                for brace_ob in brace_set
            ]
        )

    def get_all_projection_brace_objects(self):
        return [
            brace_ob
            for brace_dict in self.event_braces.values()
            for brace_set in brace_dict.values()
            for brace_ob in brace_set
        ]

    def hide_event_projects(self):
        self.hide(
            *[
                event_projection
                for projections in self.event_projections.values()
                for event_projection in projections
            ]
        )

    def get_all_event_projection_objects(self):
        return [
            event_projection
            for projections in self.event_projections.values()
            for event_projection in projections
        ]

    def show_events(self):
        self.show(*self.events.values())

    def hide_events(self):
        self.hide(*self.events.values())

    def hide_frame_background_lines(self):
        frame = self.main_frame.copy()
        frame.background_lines.set_style(stroke_opacity=0)
        self.play(self.main_frame.animate.become(frame))
        self.wait()

    def make_lorentz_transformed_frame(self, frame, gamma):
        def lorentz_transform(p):
            return lorentz_x(p[0], p[1], gamma)

        frame.prepare_for_nonlinear_transform()
        frame.apply_function(lorentz_transform)

        shift_offset = self.main_frame.get_origin() - frame.get_origin()
        frame.shift(shift_offset)
        return frame, shift_offset, lorentz_transform

    def apply_lorentz_transform(self, gamma=-0.2, color=RED, keep_ghost=False):
        self.is_prime = not self.is_prime
        self.rel_speed += gamma

        frame, shift_offset, lorentz_transform = self.make_lorentz_transformed_frame(
            self.main_frame.copy(), gamma
        )
        frame.background_lines.set_style(stroke_color=color)

        x_label, ct_label = self.make_labels(frame)

        self.main_frame.prepare_for_nonlinear_transform()

        if keep_ghost:
            if self.ghost is not None:
                self.hide(self.ghost)
            self.ghost = self.main_frame.copy().set_color(DARKER_GRAY)
            self.ghost.background_lines.set_style(stroke_opacity=0)
            self.add(self.ghost)

        animations = [
            self.main_frame.animate.become(frame),
            self.x_label.animate.become(x_label),
            self.ct_label.animate.become(ct_label),
        ]

        if self.light_cone is not None:
            new_light_cone = (
                self.light_cone.copy().apply_function(lorentz_transform).shift(shift_offset)
            )
            animations.append(self.light_cone.animate.become(new_light_cone))

        if self.ftl_area is not None:
            new_ftl_area = self.make_ftl_area(frame)
            animations.append(self.ftl_area.animate.become(new_ftl_area))

        # for event_projection_set in self.event_projections.values():
        #     for event_projection in event_projection_set:
        #         new_event_projection = (
        #             event_projection.copy().apply_function(lorentz_transform).shift(shift_offset)
        #         )
        #         animations.append(event_projection.animate.become(new_event_projection))

        self.play(*animations)

        self.wait()

    def get_all_plot_objects(self):
        return [
            self.main_frame,
            self.worldline,
            *self.events.values(),
            *self.get_all_event_projection_objects(),
            *self.get_all_projection_brace_objects(),
        ]

    def scale_plot(self, scale=0.8, run_time=1):
        self.play(
            *[
                n.animate.apply_points_function_about_point(
                    lambda p: scale * p, about_point=ORIGIN
                )
                for n in self.get_all_plot_objects()
            ],
            run_time=run_time,
        )

    def shift_plot(self, shift=LEFT, run_time=1):
        self.play(
            *[n.animate.shift(shift) for n in self.get_all_plot_objects()],
            run_time=run_time,
        )


class Chapter1(Scene):
    def construct(self):
        bg = Rectangle(color=BG_COLOR, height=10, width=20, fill_opacity=1)
        self.add(bg)
        self.setup_objects()

        self.show_ftl_area()
        self.show_lorentz()
        self.hide_ftl_area()
        self.hide_lorentz()

        self.show_worldline()
        self.show_world_events()

        self.hide_world_events()

        self.scale_plot(scale=0.7)
        self.shift_plot(shift=UP * 1.2)
        self.setup_lab()
        self.run_lab_frame()
        self.run_box_frame()

    def make_main_axes(self):
        return Axes(
            x_range=[0, 5, 1],
            y_range=[0, 5, 1],
            x_length=5,
            y_length=5,
            x_axis_config={"include_ticks": False},
            y_axis_config={"include_ticks": False},
        )

    def make_prime_axes(self):
        axes = self.main_axes.copy().set_color(DARK_BLUE)
        origin = axes.get_origin()

        axes.x_axis.rotate(angle=-1 * self.gamma_factor, about_point=origin)
        axes.x_axis.put_start_and_end_on(
            axes.x_axis.get_start(),
            (axes.x_axis.get_end() - origin) * (1 + abs(self.gamma_factor)) + origin,
        )
        axes.y_axis.rotate(angle=self.gamma_factor, about_point=origin)
        axes.y_axis.put_start_and_end_on(
            axes.y_axis.get_start(),
            (axes.y_axis.get_end() - origin) * (1 + abs(self.gamma_factor)) + origin,
        )
        return axes

    def make_x_label(self):
        return self.make_main_axes().get_x_axis_label("x")

    def make_ct_label(self):
        return self.make_main_axes().get_y_axis_label("ct")

    def make_x_prime_label(self):
        return self.make_prime_axes().get_x_axis_label("x^\prime").set_color(DARK_BLUE)

    def make_ct_prime_label(self):
        return self.make_prime_axes().get_y_axis_label("ct^\prime").set_color(DARK_BLUE)

    def make_ftl_area(self, axes):
        origin = axes.get_origin()
        x_end = axes.x_axis.get_end()

        return Polygon(
            *[origin, origin + point(5, 5), x_end],
            color=DARK_GRAY,
            fill_opacity=0.3,
            stroke_width=0,
        )

    def setup_objects(self):
        self.gamma_factor = -0.2
        self.main_axes = self.make_main_axes()
        self.x_label = self.make_x_label()
        self.ct_label = self.make_ct_label()

        for ob_group in [[self.main_axes], [self.x_label, self.ct_label]]:
            self.show(*ob_group)

        self.flash(self.x_label, self.ct_label)

        self.photon_line = self.main_axes.plot(lambda x: x)
        self.photon_line = DashedLine(
            self.photon_line.get_start(), self.photon_line.get_end(), color=WHITE
        )

        origin = self.main_axes.get_origin()

        self.ftl_area = self.make_ftl_area(self.main_axes)

        self.ftl_is_visible = False

        wordline_points = [
            origin,
            origin + point(2, 2),
            origin + point(3, 4),
            origin + point(4.5, 5),
        ]

        self.worldline = CubicBezier(*wordline_points, color=YELLOW)

        event1_pt = self.worldline.point_from_proportion(0.5)
        event2_pt = self.worldline.point_from_proportion(0.7)

        self.event1 = Dot(color=TEAL).move_to(event1_pt).set_opacity(0.8)
        self.event2 = Dot(color=TEAL).move_to(event2_pt).set_opacity(0.8)

        self.event_interval = Line(
            start=event1_pt,
            end=event2_pt,
            buff=self.event1.radius,
            color=TEAL,
            stroke_width=DEFAULT_STROKE_WIDTH * 1.5,
        )

        dx = get_horizontal_brace(event1_pt, event2_pt)
        self.event_dx = VGroup(dx, dx.get_tex("\Delta x"))
        dy = get_vertical_brace(event1_pt, event2_pt)
        self.event_dy = VGroup(dy, dy.get_tex("c \Delta t"))

    def make_lab_box(self):
        worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)
        return Square(side_length=0.5, color=YELLOW, fill_opacity=1).move_to(
            point(worldline_pt[0], self.table_top[1] - 0.25)
        )

    def make_worldline_box_event(self):
        worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)
        return Dot(color=TEAL).move_to(worldline_pt)

    def make_event_box_connector(self):
        return DashedLine(
            self.make_lab_box().get_top(),
            self.make_worldline_box_event().get_center(),
            color=TEAL,
            dashed_ratio=0.4,
            stroke_width=DEFAULT_STROKE_WIDTH / 2,
        )

    def setup_lab(self):
        divide_top = DOWN
        self.lab_divider = Polygon(
            *[
                config.left_side + divide_top,
                config.right_side + divide_top,
                config.right_side + 10 * DOWN,
                config.left_side + 10 * DOWN,
            ],
            color=BLACK,
            fill_opacity=1,
        )

        padding = 1
        table_left = self.main_axes.x_axis.get_start() + padding * LEFT
        table_right = self.main_axes.x_axis.get_end() + padding * RIGHT

        self.table_top = DOWN * 3

        self.lab_table = Polygon(
            *[
                table_left + self.table_top,
                table_right + self.table_top,
                table_right + 2 * self.table_top,
                table_left + 2 * self.table_top,
            ],
            color=WHITE,
            fill_opacity=1,
        ).set_color_by_gradient([GRAY, DARKER_GRAY, GRAY, DARKER_GRAY])

        self.worldline_alpha = 0.1
        worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)

        self.worldline_box_event = self.make_worldline_box_event()
        self.lab_box = self.make_lab_box()
        self.event_box_connector = self.make_event_box_connector()

        self.show(self.lab_divider, self.lab_table)
        self.show(self.lab_box, self.worldline_box_event, self.event_box_connector)

    def run_lab_frame(self):
        self.stopwatch = StopWatch(
            center=self.main_axes.get_left() + 3 * LEFT,
            outer_radius=0.75,
            inner_radius=0.75 * (1.25 / 1.5),
        )
        self.frame_label = Text(
            "The Lab Frame", font_size=DEFAULT_FONT_SIZE / 2, font="sans-serif"
        ).next_to(self.stopwatch, UP)
        self.show(self.stopwatch, self.frame_label)

        self.stopwatch.start_running()

        def update_lab(dt):
            self.worldline_alpha += dt / 5
            if (self.worldline_alpha) >= 0.95:
                self.worldline_alpha = 0.95

            worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)
            self.worldline_box_event.move_to(worldline_pt)
            self.lab_box.become(self.make_lab_box())
            self.event_box_connector.become(self.make_event_box_connector())

        self.add_updater(update_lab)
        self.wait(5)
        self.stopwatch.stop_running()
        self.remove_updater(update_lab)
        self.wait()

        tmp_box = self.lab_box.copy()
        tmp_event = self.worldline_box_event.copy()
        tmp_connector = self.event_box_connector.copy()
        self.add(tmp_box, tmp_event, tmp_connector)

        self.worldline_alpha = 0.1
        worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)
        self.play(
            self.worldline_box_event.animate.move_to(worldline_pt),
            self.lab_box.animate.become(self.make_lab_box()),
            self.event_box_connector.animate.become(self.make_event_box_connector()),
        )
        self.wait()

        p0 = self.worldline_box_event.get_center()
        p1 = tmp_event.get_center()

        dt_line0 = self.main_axes.get_line_from_axis_to_point(1, p0)
        dt_line1 = self.main_axes.get_line_from_axis_to_point(1, p1)

        t0 = dt_line0.get_left()
        t1 = dt_line1.get_left()

        dt_brace = get_vertical_brace(t1, t0)
        dt_label = dt_brace.get_tex("c \Delta t")

        dt = Line(start=t0, end=t1, stroke_width=DEFAULT_STROKE_WIDTH * 2, color=RED)

        self.show(dt_brace, dt_label, dt_line0, dt_line1, dt)
        self.play(FocusOn(self.stopwatch.time_sector))
        self.play(FocusOn(dt))
        self.play(dt.animate.become(self.stopwatch.time_sector), run_time=3)

        self.wait()

        self.hide(
            dt,
            dt_brace,
            dt_label,
            dt_line0,
            dt_line1,
            tmp_box,
            tmp_event,
            tmp_connector,
            self.stopwatch,
            self.frame_label,
        )

    def run_box_frame(self):
        self.box_stopwatch = StopWatch(
            center=self.main_axes.get_right() + 3 * RIGHT,
            outer_radius=0.75,
            inner_radius=0.75 * (1.25 / 1.5),
        )
        self.box_frame_label = Text(
            "The Box Frame", font_size=DEFAULT_FONT_SIZE / 2, font="sans-serif"
        ).next_to(self.box_stopwatch, UP)
        self.show(self.box_stopwatch, self.box_frame_label)

        self.box_stopwatch.start_running(update_rate=0.6)

        original_origin = self.main_axes.get_origin()
        original_worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)

        def update_lab_from_box(dt):
            if (self.worldline_alpha + dt / 5) >= 0.95:
                self.worldline_alpha = 0.95
                return

            old_worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)
            new_worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha + dt / 5)
            self.worldline_alpha += dt / 5

            diff_worldline = new_worldline_pt - old_worldline_pt

            for ob in [*self.all_plot_objects(), self.lab_table]:
                ob.shift(point(-1 * diff_worldline[0], 0))

            self.worldline_box_event.shift(point(0, diff_worldline[1]))

            self.event_box_connector.become(
                DashedLine(
                    self.lab_box.get_top(),
                    self.worldline_box_event.get_center(),
                    color=TEAL,
                    dashed_ratio=0.4,
                    stroke_width=DEFAULT_STROKE_WIDTH / 2,
                )
            )

        self.add_updater(update_lab_from_box)
        self.wait(5)
        self.box_stopwatch.stop_running()
        self.remove_updater(update_lab_from_box)
        self.wait()
        self.worldline_alpha = 0.1

        shift_back = original_origin - self.main_axes.get_origin()
        worldline_pt = self.worldline.point_from_proportion(self.worldline_alpha)
        self.play(
            *[ob.animate.shift(shift_back) for ob in self.all_plot_objects()],
            self.worldline_box_event.animate.move_to(original_worldline_pt),
            self.lab_table.animate.shift(shift_back),
            self.event_box_connector.animate.put_start_and_end_on(
                self.lab_box.get_top(), original_worldline_pt
            ),
        )

        start = self.worldline.point_from_proportion(0)
        end = self.worldline.point_from_proportion(1)
        self.gamma_factor = -1 * Line(start=start, end=end).get_angle()
        new_axes = self.make_prime_axes()
        self.show(new_axes)

    def all_plot_objects(self):
        return [
            self.main_axes,
            self.x_label,
            self.ct_label,
            self.worldline,
            self.event1,
            self.event2,
            self.event_dx,
            self.event_dy,
            self.event_interval,
        ]

    def scale_plot(self, scale=0.8, run_time=1):
        self.play(
            *[
                n.animate.apply_points_function_about_point(
                    lambda p: scale * p, about_point=ORIGIN
                )
                for n in self.all_plot_objects()
            ],
            run_time=run_time,
        )

    def shift_plot(self, shift=UP, run_time=1):
        self.play(*[n.animate.shift(shift) for n in self.all_plot_objects()], run_time=run_time)

    def show_ftl_area(self, hide_at_end=False):
        self.show(self.photon_line)
        self.show(self.ftl_area, run_time=2)

        self.ftl_is_visible = True

        if hide_at_end:
            self.hide_ftl_area()

    def hide_ftl_area(self):
        self.hide(self.photon_line, self.ftl_area)
        self.ftl_is_visible = False

    def show_lorentz(self, gamma_factor=-0.2):
        self.gamma_factor = gamma_factor

        animations = [
            self.main_axes.animate.become(self.make_prime_axes()),
            self.x_label.animate.become(self.make_x_prime_label()),
            self.ct_label.animate.become(self.make_ct_prime_label()),
        ]

        if self.ftl_is_visible:
            animations.append(
                self.ftl_area.animate.become(self.make_ftl_area(self.make_prime_axes()))
            )
        self.play(*animations)
        self.wait()

    def hide_lorentz(self):
        animations = [
            self.main_axes.animate.become(self.make_main_axes()),
            self.x_label.animate.become(self.make_x_label()),
            self.ct_label.animate.become(self.make_ct_label()),
        ]

        if self.ftl_is_visible:
            animations.append(
                self.ftl_area.animate.become(self.make_ftl_area(self.make_main_axes()))
            )
        self.play(*animations)
        self.wait()

    def show_worldline(self):
        self.show(self.worldline)

    def hide_worldline(self):
        self.hide(self.worldline)

    def show_world_events(self):
        self.show(self.event1, self.event2, skip_wait=True)
        self.show(self.event_interval)
        self.show_series(self.event_dx, self.event_dy, AnimMethod=FadeIn)

    def hide_world_events(self):
        self.hide(self.event1, self.event2, self.event_interval, self.event_dx, self.event_dy)

    def show(self, *mobjects, run_time=1, skip_wait=False, AnimMethod=Create):
        self.play(*[AnimMethod(n) for n in mobjects], run_time=run_time)
        if skip_wait:
            return
        self.wait()

    def hide(self, *mobjects, run_time=1, AnimMethod=Uncreate):
        self.play(*[AnimMethod(n) for n in mobjects], run_time=run_time)
        self.wait()

    def show_series(self, *mobjects, run_time=1, AnimMethod=Create, skip_wait=False):
        for n in mobjects:
            self.play(AnimMethod(n), run_time=run_time)
        if skip_wait:
            return
        self.wait()

    def flash(self, *mobjects):
        for n in mobjects:
            dl_corner = n.get_corner(DL)
            ur_corner = n.get_corner(UR)
            radius = np.linalg.norm(ur_corner - dl_corner) / 2 + SMALL_BUFF
            self.play(Flash(n, flash_radius=radius))
        self.wait()


class StopWatch(VGroup):
    def __init__(
        self,
        center=ORIGIN,
        outer_radius=1.5,
        inner_radius=1.25,
        primary_color=WHITE,
        bg_color=BLACK,
    ):
        self.main_center = center
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.primary_color = primary_color
        self.bg_color = bg_color
        self.outer_circle = Circle(
            radius=self.outer_radius, fill_opacity=1, color=primary_color
        ).move_to(center)
        self.inner_circle = Circle(
            radius=self.inner_radius, fill_opacity=1, color=bg_color
        ).move_to(center)
        self.vtime = 0

        self.ticks = []
        for n in range(8):
            angle = n * 2 * PI / 8
            vec = point(np.cos(angle), np.sin(angle))
            start = self.main_center + 0.8 * vec * self.inner_radius
            end = self.main_center + 0.9 * vec * self.inner_radius
            tick_line = Line(start=start, end=end, stroke_width=DEFAULT_STROKE_WIDTH / 2)
            self.ticks.append(tick_line)

        self.center_axle = Dot(point=center)
        self.ticker_line = Line(start=center, end=center + 0.75 * UP)
        self.ticker = Polygon(
            center + 0.75 * self.inner_radius * UP,
            center + (DEFAULT_DOT_RADIUS / 4) * RIGHT,
            center + (DEFAULT_DOT_RADIUS / 4) * LEFT,
            fill_opacity=1,
        )

        self.ghost_ticker = DashedLine(
            self.main_center, self.main_center + 0.75 * self.inner_radius * UP, color=bg_color
        )
        self.time_sector = self.get_time_sector()

        vmobjects = [
            self.outer_circle,
            self.inner_circle,
            self.ghost_ticker,
            *self.ticks,
            self.time_sector,
            self.ticker,
            self.center_axle,
        ]
        super().__init__(*vmobjects)

    def get_time_sector(self):
        """TODO: Fix large angle case"""
        angle = PI / 2 - self.ticker_line.get_angle()
        if angle >= 3 * PI / 2:
            return VGroup(
                ArcBetweenPoints(
                    start=self.main_center + 0.75 * self.inner_radius * LEFT,
                    end=self.main_center + 0.75 * self.inner_radius * UP,
                    angle=(3 * PI / 2) - 0.01,
                ),
                ArcBetweenPoints(
                    start=self.ticker.get_end(),
                    end=self.main_center + 0.75 * self.inner_radius * LEFT,
                    angle=angle - ((3 * PI / 2) - 0.01),
                ),
            )
        return ArcBetweenPoints(
            start=self.ticker.get_end(),
            end=self.main_center + 0.75 * self.inner_radius * UP,
            angle=angle,
            color=RED,
        )

    def shift(self, *vectors: np.ndarray):
        for v in vectors:
            self.main_center += v
        return super().shift(*vectors)

    def scale(self, scale_factor: float, **kwargs):
        self.outer_radius = self.outer_radius * scale_factor
        self.inner_radius = self.inner_radius * scale_factor
        return super().scale(scale_factor, **kwargs)

    def update_ticker(self, dt):
        new_time = self.vtime + dt
        self.ticker_line.rotate(angle=-self.update_rate * dt, about_point=self.main_center)
        self.ticker.rotate(angle=-self.update_rate * dt, about_point=self.main_center)
        self.time_sector.become(self.get_time_sector())
        if self.vtime == 0:
            self.ghost_ticker.set_color(self.primary_color)
        self.vtime = new_time

    def get_time(self):
        return self.vtime

    def ticker_updater(self, _, dt):
        return self.update_ticker(dt)

    def start_running(self, update_rate=0.5):
        self.update_rate = update_rate
        self.add_updater(self.ticker_updater)

    def stop_running(self):
        self.remove_updater(self.ticker_updater)
