# manim -pql number_line_2.py  NumberLineConstruction --disable_caching
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from gpt_helper import talk_to_gpt
from googletrans import Translator
translator = Translator()
config.disable_caching = True
# Index 1 is forward direction
# Index -1 is backward direction
config.frame_size = 720, 1280
# config.frame_width = 6
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
    
    # Creates and returns an arc from start to end
    def show_arc(self, number_line, start, leap, direction):
        end = start + direction*leap
        jump_arc = ArcBetweenPoints(number_line.n2p(start), number_line.n2p(end), angle = ANGLE, stroke_color=STROKE_COLOR[direction])
        current_jump_label = Integer(leap, color=JUMP_TEXT_COLOR, font_size= 36)   
        return jump_arc, current_jump_label
    
    # Shows a dot transition from old point to new point
    # Also leaves a checkpoint forever
    def show_dot(self, number_line, start_position, old_dot, final_position):
        if old_dot == None:
            checkpoint_dot = Dot(point=number_line.n2p(start_position), color=GREEN)
            self.add(checkpoint_dot)
            old_dot = Dot(point=number_line.n2p(start_position), radius=DOT_RADIUS, color=DOT_COLOR)    
            
        dot = Dot(point=number_line.n2p(final_position), radius=DOT_RADIUS, color=DOT_COLOR)
        checkpoint_dot = Dot(point=number_line.n2p(final_position), color=GREEN)
        self.play(Transform(old_dot, dot, replace_mobject_with_target_in_scene=True), run_time = 1)
        # self.remove(old_dot)
        self.add(checkpoint_dot)
        return dot
    
    def show_jumps(self, micro_step, number_line, time, old_dot):
        leap = micro_step["length"]
        direction = micro_step["direction"]        
        current_position = micro_step["start"] 
        final_position = current_position+direction*leap
        group_of_miniarcs = VGroup()
        
        # Create miniarcs of distance 1 and display
        for i in range(leap):
            one_step, one_step_label = self.show_arc(number_line, current_position, 1, direction)
            self.play(Create(one_step), run_time = time/leap)
            group_of_miniarcs.add(one_step)
            current_position += direction*1
        
        # Create an arc of the actual leap
        jump_arc, current_jump_label = self.show_arc(number_line, micro_step["start"], leap, direction)
        
        # Transform all the miniarcs into the big arc
        self.play(Transform(group_of_miniarcs, jump_arc))
        
        # Show current step label
        self.play(Write(current_jump_label.next_to(jump_arc, TEXT_POSITION[direction])))
        
        # Show and return the dot movement
        dot = self.show_dot(number_line, micro_step["start"], old_dot, final_position)
        # self.wait()
        return dot

    # Pre calculate the max and min 
    def get_extreme(self, response):
        total = 0
        maximum = 0
        minimum = 2**16 - 1
        for step in response["representation_steps"]:
            for micro_step in step["commands"]:
                direction = micro_step["Jump"]["direction"]
                length = micro_step["Jump"]["length"]
                start = micro_step["Jump"]["start"]
                total = start + direction*length
                maximum = max(total, start, maximum)
                minimum = min(total, start, minimum)
        return maximum, minimum        
        
    
    def construct(self):
        self.set_speech_service(GTTSService(transcription_model='base'))
        # question = "Varun hopped 3 steps and hopped back 4 steps. He again jumped 3 hops twice in backward direction. How far away is he from the start point?"
        # question = "Represent 3 multiplied by 4 in a number line"
        question = "What is 16 divided by 4? Show the working on a number line"
        # question = "Madhavi is very tall and can jump 2 steps in one hop. She hops 3 times. Where is she finally?" # Incomplete conclusion
        # question = "Which number will we reach if we start from -4 and move 7 steps to the right?"
        # question = "Write the next four integers in each of the following sequences: -12, -10, -8, -6"    # Bad result
        # question = "Write the next four integers in the sequence: 12, 10, 8, 6"
        
        
        response = talk_to_gpt(question)
        # response = {'representation_steps': [{'description': 'Firstly, Madhavi jumps 2 steps forward', 'commands': [{'Jump': {'direction': 1, 'length': 2, 'start': 0}}]}, {'description': 'Then she jumps 2 steps forward again', 'commands': [{'Jump': {'direction': 1, 'length': 2, 'start': 2}}]}, {'description': 'Finally, she jumps 2 steps forward for the last time', 'commands': [{'Jump': {'direction': 1, 'length': 2, 'start': 4}}]}], 'finishing_step': 'After these steps, Madhavi finally reaches the position 6'}
        print(response)
        
        with self.voiceover(text=question) as tracker:
            text = Tex(question)
            text.scale(0.8)
            self.play(AddTextLetterByLetter(text), run_time=tracker.duration)
        self.play(text.animate.to_edge(UP))
        
        maximum, minimum = self.get_extreme(response)
        
        number_line1 = NumberLine(x_range=[minimum-2, maximum+2], length=10, include_numbers=False, include_ticks=False, font_size=30)
        number_line2 = NumberLine(x_range=[minimum-2, maximum+2], length=10, include_numbers=True, include_ticks=True) #numbers_with_elongated_ticks=range(minimum, maximum, 10)
        
        self.play(Create(number_line1))
        self.play(Create(number_line2))
        self.wait()
        
        # None type dot as we don't know starting point
        dot = None
        
        
        # Loop on the steps of representation
        for step in response["representation_steps"]:
            sentence = translator.translate(step["description"])
            print("Translated text: ",sentence.text)
            with self.voiceover(text=sentence.text) as tracker :
                    for micro_step in step["commands"] :
                        dot = self.show_jumps(micro_step["Jump"], number_line1, tracker.duration, dot)
                        self.wait()
        
        
        final_position = micro_step["Jump"]["start"] + micro_step["Jump"]["direction"]*micro_step["Jump"]["length"]
        with self.voiceover(text=response["finishing_step"]) as tracker :
            try:
                self.wait_until_bookmark('A')
                self.play(Indicate(dot, scale_factor=3))
            except:
                self.play(Indicate(dot, scale_factor=3))
            self.wait()