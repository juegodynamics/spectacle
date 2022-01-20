from spectacle import *


class SierpinskiUnit(Polygram):
    def __init__(self, *vertices: Sequence[float], shape: Polygram = None, color=BLUE, **kwargs):
        super().__init__(vertices, color=color, **kwargs)

    def get_sub_units(self) -> Sequence["SierpinskiUnit"]:
        vertices: Sequence[np.ndarray] = self.get_vertices()
        subunits: Sequence[SierpinskiUnit] = []
        for index, v in enumerate(vertices):
            v_last, v_next = vertices[index - 1], vertices[(index + 1) % len(vertices)]
            subunits.append(
                self.copy()
                .match_points(
                    SierpinskiUnit(
                        *[
                            midpoint(v_last, v),
                            v,
                            midpoint(v, v_next),
                        ]
                    )
                )
                .set_stroke(width=self.get_stroke_width() * (np.log(2) / np.log(3)))
            )
        return subunits


class Sierpinski(VGroup):
    def __init__(self, *vertices: Sequence[float], num_iterations=3, color=BLUE, **kwargs):
        self._sub_units = [SierpinskiUnit(*vertices, color=color, **kwargs)]
        super().__init__(**kwargs)
        self.iterate(num_iterations)

    def iterate(self, num_iterations=1) -> Sequence[SierpinskiUnit]:
        if num_iterations == 0:
            if hasattr(self, "submobjects"):
                original_objects = self.submobjects
                self.remove(*original_objects)
            self.add(*self._sub_units)
            return self
        self._sub_units = [
            sub_unit for _unit in self._sub_units for sub_unit in _unit.get_sub_units()
        ]
        return self.iterate(num_iterations - 1)

    # @override_animate(iterate)
    # def _iterate_animation(self, num_itera)


class FractalDemo(Scene):
    def construct(self):
        fractal = Sierpinski(
            *Triangle().scale(2).get_vertices(),
            num_iterations=1,
            stroke_width=DEFAULT_STROKE_WIDTH * 0.8,
        )

        self.add(fractal)
        for _ in range(12):
            next_fractal = fractal.copy().iterate()
            self.play(Transform(fractal, next_fractal), run_time=0.2)
            fractal = next_fractal
            self.wait(0.1)
