from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.graphics import *
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import *
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
import json, sys, re
from os.path import join, dirname
from subprocess import Popen
from sys import platform
from kivy.uix.boxlayout import *
from kivy.uix.button import *
from kivy.app import App
from kivy.lang import Builder
import thread
import os
from random import randint
import time

from game_utils import utils
from game_state import game_state

#This is the games main widget.
#make another widget to float ontop as an ingame menu or add
# navigation tools somewhere in this widget

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

Builder.load_string("""
<ImageButton@Button>:
	source: None
	background_color: 1, 1, 1, 1
	on_press: root.on_press
	Image:
        source: root.source
		pos: root.pos
		size: root.size
        
<GameScreen>: 
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            canvas:
            Button:
                size_hint_x: 0.5
                text: 'Menu'
                on_press: root.manager.current = 'menu'
            Image:
                id: mainImage
                pos: 0, self.height + 60
                height: root.height/2 - 30
                size_hint_x: 1
                source: 'police_car.gif'
                anim_delay: 0.1
            Button:
                id: aabutton
                size_hint_x: 0.5
                text: 'Send In Swat'
                on_press: root.sendInSwat()

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
                text_size: self.width, None
                text: "Hostage Taker: "
            
        BoxLayout:
			orientation: 'horizontal'
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
			ImageButton:
                id: micpictureConnorHotdog
				allow_stretch: True
				keep_ratio: False
				size_hint_x: 0.3
				source: 'mic.png'
				on_press: root.stt()
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        Image:
            id: menuImage
            source: 'police_car.gif'
            allow_stretch: True
            anim_delay: 0.1
        Button:
            text: 'Start Game'
            on_press: root.startGame()
        BoxLayout:
			orientation: 'horizontal'
			Spinner:
				id: sceneselect
				size: root.height/3, root.width/4
				text: "Scenario Select"
				values: ""
				size_hint: None, None
			Button:
				text: "Learn to Play"
                size: root.height/3, root.width/4
				on_press: root.manager.current = 'help'
			Button:
				id: btnExit
                size: root.height/3, root.width/4
				text: "Exit"
				on_press: app.stop()
<AfterActionScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.25
            Button:
                text: 'Menu'
                on_press: root.manager.current = 'menu'
            Button: 
                text: 'Quit'
                on_press: app.stop()
        ScrollView:
            id: aascrollview
            left: 0
            Label:
                id: aatext
                height: self.texture_size[1]
                size_hint_y: None
                valign: 'top'
                padding: 5, 5
                text_size: self.width, None
                text: "After Action report: "
<HelpScreen>
	BoxLayout:
		orientation: 'vertical'
		Button:
			size_hint_y: 0.5
			text: 'Menu'
			on_press: root.manager.current = 'menu'
		Label:
			halign: 'left'
			padding: 10, 10
			text_size: root.width, None
			size: self.texture_size
			text: "Welcome to group 65b's hostage negotiator training simulator. Here are the basics you need to know in order to play the game."
		Label:
			halign: 'left'
			padding: 10, 10
			text_size: root.width, None
			size: self.texture_size
			text: "You have an assistant named Watson. In order to ask his advice, type into the bottom entry field any query you'd like prefaced with ~ watson ~. For example: Watson, what is rapport?"
		Label:
			halign: 'left'
			padding: 10, 10
			text_size: root.width, None
			size: self.texture_size
			text: "Responding to the hostage taker is as simple as typing into the bottom text box normally. You are under no time constraints for this, and can ask watson as many questions you like in between responses."
		Label:
			halign: 'left'
			padding: 10, 10
			text_size: root.width, None
			size: self.texture_size
			text: "In order to succeed at the scenarios, you must get the hostage taker into a mental state whereby you can arrest him without any danger to the hostages or surrounding police force. "
""")
class GameScreen(Screen):

    def __init__(self):
        super(GameScreen, self).__init__()
        global GS
        GS=self
        self.finishedGame = False
        self.name = 'game'
        self.NOSWAT = False
        global swat 
        swat = False
        self.spellchecked = False

    def changeGame(self, nlc, response):
        self.ids['scrollidLeft'].children[0].text = "Hostage Taker: "
        self.ids['mainImage'].source = "police_car.gif"
        self.utils = utils()
        self.game_state = game_state(nlc, response, self.utils)
        self.ids['scrollid'].children[0].text = "Watson: " + self.game_state.startText()
        self.utils.updateGameState( self.game_state)

    def hostage_taker_query(self, text):
        is_spelled_correctly = self.utils.spellcheck(text)
        if self.spellchecked == True:
            is_spelled_correctly = True
        print "was the text spelled right?: " + str(is_spelled_correctly)
        if not is_spelled_correctly:
            self.ids['mainImage'].source = "watson_avatar.jpg" #why no work?
            self.ids['scrollid'].children[0].text = "Watson: Check your response there, you wouldn't want to sound dumb speaking to the hostage taker would you?"
            self.utils.WatsonVoice("Check your response there, you wouldn't want to sound dumb speaking to the hostage taker would you?")
            self.ids['textInput'].background_color = 1, 0, 0, 1
            self.ids['textInput'].text = text
            self.spellchecked = True
        else:
            NLC_class = self.utils.nlc_classify_top_result(text)
            tones = self.utils.analyze_tone(text)
            self.game_state.anal_tones(tones)
            #self.ids['mainImage'].source = "hostage_1.jpg"
            response = self.game_state.move_state(NLC_class, text)
            self.utils.hostageTakerVoice(response)
            self.ids['scrollidLeft'].children[0].text = "Hostage Taker: " + response
            
            if self.spellchecked == True:
                self.spellchecked = False
                self.ids['textInput'].background_color = 1, 1, 1, 1
                self.ids['textInput'].text = ""

            
        if self.spellchecked == True:
            is_spelled_correctly = True
            #self.ids['textInput'].text = ""
            #self.ids['textInput'].background_color = 1, 1, 1, 1
            
        self.updateUI()

    def rr_process(self, text):
        print self.ids['mainImage'].source
        print self.ids['mainImage']
        print self.ids['mainImage'].source
        #self.ids['mainImage'].source = "watson_avatar.jpg"
        #is_spelled_correctly = self.utils.spellcheck(text)
        #print "was the text spelled right?: " + str(is_spelled_correctly)
        #if not is_spelled_correctly:
            #self.ids['scrollid'].children[0].text = "Watson: I don't quite follow you, could you repeat your question clearly?"
            #self.utils.WatsonVoice("I don't quite follow you, could you repeat your question clearly?")
        #else:
        answer = self.utils.rr_process(text)
        #print newText in the Gui
        self.ids['scrollid'].children[0].text = "Watson: " + answer
        #play the audio if it exists
        self.utils.play_wav('output.wav')
        self.updateUI()

    def updateUI(self):
        print self.game_state.isTerminal == True 
        print self.finishedGame == True
        if self.game_state.isTerminal == True or self.finishedGame == True:
            self.NOSWAT = True
            self.ids["aabutton"].text = "AARP"
            self.ids["textInput"].text = "Game Over! Proceed to AARP"
            self.ids["textInput"].on_focus = "False"

        
    def gameEnded(self):
        self.game_state.log.append("\n\nFinal Stats:\n    Anger: " + str(self.game_state.anger) + "\n    Sad: " + str(self.game_state.sad) + "\n    Fear: " + str(self.game_state.fear) + "\n    Rapport: " + str(self.game_state.rapport))
        self.finishedGame = True
        AARP.printStats(self.game_state.log)
        
    def stt(self):
        self.ids["micpictureConnorHotdog"].source = "mic2.png"
        thread.start_new_thread(self.utils.call_speech_to_text, (self,))

    def updateSTT(self, text):
        if self.ids["textInput"].text == 'Enter your query here':
            self.ids["textInput"].text = text
        else:
            self.ids["textInput"].text += " "+text

    def stt_processing(self, value):
        self.ids["micpictureConnorHotdog"].disabled = value
        self.ids["micpictureConnorHotdog"].source = "mic.png"

    def recording_picture(self, value):
        if value:
            self.ids["micpictureConnorHotdog"].source = "mic2.png"
        else:
            self.ids["micpictureConnorHotdog"].source = "mic.png"


    def block_stt_button(self, value):
        self.ids["micpictureConnorHotdog"].disabled = value

    def sendInSwat(self):
        if self.NOSWAT ==False:
            #between 0 and 30
            global swat
            swat = True
            if self.finishedGame == False:
                self.finishedGame = True
                base = 15
                base -= self.game_state.anger
                base -= self.game_state.sad
                base -= self.game_state.fear
                base += self.game_state.rapport

                print base

                number = randint(0,30)

                print number

                if number <= base:
                    status = "SURVIVE"
                else:
                    status = "DIE"


            self.game_state.log.append("YOU SENT IN SWAT!... All of the hostages: " + status)
        self.gameEnded()
    #Read in the user input and feed to R&R if Watson
    #is mentioned, otherwise feed to the NLC
    def user_input(self, text):
        self.ids['textInput'].background_color = 1, 1, 1, 1
        if self.game_state.isTerminal == False:
            #text = text.lower()
            if self.utils.isWatsonQuery(text):
                self.ids['mainImage'].source = "watson_avatar.jpg"
                clean = self.utils.cleanse_rr_string(text)
                thread.start_new_thread(self.rr_process, (clean,))
            else:
                self.ids['mainImage'].source = "hostage_1.jpg"
                thread.start_new_thread( self.hostage_taker_query, (text,))
            self.ids['textInput'].text =  ''
            if self.game_state.isTerminal == True:
                print "GAMEOVER"
                self.ids["aabutton"].text = "AARP"
                self.ids["textInput"].text = "Game Over! Proceed to AARP"
                self.ids["textInput"].on_focus = "False"
                self.gameEnded()
        else:
            if self.finishedGame == False:
                self.gameEnded()
            self.ids["aabutton"].text = "AARP"
            self.ids["textInput"].text = "Game Over! Proceed to AARP"
            self.ids["textInput"].on_focus = "False"

               
class MenuScreen(Screen):

    def __init__(self, name):
        super(MenuScreen, self).__init__()
        self.name = name
        scenarioDir =  os.listdir("json/")
        for i in scenarioDir:
            if i[0] == ".":
                scenarioDir.remove(i)

        self.ids["sceneselect"].values = scenarioDir

    def startGame(self):
        if self.ids["sceneselect"].text != "Scenario Select":
            scenarioDir =  os.listdir("json/"+self.ids["sceneselect"].text)
            scenarioDir.remove("nlc.json")
            GS.changeGame("json/"+self.ids["sceneselect"].text+"/nlc.json", "json/"+self.ids["sceneselect"].text+"/"+scenarioDir[(randint(0,len(scenarioDir)-1))])
            sm.current = 'game'
            thread.start_new_thread(GS.game_state.start,())
    
class CustomDropDown(DropDown):
    pass
    
class AfterActionScreen(Screen):
    
    def __init__(self, name):
        super(AfterActionScreen, self).__init__()
        self.name = name
        global AARP
        AARP=self #Yikes! Brandon shut the fuck up.

    def printStats(self, text):

        stringToShow =""
        for s in text:
            print s
            stringToShow += s +"\n"

        thread.start_new_thread(self.updateText,(stringToShow,))
        

    def updateText(self, text):
        sm.current = 'afteraction'
        if swat == True:
            time.sleep(.5)

            if platform == "linux" or platform == "linux2" or platform == "darwin":
                Popen(["play", 'gun.wav'])
            elif platform == "win32":
                Popen(["sox", 'gun.wav', '-t', 'waveaudio'], shell = True)

            time.sleep(2)

        self.ids["aascrollview"].children[0].text = text

    
class HelpScreen(Screen):
    pass
    
dropdown = CustomDropDown()
mainbutton = Button(text='Hello', size_hint=(None, None))
mainbutton.bind(on_release=dropdown.open)
dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
    
    
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(GameScreen())
sm.add_widget(HelpScreen(name='help'))
sm.add_widget(AfterActionScreen(name='afteraction'))

class hnsApp(App):
    def build(self):
        return sm
        

hnsApp().run()
