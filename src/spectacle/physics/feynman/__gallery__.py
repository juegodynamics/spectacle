from particles import *
from layout import *


class Gallery_QED_FeynmanDiagramScene(Scene):
    def construct(self):
        incoming1 = Quark(start=1.5 * LEFT + DOWN, end=ORIGIN, color=WHITE)

        outgoing1 = Quark(start=ORIGIN, end=1.5 * LEFT + UP, color=WHITE)
        out = Gluon(start=ORIGIN, end=RIGHT * 2)
        # diagram = ProtonConfinement()

        step1 = Text("An incoming quark").shift(DOWN * 2)
        self.play(incoming1.get_interact_animation(), Create(step1), run_time=2)

        self.wait()

        step2 = Text("emits a gluon").next_to(step1, DOWN / 2)
        self.play(
            out.get_interact_animation(),
            outgoing1.get_interact_animation(),
            Create(step2),
            run_time=2,
        )

        self.wait(2)

        incoming2 = Quark(start=2.5 * RIGHT + DOWN, end=RIGHT, color=WHITE)
        outgoing2 = Quark(start=RIGHT, end=2.5 * RIGHT + UP, color=WHITE)

        step3 = Text("Another incoming quark").shift(DOWN * 2)
        step4 = Text("absorbs a gluon").next_to(step3, DOWN / 2)

        self.play(
            incoming1.animate.shift(LEFT), outgoing1.animate.shift(LEFT), out.animate.shift(LEFT)
        )
        self.play(
            incoming2.get_interact_animation(),
            outgoing2.get_interact_animation(),
            TransformMatchingShapes(step1, step3),
            TransformMatchingShapes(step2, step4),
        )

        self.wait()

        self.play(FadeOut(step3), FadeOut(step4))

        step5 = Text("A red quark", t2c={"red": RED}).shift(DOWN * 2)
        step6 = Text("emits a red/antiblue gluon", t2c={"red": RED, "antiblue": BLUE}).next_to(
            step5, DOWN / 2
        )
        step7 = Text("and becomes blue", t2c={"blue": BLUE}).next_to(step6, DOWN / 2)
        self.play(incoming1.animate.set_color(RED), Create(step5))
        self.wait()
        self.play(out.animate.set_color_by_gradient([RED, BLUE, RED, BLUE, RED]), Create(step6))
        self.wait()
        self.play(outgoing1.animate.set_color(BLUE), Create(step7))
        self.wait()


class Gallery_Proton(Scene):
    def construct(self):
        diagram = ProtonConfinement()
        self.add(diagram)

        self.play(diagram.animate.set_color(DARKER_GRAY))

        diagram2 = ProtonConfinement()

        for anim in diagram2.interact_animations():
            self.play(anim)

        self.wait()


class ParticleAntiparticle(Scene):
    def construct(self):
        photon_incoming = Photon(start=LEFT * 2, end=LEFT / 2)

        angle = PI / 2

        electrons = [
            Electron(start=LEFT / 2, end=RIGHT / 2, angle=angle),
            Electron(start=RIGHT / 2, end=LEFT / 2, angle=angle),
        ]

        photon_outgoing = Photon(start=RIGHT / 2, end=RIGHT * 2)

        self.play(*[Create(n) for n in [photon_incoming, *electrons, photon_outgoing]])

        self.wait()
