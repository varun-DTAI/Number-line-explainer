# manim -pql number_line_1.py  NumberLineConstruction
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from gpt_helper import talk_to_gpt
from googletrans import Translator, LANGUAGES
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
CHECKPOINT_DOT_COLOR = GREEN

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
        checkpoint_dot = Dot(point=number_line.n2p(final_position), color=CHECKPOINT_DOT_COLOR)
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
        self.wait()
        return dot

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
        question = "Varun hopped 3 steps and hopped back 4 steps. He again jumped 3 hops twice in backward direction. How far away is he from the start point?"
        response = talk_to_gpt(question)
        print(response)
        
        r_preamble = r"""
        \usepackage{fontspec}
        \usepackage{polyglossia}
        \setdefaultlanguage{hindi}
        \setmainfont[Script=Devanagari]{Nakula}
        """
        #\babelprovide[import = hi, main]{hindi}
        # hn_tex = TexTemplate(
        # preamble=r_preamble,
        # tex_compiler="lualatex",
        # )
        
        translator = Translator()
        translated_sentence = translator.translate(question, src='en', dest='hi')
        print(translated_sentence.text)
        with self.voiceover(text=translated_sentence.text) as tracker:
            # text = Title(
            # translated_sentence.text,
            # tex_environment="justify",
            # tex_template=hn_tex,
            # )
            
            text = Tex(question)
            text.scale(0.8)
            self.play(AddTextLetterByLetter(text), run_time=tracker.duration)
        self.play(Transform(text, text.move_to(UP * 3)))
        
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
            translated_sentence = translator.translate(step["description"], src='en', dest='hi')
            with self.voiceover(text=translated_sentence.text) as tracker :
                    for micro_step in step["commands"] :
                        dot = self.show_jumps(micro_step["Jump"], number_line1, tracker.duration, dot)
                        self.wait()
        
        final_position = micro_step["Jump"]["start"] + micro_step["Jump"]["direction"]*micro_step["Jump"]["length"]
        with self.voiceover(text="After performing the steps, we finally reach the point <bookmark mark='A'/> "+str(final_position)) as tracker :
            self.wait_until_bookmark("A")
            self.play(Indicate(dot, scale_factor=3))
            self.wait()