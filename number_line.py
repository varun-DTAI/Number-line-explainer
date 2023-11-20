from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from gpt_helper import talk_to_gpt

# Index 1 is forward direction
# Index -1 is backward direction

# Negative means it'll come above the axis
ANGLE = -TAU/3
STROKE_COLOR = {1 : YELLOW, -1 : ORANGE}
MAIN_NUMBER_LINE_COLOR = WHITE
JUMP_TEXT_COLOR = BLUE
TOTAL_JUMP_TEXT_COLOR = GREEN
DOT_COLOR = RED
DOT_RADIUS = DEFAULT_DOT_RADIUS+0.05
TEXT_POSITION = {1 : UP, -1 : DOWN}

class NumberLineConstruction(VoiceoverScene):
    def show_arc(self, number_line, start, leap, direction):
        end = start + direction*leap

        jump_arc = ArcBetweenPoints(number_line.n2p(start), number_line.n2p(end), angle = ANGLE, stroke_color=STROKE_COLOR[direction])
        current_jump_label = Integer(leap, color=JUMP_TEXT_COLOR, font_size= 36)   #next_to(jump_arc, TEXT_POSITION[direction])
        total_label = Integer(end, color=TOTAL_JUMP_TEXT_COLOR)
        return jump_arc, current_jump_label, total_label
        
    def show_jumps(self, micro_step, number_line, total_displacement, time, old_dot):
        start = micro_step["start"] 
        leap = micro_step["length"]
        direction = micro_step["direction"]
        
        current_displacement = start
        # line_lap = Line(number_line.n2p(total_displacement), number_line.n2p(total_displacement + direction*leap), stroke_color = MAIN_NUMBER_LINE_COLOR)
        group_of_miniarcs = VGroup()
        for i in range(leap):
            one_step, one_step_label, next_step_label = self.show_arc(number_line, current_displacement, 1, direction)
            self.play(Create(one_step), run_time = time/leap)
            group_of_miniarcs.add(one_step)
            current_displacement += direction*1
        
        jump_arc, current_jump_label, total_label = self.show_arc(number_line, total_displacement, leap, direction)
        # self.play(*[FadeOut(obj) for obj in group])
        total_displacement += direction*leap
        
        dot = Dot(point=number_line.n2p(total_displacement), radius=DOT_RADIUS, color=DOT_COLOR)
        checkpoint_dot = Dot(point=number_line.n2p(total_displacement), color=GREEN)
        self.play(Transform(group_of_miniarcs, jump_arc))
        self.play(Write(current_jump_label.next_to(jump_arc, TEXT_POSITION[direction])))
        
        self.play(Transform(old_dot, dot), run_time = 1)
        self.add(checkpoint_dot)
        self.remove(old_dot)
        
        self.wait()
        return dot, total_displacement

    def get_extreme(self, response):
        total = 0
        maximum = 0
        minimum = 1000
        for step in response["representation_steps"]:
            for micro_step in step["commands"]:
                direction = micro_step["Jump"]["direction"]
                length = micro_step["Jump"]["length"]
                # start = micro_step["Jump"]["start"]
                total += direction*length
                maximum = max(total, maximum)
                minimum = min(total, minimum)
        return maximum, minimum
    
    # def show_result(final_position, number_line):
        
        
    
    def construct(self):
        self.set_speech_service(GTTSService(transcription_model='base'))
        question = "Varun hopped 3 steps and hopped back 4 steps. He again jumped 3 hops twice in backward direction. How far away is he from the start point?"
        # question = "Divide 4 from 16"
        response = talk_to_gpt(question)
        # response = {'representation_steps': [{'description': 'Jump 3 steps forward', 'commands': [{'Jump': {'direction': 1, 'length': 3}}]}, {'description': 'Jump 4 steps backward', 'commands': [{'Jump': {'direction': -1, 'length': 4}}]}]}
        print(response)
        print(type(response))
        
        with self.voiceover(text=response["Question"]) as tracker:
            text = Tex(response["Question"])
            text.scale(0.8)
            self.play(AddTextLetterByLetter(text), run_time=tracker.duration)
        self.play(Transform(text, text.move_to(UP * 3)))
        
        maximum, minimum = self.get_extreme(response)
        
        number_line1 = NumberLine(x_range=[minimum-2, maximum+2], length=10, include_numbers=False, include_ticks=False, font_size=30)
        number_line2 = NumberLine(x_range=[minimum-2, maximum+2], length=10, include_numbers=True, include_ticks=True) #numbers_with_elongated_ticks=range(minimum, maximum, 10)
        
        self.play(Create(number_line1))
        self.play(Create(number_line2))
        self.wait()
        
        checkpoint_dot = Dot(point=number_line1.n2p(0), color=GREEN)
        dot = Dot(point=number_line1.n2p(0), radius=DOT_RADIUS, color=DOT_COLOR)
        self.add(checkpoint_dot)
        self.add(dot)
        total_displacement = 0
        for step in response["representation_steps"]:
            with self.voiceover(text=step["description"]) as tracker :
                    for micro_step in step["commands"] :
                        dot, total_displacement = self.show_jumps(micro_step["Jump"], number_line1, total_displacement, tracker.duration, dot)
                        self.wait()
        
        with self.voiceover(text="After performing the steps, we finally reach the point <bookmark mark='A'/>"+str(total_displacement)) as tracker :
            self.wait_until_bookmark("A")
            self.play(Indicate(dot, scale_factor=3))
            self.wait()