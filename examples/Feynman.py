from spectacle import *


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


BG_COLOR = "#0A1929"


class Feynman(Composer):
    def construct(self):
        bound = 20
        dx = 0.5

        field = NumberPlane(
            x_range=[-bound, bound, dx],
            y_range=[-bound / 2, bound / 2, dx],
            background_line_style={"stroke_width": DEFAULT_STROKE_WIDTH / 2},
        ).set_color_by_gradient(RAINBOW)
        self.add(field)

        field.prepare_for_nonlinear_transform()

        def transform(p):
            x, y = p[0], p[1]
            r = np.linalg.norm(p)
            return point(
                -y * np.cos(PI * r),
                x * np.cos(PI * r),
            )

        self.play(field.animate.apply_function(transform), run_time=5)
