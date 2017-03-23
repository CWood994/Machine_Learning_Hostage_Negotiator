from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.graphics import *
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import *
from kivy.uix.screenmanager import ScreenManager, Screen
import json, sys, re
from os.path import join, dirname
from subprocess import Popen
from sys import platform
from kivy.uix.boxlayout import *
from kivy.uix.button import *
from kivy.app import App
from kivy.lang import Builder

from game_utils import utils
from game_state import game_state

#This is the games main widget.
#TODO make another widget to float ontop as an ingame menu or add
# navigation tools somewhere in this widget

Builder.load_string("""
<GameScreen>: 
	BoxLayout:
		orientation: 'vertical'
		canvas:
		Image:
			id: mainImage
			pos: 0, self.height + 60
			height: root.height/2 - 30
			width: root.width
			source: 'hostage_1.jpg'

		ScrollView:
			id: scrollid
			left: root.width / 2 
			right: root.width 
			height: (root.height / 4) * 2
			width: root.width / 2 
			center_x: root.width * 3 / 4
			center_y: root.height / 4 + 30
			Label:
				id: wattext
				height: self.texture_size[1]
				size_hint_y: None
				valign: 'top'
				padding: 5, 5
				text_size: self.width, None
				text: "Watson: "

		ScrollView:
			id: scrollidLeft
			left: 0
			right: root.width/2 
			height: (root.height / 4) * 2
			width: root.width / 2 
			center_x: root.width / 4
			center_y: root.height / 4 + 30
			Label:
				id: wattext
				height: self.texture_size[1]
				size_hint_y: None
				valign: 'top'
				padding: 5, 5
				text_size: self.width, None
				text: "Hostage Taker: "
			
		
		TextInput:
			id: textInput
			text: 'Enter your query here'
			bottom: 0
			width: root.width
			scroll_x: 0
			height: 30
			multiline: False
			on_focus: True
			on_text_validate: root.user_input(self.text)
			use_bubble: True
        
<MenuScreen>:
    BoxLayout:
		orientation: 'vertical'
        Button:
            text: 'Goto game'
            on_press: root.manager.current = 'game'
        Button:
            text: 'Quit'
            on_press: root.quit()
        Button:
			text: 'Settings'
			



""")
class GameScreen(Screen):

    def __init__(self):
        super(GameScreen, self).__init__()
        self.game_state = game_state("nlc.json", "response.json")
        start_text = self.game_state.start() #TODO: implement start intro thing
        self.utils = utils()
        self.name = 'game'

    def hostage_taker_query(self, text):
        NLC_class = self.utils.nlc_classify_top_result(text)
        self.ids['mainImage'].source = "hostage_1.jpg"
        response = self.game_state.move_state(NLC_class, text)
        self.utils.hostageTakerVoice(response)
        self.ids['scrollidLeft'].children[0].text = "Hostage Taker: " + response

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
        if self.game_state.isTerminal == True:
            print "gameEnded"
            
	def quit(self):
		 sys.exit(0)
            
		
class MenuScreen(Screen):
	pass
	
	
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(GameScreen())

class hnsApp(App):
    def build(self):
		return sm
        

hnsApp().run()
