from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.graphics import *
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import *
import json, sys, re
from watson_developer_cloud import RetrieveAndRankV1

retrieve_and_rank = RetrieveAndRankV1(
    username='6cb8a2a2-01fc-4bad-ae24-b741082df113',
    password='cxSIPwhVnZft')
solr_cluster_id = 'scff9b5a52_0a69_4a59_8e98_85c2184af3c5'
#status = retrieve_and_rank.get_solr_cluster_status(
    #solr_cluster_id=solr_cluster_id)
#print(json.dumps(status, indent=2))
configs = retrieve_and_rank.list_configs(solr_cluster_id=solr_cluster_id)
#print(json.dumps(configs, indent=2))

#regular expression identifier for text that goes to R&R
rr_text_id = "^\w*\s*watson[,.\-!]{0,1}\s+"

#This is the games main widget.
#TODO make another widget to float ontop as an ingame menu or add
# navigation tools somewhere in this widget
class hnsGame(Widget):
    def hostage_taker_query(self, text):
        self.ids['mainImage'].source = "hostage_1.jpg"
        self.ids['scrollidLeft'].children[0].text = "Hostage Taker: " + "Leave me alone!"


    #sends a request(text) to IBM's servers for R&R and
    #returns the response
    def watson(self, text):
        response = ''
        if len(configs['solr_configs']) > 0:
            collections = retrieve_and_rank.list_collections(
                solr_cluster_id=solr_cluster_id)
            #print(json.dumps(collections, indent=2))

            pysolr_client = retrieve_and_rank.get_pysolr_client(solr_cluster_id,
                                                                collections[
                                                                    'collections'][0])
            results = pysolr_client.search(text)

            i = 0
            newText = ''
            #This catches an empty docset which would
            #otherwise throw errors
            try:
                response = results.docs[0]['body'][0]
            except IndexError:
                response = "I'm sorry, they don't teach that at the academy"
        #Error catch for improper solr setup
        else:
            print("Error: Solr misconfigured. Configs couldn't be read.")
            sys.exit(1)
        return response

    def rr_process(self, text):
        self.ids['mainImage'].source = "watson_avatar.jpg"
        answer = self.watson(text)
        #print newText in the Gui
        self.ids['scrollid'].children[0].text = "Watson: " + answer

    #Read in the user input and feed to R&R if Watson
    #is mentioned, otherwise feed to the NLC
    def user_input(self, text):
        text = text.lower()
        if self.isWatsonQuery(text):
            self.rr_process(re.sub(rr_text_id,'',text, flags=re.IGNORECASE))
        else:
            self.hostage_taker_query(text)
        self.ids['textInput'].text =  text

    def isWatsonQuery(self, text):
        if re.search(rr_text_id, text, re.IGNORECASE):
            return True
        else:
            return False



class hnsApp(App):
    def build(self):
        return hnsGame()
        
if __name__ == '__main__':
    hnsApp().run()
