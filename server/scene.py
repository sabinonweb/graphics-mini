from manim import *

class SquareAndCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(PINK, opacity=0.5)
        
        square = Square()
        square.set_fill(BLUE, opacity=0.5)
        
        square.next_to(circle, UP, buff=0.5)
        self.play(Create(circle), Create(square))
        
        
class DifferentRotations(Scene):
    def construct(self):
        left_square = Square(color=BLUE, fill_opacity=0.7).shift(2 * LEFT)
        right_square = Square(color=GREEN, fill_opacity=0.7).shift(2 * RIGHT)
        
        self.play(left_square.animate.rotate(PI), Rotate(right_square, angle=PI), run_time=2)
        self.wait
        
class Shapes(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        triangle = Triangle()
        
        circle.shift(LEFT)
        square.shift(UP)
        triangle.shift(RIGHT)
        
        self.add(circle, square, triangle)
        self.wait(1)
        
class MObjectPlacement(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        triangle = Triangle()
        
        circle.move_to(LEFT * 2)
        square.next_to(circle, LEFT)
        triangle.align_to(circle, LEFT)
        
        self.add(circle, square, triangle)
        self.wait(1)
        
class MObjectStyling(Scene):
    def construct(self):
        circle = Circle().shift(LEFT)
        square = Square().shift(UP)
        triangle = Triangle().shift(RIGHT)

        circle.set_stroke(color=GREEN, width=20)
        square.set_fill(YELLOW, opacity=1.0)
        triangle.set_fill(PINK, opacity=0.5)

        self.add(circle, square, triangle)
        self.wait(1)
        
class SomeAnimations(Scene):
    def construct(self):
        square = Square()
        
        self.play(FadeIn(square))
        self.play(Rotate(square, PI / 4))
        self.play(FadeOut(square))
        self.wait()
        
class AnimateMore(Scene):
    def construct(self):
        square = Square().set_fill(RED, opacity=1.0)
        self.add(square)
        
        self.play(square.animate.set_fill(WHITE))
        self.play(square.animate.shift(UP).rotate(PI / 3))
        self.wait(1)