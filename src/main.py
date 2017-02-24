from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.graphics import *
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import *
import json, sys, re
from os.path import join, dirname
from subprocess import Popen
from sys import platform

from text_processor import text_processor

#This is the games main widget.
#TODO make another widget to float ontop as an ingame menu or add
# navigation tools somewhere in this widget
class hnsGame(Widget):

    def __init__(self):
        super(hnsGame, self).__init__()
        self.utils = text_processor()

    def hostage_taker_query(self, text):
        NLC_class = self.utils.nlc_classify_top_result(text)
        self.ids['mainImage'].source = "hostage_1.jpg"
        self.ids['scrollidLeft'].children[0].text = "Hostage Taker: " + "Leave me alone! I don't wanna talk about: " + NLC_class

    def rr_process(self, text):
        self.ids['mainImage'].source = "watson_avatar.jpg"
        answer = self.utils.rr_process(text)
        #print newText in the Gui
        self.ids['scrollid'].children[0].text = "Watson: " + answer
        #play the audio if it exists
        self.utils.play_wav('output.wav')

    #Read in the user input and feed to R&R if Watson
    #is mentioned, otherwise feed to the NLC
    def user_input(self, text):
        text = text.lower()
        if self.utils.isWatsonQuery(text):
            self.rr_process(self.utils.cleanse_rr_string(text))
        else:
            self.hostage_taker_query(text)
        self.ids['textInput'].text =  text

class hnsApp(App):
    def build(self):
        return hnsGame()
        
if __name__ == '__main__':
    hnsApp().run()
