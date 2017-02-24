import json, sys, re, os

from watson_developer_cloud import RetrieveAndRankV1
from watson_developer_cloud import NaturalLanguageClassifierV1
from os.path import join, dirname
from watson_developer_cloud import TextToSpeechV1
from subprocess import Popen
from sys import platform

class utils():

    def __init__(self):
        self.init_services()
        #regular expression identifier for text that goes to R&R
        self.rr_text_id = "^\w*\s*watson[,.\-!]{0,1}\s+"

    #Get rid of the rr_text_id regular expression
    def cleanse_rr_string(self, text):
        return re.sub(self.rr_text_id,'',text, flags=re.IGNORECASE)

    #Necessary to initialize FIXME usernames and passwords should be
    #read from an outside file and not hardcoded
    def init_services(self):
        self.text_to_speech = TextToSpeechV1(
            username='f112c56c-35ec-4728-b1ca-fe29fcd36f58',
            password='vijGcGcSV2KX',
            x_watson_learning_opt_out=True)  # Optional flag

        self.retrieve_and_rank = RetrieveAndRankV1(
            username='6cb8a2a2-01fc-4bad-ae24-b741082df113',
            password='cxSIPwhVnZft')
        self.solr_cluster_id = 'scff9b5a52_0a69_4a59_8e98_85c2184af3c5'

        self.natural_language_classifier = NaturalLanguageClassifierV1(
            username='9215e28a-3cff-4d3b-ad99-44d35e641876',
            password='6CXwnXGbblMh')

        self.configs = self.retrieve_and_rank.list_configs(solr_cluster_id=self.solr_cluster_id)

    def nlc_classify(self, text):
        classes = self.natural_language_classifier.classify('f5bbc5x176-nlc-3978', text)
        return classes

    def nlc_classify_top_result(self, text):
        return self.nlc_classify(text)['classes'][0]['class_name']

    #Takes some text destined for rr, gets the first result with rr_query_
    #first_result and then uses text to speech to write a wav file with the
    #response text
    def rr_process(self, text):
        answer = self.rr_query_first_result(text)
        #print newText in the Gui

        try:
            with open(join(dirname(__file__), 'output.wav'), 'wrb') as audio_file:
                output = self.text_to_speech.synthesize(answer, accept='audio/wav', voice="en-US_MichaelVoice")
                audio_file.write(output)
        #Ignore audio problems if they exist instead of
        #interrupting the user
        except:
            pass
        return answer

    #Play an audio file
    def play_wav(self, filename):
        try:
            with open(join(dirname(__file__), filename), 'rb') as audio_file:
                if platform == "linux" or platform == "linux2" or platform == "darwin":
                    Popen(["play", 'output.wav'])
                elif platform == "win32":
                    Popen(["sox", 'output.wav', '-t', 'waveaudio'], shell = True)
        except:
            pass

    #Read in the user input and feed to R&R if Watson
    #is mentioned, otherwise feed to the NLC
    def user_input(self, text):
        text = text.lower()
        if self.isWatsonQuery(text):
            self.rr_process(re.sub(self.rr_text_id,'',text, flags=re.IGNORECASE))
        else:
            self.hostage_taker_query(text)

    #Check if the input should go to RR based on the regular expression
    #rr_text_id
    def isWatsonQuery(self, text):
        if re.search(self.rr_text_id, text, re.IGNORECASE):
            return True
        else:
            return False

    #Actually sends the rr query(text) to Watson and returns the result set
    def rr_query(self, text):
        results = ''
        if len(self.configs['solr_configs']) > 0:
            collections = self.retrieve_and_rank.list_collections(
                solr_cluster_id=self.solr_cluster_id)

            pysolr_client = self.retrieve_and_rank.get_pysolr_client(self.solr_cluster_id,
                                                                collections[
                                                                    'collections'][0])
            results = pysolr_client.search(text)
        #Error catch for improper solr setup
        else:
            print("Error: Solr misconfigured. Configs couldn't be read.")
            sys.exit(1)
        return results

    #runs rr_query and returns the first response body or a fallback result if empty
    def rr_query_first_result(self, text):
        response = ''
        results = self.rr_query(text)

        i = 0
        newText = ''

        #This catches an empty docset which would
        #otherwise throw errors
        try:
            response = results.docs[0]['body'][0]
        except IndexError:
            response = "I'm sorry, they don't teach that at the academy"
        return response
