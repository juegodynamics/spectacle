from .particles import *


def get_particle_renderers():
    return {ELECTRON: Electron, PHOTON: Photon, QUARK: Quark, GLUON: Gluon}


def render_particle(particle, start, end, hide_labels=False):
    Renderer = get_particle_renderers()[particle]
    return Renderer(start=start, end=end, show_label=(not hide_labels))


def get_particle_interactions():
    return {
        ELECTRON: {
            ELECTRON: PHOTON,
            QUARK: PHOTON,
            PHOTON: ELECTRON,
        },
        PHOTON: {
            ELECTRON: PHOTON,
            QUARK: PHOTON,
        },
        QUARK: {
            ELECTRON: PHOTON,
            QUARK: GLUON,
            GLUON: QUARK,
        },
        GLUON: {
            QUARK: GLUON,
            GLUON: QUARK,
        },
    }


def chain_points(direction):
    return [2 * direction + DOWN, direction, 2 * direction + UP]


class TwoVertexLayout(VGroup):
    def __init__(
        self,
        incoming_particle_left=ELECTRON,
        is_left_anti=False,
        incoming_particle_right=ELECTRON,
        is_right_anti=False,
        virtual_particle=PHOTON,
        hide_labels=False,
    ):
        left_chain_points = chain_points(LEFT)
        if is_left_anti:
            left_chain_points.reverse()

        right_chain_points = chain_points(RIGHT)
        if is_right_anti:
            right_chain_points.reverse()

        particle_interaction_map = get_particle_interactions()

        outgoing_particle_left = particle_interaction_map[incoming_particle_left][virtual_particle]
        outgoing_particle_right = particle_interaction_map[incoming_particle_right][
            virtual_particle
        ]

        self.incoming_particles = [
            render_particle(
                incoming_particle_left,
                left_chain_points[0],
                left_chain_points[1],
                hide_labels=hide_labels,
            ),
            render_particle(
                incoming_particle_right,
                start=right_chain_points[0],
                end=right_chain_points[1],
                hide_labels=hide_labels,
            ),
        ]

        self.virtual_particle = render_particle(
            virtual_particle, start=LEFT, end=RIGHT, hide_labels=hide_labels
        )

        self.outgoing_particles = [
            render_particle(
                outgoing_particle_left,
                start=left_chain_points[1],
                end=left_chain_points[2],
                hide_labels=hide_labels,
            ),
            render_particle(
                outgoing_particle_right,
                start=right_chain_points[1],
                end=right_chain_points[2],
                hide_labels=hide_labels,
            ),
        ]

        vmobjects = [*self.incoming_particles, self.virtual_particle, *self.outgoing_particles]

        super().__init__(*vmobjects)

    def interact_animations(self):
        return [
            AnimationGroup(*[n.get_interact_animation() for n in self.incoming_particles]),
            Create(self.virtual_particle),
            AnimationGroup(*[n.get_interact_animation() for n in self.outgoing_particles]),
        ]


dl = "down-left"
dr = "down-right"
ul = "up-left"
ur = "up-right"

inner = "inner"
outer = "outer"


class FourVertexBoxLayout:
    def __init_layout__(
        self,
    ):
        # Separation Height for Box:
        mid_height = 1.5

        self.dirs = [dl, dr, ul, ur]
        self.layers = [inner, outer]
        self.x_diff = {dl: LEFT, dr: RIGHT, ul: LEFT, ur: RIGHT}
        self.y_diff = {dl: DOWN, dr: DOWN, ul: UP, ur: UP}

        self.points = {
            dl: {inner: LEFT + mid_height * DOWN / 2},
            dr: {inner: RIGHT + mid_height * DOWN / 2},
            ul: {inner: LEFT + mid_height * UP / 2},
            ur: {inner: RIGHT + mid_height * UP / 2},
        }

        inner_outer_spacing = [1, 1]

        for n in self.dirs:
            self.points[n][outer] = (
                self.points[n][inner]
                + self.x_diff[n] * inner_outer_spacing[0]
                + self.y_diff[n] * inner_outer_spacing[1]
            )

        def new_layers(new_value):
            return {inner: new_value(), outer: new_value()}

        def new_dirs(new_value):
            return {
                dl: new_value(),
                dr: new_value(),
                ul: new_value(),
                ur: new_value(),
            }

        self.particles = new_dirs(
            lambda: new_layers(lambda: new_dirs(lambda: new_layers(lambda: None)))
        )


class ParticleInteractionManager(FourVertexBoxLayout):
    def __init_particles__(self, hide_labels=False):
        self.__init_layout__()
        self.hide_labels = hide_labels
        self.particle_interaction_map = get_particle_interactions()
        self.particle_objects = []

    def interact(self, particle1, particle2):
        return self.particle_interaction_map[particle1][particle2]

    def render_particle(self, particle, start, end):
        return render_particle(particle, start, end, hide_labels=self.hide_labels)

    def create_particle(self, dir1, layer1, dir2, layer2, particle):
        self.particles[dir1][layer1][dir2][layer2] = self.render_particle(
            particle, self.points[dir1][layer1], self.points[dir2][layer2]
        )
        self.particle_objects.append(self.particles[dir1][layer1][dir2][layer2])
        return self.particles[dir1][layer1][dir2][layer2]


class FourVertexLayoutDoubleInterchange(VGroup, ParticleInteractionManager):
    def __init__(
        self,
        incoming_particle_left=ELECTRON,
        is_left_anti=False,
        incoming_particle_right=ELECTRON,
        is_right_anti=False,
        hide_labels=False,
    ):

        self.__init_particles__(hide_labels=hide_labels)

        # Incomings
        self.movement1 = [
            self.create_particle(dl, outer, dl, inner, incoming_particle_left),
            self.create_particle(dr, outer, dr, inner, incoming_particle_right),
        ]

        virtual_bot = self.interact(incoming_particle_left, incoming_particle_right)
        self.exchange1 = self.create_particle(dl, inner, dr, inner, virtual_bot)

        virtual_left = self.interact(incoming_particle_left, virtual_bot)
        virtual_right = self.interact(incoming_particle_right, virtual_bot)
        self.movement2 = [
            self.create_particle(dl, inner, ul, inner, virtual_left),
            self.create_particle(dr, inner, ur, inner, virtual_right),
        ]

        virtual_top = self.interact(virtual_left, virtual_right)
        self.exchange2 = self.create_particle(ul, inner, ur, inner, virtual_top)

        outgoing_particle_left = self.interact(virtual_left, virtual_top)
        outgoing_particle_right = self.interact(virtual_right, virtual_top)
        self.movement3 = [
            self.create_particle(ul, inner, ul, outer, outgoing_particle_left),
            self.create_particle(ur, inner, ur, outer, outgoing_particle_right),
        ]

        super().__init__(*self.particle_objects)

    def interact_animations(self):
        return [
            AnimationGroup(*[n.get_interact_animation() for n in self.movement1]),
            Create(self.exchange1),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement2]),
            Create(self.exchange2),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement3]),
        ]


class FourVertexLayoutCrossoverInterchange(VGroup, ParticleInteractionManager):
    def __init__(
        self,
        incoming_particle_left=ELECTRON,
        is_left_anti=False,
        incoming_particle_right=ELECTRON,
        is_right_anti=False,
        hide_labels=False,
    ):

        self.__init_particles__(hide_labels=hide_labels)

        # Incomings
        self.movement1 = [
            self.create_particle(dl, outer, dl, inner, incoming_particle_left),
            self.create_particle(dr, outer, dr, inner, incoming_particle_right),
        ]

        virtual_ltr = self.interact(incoming_particle_left, incoming_particle_right)
        virtual_rtl = self.interact(incoming_particle_left, incoming_particle_right)

        virtual_left = self.interact(incoming_particle_left, virtual_ltr)
        virtual_right = self.interact(incoming_particle_right, virtual_rtl)
        self.movement2 = [
            self.create_particle(dl, inner, ur, inner, virtual_ltr),
            self.create_particle(dr, inner, ul, inner, virtual_rtl),
            self.create_particle(dl, inner, ul, inner, virtual_left),
            self.create_particle(dr, inner, ur, inner, virtual_right),
        ]

        outgoing_particle_left = self.interact(virtual_left, virtual_rtl)
        outgoing_particle_right = self.interact(virtual_right, virtual_ltr)
        self.movement3 = [
            self.create_particle(ul, inner, ul, outer, outgoing_particle_left),
            self.create_particle(ur, inner, ur, outer, outgoing_particle_right),
        ]

        super().__init__(*self.particle_objects)

    def interact_animations(self):
        return [
            AnimationGroup(*[n.get_interact_animation() for n in self.movement1]),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement2]),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement3]),
        ]


class ProtonConfinement(VGroup):
    def __init__(
        self,
    ):
        self.particle_objects = []

        mid_separation = [1, 0.2]
        outer_sep1 = 0.75
        outer_sep2 = 2 * outer_sep1

        mid_inners = {
            ul: LEFT * mid_separation[0] + UP * mid_separation[1],
            dl: LEFT * mid_separation[0] + DOWN * mid_separation[1],
            dr: RIGHT * mid_separation[0] + UP * mid_separation[1],
            ur: RIGHT * mid_separation[0] + DOWN * mid_separation[1],
        }

        mid_outers = {
            ul: mid_inners[ul] + LEFT * outer_sep2,
            dl: mid_inners[dl] + LEFT * outer_sep1,
            ur: mid_inners[ur] + RIGHT * outer_sep1,
            dr: mid_inners[dr] + RIGHT * outer_sep2,
        }

        corner_spacing = [0, 2]

        outer_corner_base = {
            ul: mid_outers[dl] + LEFT * corner_spacing[0] + UP * corner_spacing[1],
            dl: mid_outers[dl] + LEFT * corner_spacing[0] + DOWN * corner_spacing[1],
            ur: mid_outers[ur] + RIGHT * corner_spacing[0] + UP * corner_spacing[1],
            dr: mid_outers[ur] + RIGHT * corner_spacing[0] + DOWN * corner_spacing[1],
        }

        fine_spacing = [outer_sep1, 0]

        def get_fine_corner(base, y, x):
            return outer_corner_base[base] + y * fine_spacing[1] + x * fine_spacing[0]

        fine_corners = {
            ul: {
                dl: get_fine_corner(ul, DOWN, LEFT),
                ur: get_fine_corner(ul, UP, RIGHT),
            },
            dl: {
                ul: get_fine_corner(dl, UP, LEFT),
                dr: get_fine_corner(dl, DOWN, RIGHT),
            },
            ur: {
                ul: get_fine_corner(ur, UP, LEFT),
                dr: get_fine_corner(ur, DOWN, RIGHT),
            },
            dr: {
                ur: get_fine_corner(dr, UP, RIGHT),
                dl: get_fine_corner(dr, DOWN, LEFT),
            },
        }

        # print(fine_corners)

        incoming = "incoming"
        outgoing = "outgoing"
        left = "left"
        middle = "middle"
        right = "right"

        red = RED
        blue = BLUE
        green = GREEN

        antired = TEAL
        antiblue = YELLOW
        antigreen = PINK

        angle = 0

        tip_alpha_bottom = (
            0.5
            * np.linalg.norm(mid_outers[dl] - outer_corner_base[dl])
            / np.linalg.norm(mid_outers[ul] - fine_corners[dl][ul])
        )

        tip_alpha_top = (
            0.48
            * np.linalg.norm(outer_corner_base[ul] - mid_outers[dl])
            / np.linalg.norm(fine_corners[ur][ul] - mid_inners[dr])
        )

        self.quarks = {
            incoming: {
                left: {
                    left: Quark(
                        start=fine_corners[dl][ul],
                        end=mid_outers[ul],
                        color=green,
                        angle=angle,
                        tip_alpha=tip_alpha_bottom,
                    ),
                    middle: Quark(
                        start=outer_corner_base[dl], end=mid_outers[dl], color=red, angle=angle
                    ),
                    right: Quark(
                        start=fine_corners[dl][dr], end=mid_inners[dl], color=blue, angle=angle
                    ),
                },
                right: {
                    left: Quark(
                        start=fine_corners[dr][dl], end=mid_inners[ur], angle=-angle, color=blue
                    ),
                    middle: Quark(start=outer_corner_base[dr], end=mid_outers[ur], angle=-angle),
                    right: Quark(
                        start=fine_corners[dr][ur],
                        end=mid_outers[dr],
                        angle=-angle,
                        tip_alpha=tip_alpha_bottom,
                        color=green,
                    ),
                },
            },
            outgoing: {
                left: {
                    left: Quark(start=mid_outers[ul], end=fine_corners[ul][dl], angle=angle),
                    middle: Quark(
                        start=mid_outers[dl],
                        end=outer_corner_base[ul],
                        angle=angle,
                        tip_alpha=tip_alpha_top,
                        color=blue,
                    ),
                    right: Quark(
                        start=mid_inners[ul], end=fine_corners[ul][ur], angle=angle, color=green
                    ),
                },
                right: {
                    left: Quark(
                        start=mid_inners[dr], end=fine_corners[ur][ul], angle=-angle, color=green
                    ),
                    middle: Quark(
                        start=mid_outers[ur],
                        end=outer_corner_base[ur],
                        angle=-angle,
                        tip_alpha=tip_alpha_top,
                        color=blue,
                    ),
                    right: Quark(start=mid_outers[dr], end=fine_corners[ur][dr], angle=-angle),
                },
            },
        }

        self.gluons = {
            ul: Gluon(start=mid_outers[ul], end=mid_inners[ul], color=green, anti_color=red),
            dl: Gluon(
                start=mid_outers[dl],
                end=mid_inners[dl],
                color=red,
                anti_color=blue,
            ),
            ur: Gluon(start=mid_inners[ur], end=mid_outers[ur], color=blue, anti_color=red),
            dr: Gluon(start=mid_inners[dr], end=mid_outers[dr], color=green, anti_color=red),
        }

        top_virtual = Chain(Quark, mid_inners[ur], ORIGIN, mid_inners[ul], color=red)

        bottom_virtual = Chain(Quark, mid_inners[dl], ORIGIN, mid_inners[dr], color=red)

        self.movement1 = [
            self.add_particle(self.quarks[incoming][left][middle]),
            self.add_particle(self.quarks[incoming][left][right]),
        ]

        self.exchange1 = self.add_particle(self.gluons[dl])

        self.movement2 = [
            self.add_particle(self.quarks[outgoing][left][middle]),
            self.add_particle(bottom_virtual),
            self.add_particle(self.quarks[incoming][right][right]),
        ]

        self.exchange2 = self.add_particle(self.gluons[dr])

        self.movement3 = [
            self.add_particle(self.quarks[outgoing][right][left]),
            self.add_particle(self.quarks[outgoing][right][right]),
        ]

        self.movement4 = [
            self.add_particle(self.quarks[incoming][right][left]),
            self.add_particle(self.quarks[incoming][right][middle]),
        ]

        self.exchange3 = self.add_particle(self.gluons[ur])

        self.movement5 = [
            self.add_particle(self.quarks[outgoing][right][middle]),
            self.add_particle(top_virtual),
            self.add_particle(self.quarks[incoming][left][left]),
        ]

        self.exchange4 = self.add_particle(self.gluons[ul])

        self.movement6 = [
            self.add_particle(self.quarks[outgoing][left][left]),
            self.add_particle(self.quarks[outgoing][left][right]),
        ]

        super().__init__(*self.particle_objects)

    def add_particle(self, particle):
        self.particle_objects.append(particle)
        return particle

    def interact_animations(self):
        return [
            AnimationGroup(*[n.get_interact_animation() for n in self.movement1]),
            Create(self.exchange1),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement2]),
            Create(self.exchange2),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement3]),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement4]),
            Create(self.exchange3),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement5]),
            Create(self.exchange4),
            AnimationGroup(*[n.get_interact_animation() for n in self.movement6]),
        ]
