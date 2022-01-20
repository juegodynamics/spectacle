from spectacle import *


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
