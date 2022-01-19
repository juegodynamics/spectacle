from spectacle import *


def make_electron_ball(color=GREEN, text_color=BLACK):
    return VGroup(
        Circle(radius=0.25, color=color, fill_opacity=1), MathTex(ELECTRON, color=text_color)
    )


def make_electron_shell(color=GREEN):
    return VGroup(Circle(radius=0.25, color=GREEN), MathTex(ELECTRON))


class ElectricCharge(VGroup):
    def __init__(self, center=ORIGIN, color=GREEN, init_velocity=ORIGIN, charge=1, is_shell=False):
        self.center = center
        self.charge = charge
        self.is_shell = is_shell
        mobject_func = {True: make_electron_shell}.get(is_shell, make_electron_ball)

        self.mobject = mobject_func(color=color).move_to(center)

        self.velocity = init_velocity

        self.acceleration = point(0, 0)
        # self.acceleration_vector = Arrow(start=self.center, end=self.center+self.acceleration, buff=0)

        vmobjects = [self.mobject]

        super().__init__(*vmobjects)

    def get_center(self):
        return self.center

    def get_source_func(self, p):
        x, y, = (
            p[0],
            p[1],
        )
        x0, y0 = self.center[0], self.center[1]
        r = np.linalg.norm(point(x - x0, y - y0))
        if r <= 0.15:
            return point(0, 0)
        efield_mag = 1 / (r ** 3)
        return self.charge * point((x - x0) * efield_mag, (y - y0) * efield_mag)

    def get_ball(self):
        return self.mobject

    def update_position_by_field(self, mobject, dt):
        self.acceleration = self.charge * self.field_func(self.center)
        self.velocity = self.velocity + self.acceleration * dt
        self.center = self.center + self.velocity * dt

        mobject.move_to(self.center)

    def get_updater_by_field(self, field_func):
        self.field_func = field_func
        return lambda mob, dt: self.update_position_by_field(mob, dt)


class FeynmanVideo(Scene):
    def construct(self):
        # self.scene1()
        # self.scene2()
        self.scene3()

    def scene1(self):
        """Scene 1:
        Show an electron generating an electric field
        """
        bound = 10
        dx = 0.5
        x_diff = 2

        held_electron = ElectricCharge(center=LEFT * x_diff, charge=10)
        efield = ArrowVectorField(held_electron.get_source_func)
        self.play(Create(efield), FadeIn(held_electron.get_ball().shift(OUT)), run_time=3)

        # efield.start_animation(warm_up=False, flow_speed=1.5)

        self.wait(4)

        free_electron = ElectricCharge(
            center=RIGHT * x_diff + DOWN * 4.2, init_velocity=point(-0.85, 2), is_shell=True
        )
        self.add(free_electron)

        free_electron.add_updater(
            free_electron.get_updater_by_field(held_electron.get_source_func)
        )

        self.play(FadeIn(free_electron), run_time=0.2)

        self.wait(10)

        self.play(
            efield.animate.set_color(BLACK),
            FadeOut(held_electron),
            FadeOut(free_electron),
            run_time=2,
        )

    def scene2(self):
        """Scene 2:
        Show two electrons repelling
        """
        x_diff = 2

        field_height = 0.25

        left_center = LEFT * x_diff + DOWN * 4.2
        right_center = RIGHT * x_diff + DOWN * 4.2

        free_electron_left = ElectricCharge(
            center=left_center, init_velocity=point(0.75, 1.8), is_shell=True, charge=2
        )
        free_electron_right = ElectricCharge(
            center=right_center, init_velocity=point(-0.75, 1.8), is_shell=True, charge=2
        )

        x_range = [left_center[0], right_center[0], 0.5]
        y_range = [left_center[1] - field_height, left_center[1] + field_height, field_height / 5]

        efield_left = ArrowVectorField(free_electron_left.get_source_func)
        efield_right = ArrowVectorField(free_electron_right.get_source_func)

        # self.add(free_electron_left, free_electron_right, efield_left, efield_right)
        self.add(free_electron_left, free_electron_right)

        free_electron_left.add_updater(
            free_electron_left.get_updater_by_field(free_electron_right.get_source_func)
        )
        free_electron_right.add_updater(
            free_electron_right.get_updater_by_field(free_electron_left.get_source_func)
        )

        self.wait(8)
        self.remove(free_electron_left, free_electron_right)

    def scene3(self):
        """Collisions"""

        floor = Line(start=-10 * RIGHT + 2 * DOWN, end=10 * RIGHT + 2 * DOWN)
        shading = VGroup(
            *[
                Line(start=(n - 1) * RIGHT + 4 * DOWN, end=n * RIGHT + 2 * DOWN)
                for n in np.arange(-11, 11)
            ]
        )

        self.play(Create(floor), Create(shading))

    def scene4(self):
        """Electron is a point"""

        electron = ElectricCharge()
        self.play(FadeIn(electron))
        self.wait()

        electron_dot = Dot(color=WHITE, radius=DEFAULT_DOT_RADIUS / 2)

        self.play(electron.animate.become(electron_dot), run_time=2)

        self.wait(2)


class CollisionScene(Scene):
    BASE_VELOCITY = 1

    def construct(self):
        floor = Line(start=-10 * RIGHT + 2 * DOWN, end=10 * RIGHT + 2 * DOWN)
        shading = VGroup(
            *[
                Line(start=(n - 1) * RIGHT + 4 * DOWN, end=n * RIGHT + 2 * DOWN)
                for n in np.arange(-11, 11)
            ]
        )

        self.play(Create(floor), Create(shading))

        start_separation = 9

        left_box = Square(side_length=1, color=GREEN, fill_opacity=1).shift(
            (start_separation - 1) * LEFT + 1.5 * DOWN
        )
        right_box = Square(side_length=1, color=GREEN, fill_opacity=1).shift(
            start_separation * RIGHT + 1.5 * DOWN
        )
        photon_box = Rectangle(height=1, width=0.25, color=GOLD, fill_opacity=1).shift(
            (start_separation - 1.5) * LEFT + 1.5 * DOWN
        )

        self.add(left_box, right_box, photon_box)

        self.left_center = left_box.get_center()
        self.right_center = right_box.get_center()
        self.photon_center = photon_box.get_center()

        self.left_velocity = point(self.BASE_VELOCITY, 0)
        self.right_velocity = point(-1 * self.BASE_VELOCITY, 0)
        self.photon_velocity = point(self.BASE_VELOCITY, 0)

        self.virtual_time = 0
        self.trigger_time = 6
        self.triggered_left = False
        self.triggered_photon = False

        left_box.add_updater(self.update_left)
        photon_box.add_updater(self.update_photon)
        right_box.add_updater(self.update_right)

        self.wait(10)

    def update_left(self, box, dt):
        self.virtual_time += dt
        if (self.virtual_time > self.trigger_time) and (not self.triggered_left):
            self.triggered_left = True
            self.left_velocity = -1 * point(self.BASE_VELOCITY, 0)
        self.left_center = self.left_center + self.left_velocity * dt
        box.move_to(self.left_center)

    def update_photon(self, box, dt):
        if (self.virtual_time > self.trigger_time) and (not self.triggered_photon):
            self.triggered_photon = True
            self.photon_velocity = self.photon_velocity * 1.4
        self.photon_center = self.photon_center + self.photon_velocity * dt
        if np.abs(self.photon_center[0] + (0.25 / 2) - (self.right_center[0] - 0.5)) < 0.01:
            self.photon_velocity = point(self.BASE_VELOCITY, 0)
        box.move_to(self.photon_center)

    def update_right(self, box, dt):
        if np.abs(self.photon_center[0] + (0.25 / 2) - (self.right_center[0] - 0.5)) < 0.01:
            self.right_velocity = point(self.BASE_VELOCITY, 0)
        self.right_center = self.right_center + self.right_velocity * dt
        box.move_to(self.right_center)
