from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.graphics import *
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import *

class hnsGame(Widget):
	def watson_query(self, text):
		print(text)
		print(self.ids['scrollid'].children[0].text)
		self.ids['scrollid'].children[0].text = text
	pass

class hnsApp(App):
	def build(self):
		return hnsGame()
		
if __name__ == '__main__':
    hnsApp().run()
