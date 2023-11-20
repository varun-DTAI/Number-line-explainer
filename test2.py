from googletrans import Translator
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

translator = Translator()
t = translator.translate('Hi I am very fond of food', dest='kn')

class NumberLineConstruction(VoiceoverScene):
    def construct(self):
            self.set_speech_service(GTTSService(transcription_model='base', lang="kn"))
            question = "Varun hopped 3 steps and hopped back 4 steps. He again jumped 3 hops twice in backward direction. How far away is he from the start point?"
            response = {'representation_steps': [{'description': 'Firstly, jump 3 steps forward', 'commands': [{'Jump': {'direction': 1, 'length': 3, 'start': 0}}]}, {'description': 'Then jump 4 steps backward', 'commands': [{'Jump': {'direction': -1, 'length': 4, 'start': 3}}]}, {'description': 'Finally, jump 3 steps backward twice', 'commands': [{'Jump': {'direction': -1, 'length': 3, 'start': -1}}, {'Jump': {'direction': -1, 'length': 3, 'start': -4}}]}]}
            print(response)
            print(type(response))
            
            for step in response["representation_steps"]:
                sentence = translator.translate(step["description"], src="en", dest="kn")
                print("Translated text: ",sentence.text)
                with self.voiceover(text=sentence.text) as tracker :
                        