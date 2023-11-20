from manim import *

class Test(Scene):
    def construct(self):
        # Create a group of objects
        group_of_objects = VGroup(
            Circle(radius=0.5, color=BLUE),
            Square(side_length=1, color=RED),
            Triangle(fill_opacity=1, color=YELLOW)
        )
        
        # Create a target object
        target_object = RegularPolygon(n=6, color=GREEN)
        
        # Display the initial group
        self.play(Create(group_of_objects))
        
        # Transform the group into the target object
        self.play(Transform(group_of_objects, target_object))
        self.wait()

