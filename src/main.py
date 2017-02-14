from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.graphics import *
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import *
import json
from watson_developer_cloud import RetrieveAndRankV1
from os.path import join, dirname
from watson_developer_cloud import TextToSpeechV1
from subprocess import Popen


text_to_speech = TextToSpeechV1(
    username='f112c56c-35ec-4728-b1ca-fe29fcd36f58',
    password='vijGcGcSV2KX',
    x_watson_learning_opt_out=True)  # Optional flag

print(json.dumps(text_to_speech.voices(), indent=2))

retrieve_and_rank = RetrieveAndRankV1(
    username='6cb8a2a2-01fc-4bad-ae24-b741082df113',
    password='cxSIPwhVnZft')
solr_cluster_id = 'scff9b5a52_0a69_4a59_8e98_85c2184af3c5'
#status = retrieve_and_rank.get_solr_cluster_status(
    #solr_cluster_id=solr_cluster_id)
#print(json.dumps(status, indent=2))
configs = retrieve_and_rank.list_configs(solr_cluster_id=solr_cluster_id)
#print(json.dumps(configs, indent=2))

class hnsGame(Widget):
    def hostage_taker_query(self, text):
        self.ids['mainImage'].source = "hostage_1.jpg"
        self.ids['scrollidLeft'].children[0].text = "Hostage Taker: " + "Leave me alone!"

    def watson_query(self, text):
        self.ids['mainImage'].source = "watson_avatar.jpg"
        text = text.split('watson')[1]
        if len(configs['solr_configs']) > 0:
            collections = retrieve_and_rank.list_collections(
                solr_cluster_id=solr_cluster_id)
            #print(json.dumps(collections, indent=2))

            pysolr_client = retrieve_and_rank.get_pysolr_client(solr_cluster_id,
                                                                collections[
                                                                    'collections'][0])
            results = pysolr_client.search(text)
            #print('{0} documents found'.format(len(results.docs)))

            i = 0
            newText = ''
            answer = ''
            for test in results:
                if i == 0:
                    answer = test['body'][0]
                newText += str(i) + ': ' + test['body'][0] + '\n'
                i += 1
        #print newText
        with open(join(dirname(__file__), 'output.wav'),
          'wb') as audio_file:
            audio_file.write(text_to_speech.synthesize(answer, accept='audio/wav',
                                  voice="en-US_MichaelVoice"))
        self.ids['scrollid'].children[0].text = "Watson: " + answer
        Popen(["play", 'output.wav'])

    def user_input(self, text):
        text = text.lower()
        if "watson" in text:
            self.watson_query(text)
        else:
            self.hostage_taker_query(text)
        self.ids['textInput'].text =  text


class hnsApp(App):
    def build(self):
        return hnsGame()
        
if __name__ == '__main__':
    hnsApp().run()
