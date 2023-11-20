from manim import *

class Sample(Scene):
    def construct(self):
        line = NumberLine()
        self.play(Create(line))