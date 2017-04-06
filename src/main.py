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


from game_utils import utils
from game_state import game_state

#This is the games main widget.
#TODO make another widget to float ontop as an ingame menu or add
# navigation tools somewhere in this widget

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

Builder.load_string("""
<GameScreen>: 
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            canvas:
            Button:
                size_hint_x: 0.5
                text: 'Goto menu'
                on_press: root.manager.current = 'menu'
            Image:
                id: mainImage
                pos: 0, self.height + 60
                height: root.height/2 - 30
                size_hint_x: 1
                source: 'police_car.gif'
            Button:
                id: aabutton
                size_hint_x: 0.5
                text: 'Send In Swat'
                on_press: root.manager.current = 'afteraction'
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
        Image:
            id: menuImage
            source: 'police_car.gif'
            allow_stretch: True
            anim_delay: 0.1
        Button:
            text: 'Goto game'
            on_press: root.startGame()
        BoxLayout:
			orientation: 'horizontal'
			Spinner:
				id: sceneselect
				size: root.height/4, root.width/4
				text: "Scenario Select"
				values: ""
				size_hint: None, None
			Button:
				text: "Learn to Play"
				on_press: root.manager.current = 'help'
			Button:
				id: btnExit
				text: "Exit"
				on_press: app.stop()
<AfterActionScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.25
            Button:
                text: 'Goto menu'
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
			text: 'Goto menu'
			on_press: root.manager.current = 'menu'
		Label:
			halign: 'left'
			padding: 10, 10
			text_size: root.width, None
			size: self.texture_size
			text: "Welcome to group 65b's hostage tranining simulator. Here are the basics you need to know in order to play the game."
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

    def changeGame(self, nlc, response):
        self.ids['scrollidLeft'].children[0].text = "Hostage Taker: "
        self.ids['scrollid'].children[0].text = "Watson: "
        self.ids['mainImage'].source = "police_car.gif"
        self.utils = utils()
        self.game_state = game_state(nlc, response, self.utils)
        self.utils.updateGameState( self.game_state)

    def hostage_taker_query(self, text):
        NLC_class = self.utils.nlc_classify_top_result(text)
        #self.ids['mainImage'].source = "hostage_1.jpg"
        response = self.game_state.move_state(NLC_class, text)
        self.utils.hostageTakerVoice(response)
        self.ids['scrollidLeft'].children[0].text = "Hostage Taker: " + response

    def rr_process(self, text):
        print self.ids['mainImage'].source
        print self.ids['mainImage']
        print self.ids['mainImage'].source
        #self.ids['mainImage'].source = "watson_avatar.jpg"
        answer = self.utils.rr_process(text)
        #print newText in the Gui
        self.ids['scrollid'].children[0].text = "Watson: " + answer
        #play the audio if it exists
        self.utils.play_wav('output.wav')
        
    def gameEnded(self):
        self.game_state.log.append("\n\nFinal Stats:\n    Anger: " + str(self.game_state.anger) + "\n    Sad: " + str(self.game_state.sad) + "\n    Fear: " + str(self.game_state.fear) + "\n    Rapport: " + str(self.game_state.rapport))
        self.finishedGame = True
        AARP.printStats(self.game_state.log)

    def sendInSwat(self):
        #between 0 and 30
        if self.finishedGame == False:
            self.finishedGame = True
            base = 15
            base -= self.game_state.anger
            base -= self.game_state.sad
            base -= self.game_state.fear
            base += self.game_state.rapport

            number = randint(0,30)

            if number <= base:
                status = "SURVIVE"
            else:
                status = "DIE"


            self.game_state.log.append("YOU SENT IN SWAT!... All of the hostages: " + status)
            self.gameEnded()
    #Read in the user input and feed to R&R if Watson
    #is mentioned, otherwise feed to the NLC
    def user_input(self, text):
        if self.game_state.isTerminal == False:
            text = text.lower()
            if self.utils.isWatsonQuery(text):
                self.ids['mainImage'].source = "watson_avatar.jpg"
                clean = self.utils.cleanse_rr_string(text)
                thread.start_new_thread(self.rr_process, (clean,))
                #self.rr_process(self.utils.cleanse_rr_string(text))
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

        self.ids["aascrollview"].children[0].text = stringToShow

    
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
