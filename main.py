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

retrieve_and_rank = RetrieveAndRankV1(
    username='6cb8a2a2-01fc-4bad-ae24-b741082df113',
    password='cxSIPwhVnZft')
solr_cluster_id = 'scff9b5a52_0a69_4a59_8e98_85c2184af3c5'
status = retrieve_and_rank.get_solr_cluster_status(
    solr_cluster_id=solr_cluster_id)
print(json.dumps(status, indent=2))
configs = retrieve_and_rank.list_configs(solr_cluster_id=solr_cluster_id)
print(json.dumps(configs, indent=2))

class hnsGame(Widget):
	def watson_query(self, text):
		if len(configs['solr_configs']) > 0:
		    collections = retrieve_and_rank.list_collections(
		        solr_cluster_id=solr_cluster_id)
		    print(json.dumps(collections, indent=2))

		    pysolr_client = retrieve_and_rank.get_pysolr_client(solr_cluster_id,
		                                                        collections[
		                                                            'collections'][0])
		    results = pysolr_client.search('Managing Quid Pro Quo Effectively')
		    print('{0} documents found'.format(len(results.docs)))

		    i = 0
		    newText = ''
		    answer = ''
		    for test in results:
		    	if i == 0:
		    		answer = test['body'][0]
		        newText += str(i) + ': ' + test['body'][0] + '\n'
		        i += 1
		print newText
		self.ids['scrollid'].children[0].text = answer
	pass

class hnsApp(App):
	def build(self):
		return hnsGame()
		
if __name__ == '__main__':
    hnsApp().run()
