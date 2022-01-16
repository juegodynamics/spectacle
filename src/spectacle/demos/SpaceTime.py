from spectacle import *


class SpaceTime(Scene):
    def construct(self):
        bounds = 5
        dx = 0.1
        # grid = NumberPlane(
        #     x_range=[-bounds,bounds, dx],
        #     y_range=[-bounds, bounds, dx],
        #     background_line_style={
        #         "stroke_color": TEAL,
        #         "stroke_width": 2,
        #         "stroke_opacity": 0.6
        #     },
        #     faded_line_style={
        #         "stroke_opacity": 0,
        #     }
        # ).set_color_by_gradient(RAINBOW)
        horizontals = [
            Line(
                start=as_point(-bounds, y),
                end=as_point(bounds, y),
                stroke_width=2,
            )
            for y in np.arange(-bounds, bounds, dx)
        ]
        verticals = [
            Line(
                start=as_point(x, -bounds),
                end=as_point(x, bounds),
                stroke_width=2,
            )
            for x in np.arange(-bounds, bounds, dx)
        ]

        grid = LineGrid().set_color_by_gradient(RAINBOW)
        # self.add(grid)

        # grid.prepare_for_nonlinear_transform()

        def transform(p):
            x, y = p[0], p[1]
            r = np.linalg.norm(p)
            f = 0.1

            return [x + f * np.cos(2 * PI * r), y + f * np.sin(2 * PI * r), 0]

        # self.play(grid.animate.apply_function(transform),run_time=10)
        self.add(grid.apply_function(transform))
        # self.add(grid)
        # self.wait(4)


class LineGrid(VMobject):
    def __init__(self, bounds=5, dx=1, **kwargs):
        print("#### Starting __init__")
        super().__init__(**kwargs)
        self.horizontals = [
            Line(
                start=as_point(-bounds, y),
                end=as_point(bounds, y),
                stroke_width=2,
            )
            for y in np.arange(-bounds, bounds, dx)
        ]
        self.verticals = [
            Line(
                start=as_point(x, -bounds),
                end=as_point(x, bounds),
                stroke_width=2,
            )
            for x in np.arange(-bounds, bounds, dx)
        ]

        self.add(*[*self.horizontals, *self.verticals])
        print("#### Finished __init__")

    def apply_function(self, function):
        for l in [*self.horizontals, *self.verticals]:
            l.apply_function(function)
        return self
