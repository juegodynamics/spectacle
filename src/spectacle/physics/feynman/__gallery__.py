from .particles import *
from .layout import *


class Gallery_QED_FeynmanDiagramScene(Scene):
    def construct(self):
        electronBall = VGroup(MathTex(ELECTRON), Circle())
        self.add(electronBall)


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
