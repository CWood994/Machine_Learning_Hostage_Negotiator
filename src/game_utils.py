import json, sys, re, os

from watson_developer_cloud import RetrieveAndRankV1
from watson_developer_cloud import NaturalLanguageClassifierV1
from os.path import join, dirname
from watson_developer_cloud import TextToSpeechV1
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import SpeechToTextV1
from recording import Recorder
from subprocess import Popen
from sys import platform
import time
import thread


class utils():

    def __init__(self):
        self.init_services()
        self.gameState = None
        #regular expression identifier for text that goes to R&R
        self.rr_text_id = "^\w*\s*watson[,.\-!]{0,1}\s+"
        self.recorder = Recorder(channels=2)
        self.recording = False

    def updateGameState(self, gs):
        self.gameState = gs

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
            
        self.tone_analyzer = ToneAnalyzerV3(
            username='c983c6a5-d2c9-4574-a7d8-538c487e6054',
            password='mJDssOlQ6UzL',
            version='2016-02-11')
        
        self.speech_to_text = SpeechToTextV1(
            username='9ddc74aa-1494-40cd-8022-e13effed7635',
            password='brtLY1f2jmmy')

        self.configs = self.retrieve_and_rank.list_configs(solr_cluster_id=self.solr_cluster_id)

        self.speech_to_text.get_model('en-US_BroadbandModel')

    def nlc_classify(self, text):
        classes = self.natural_language_classifier.classify('90e7b4x199-nlc-5406', text)
        return classes

    def nlc_classify_top_result(self, text):
        return self.nlc_classify(text)['classes'][0]['class_name']
        
    def analyze_tone(self, text):
        preTones = json.dumps(self.tone_analyzer.tone(text=text), indent=2)
        tones = json.loads(preTones)
        scoreList = []
        for x in range(0,3):
            numTones = 5
            if x == 1:
                numTones = 3
            for y in range(0,numTones):
                scoreList.append([tones["document_tone"]["tone_categories"][x]["tones"][y]["tone_name"],tones["document_tone"]["tone_categories"][x]["tones"][y]['score']])
        return scoreList

    #Takes some text destined for rr, gets the first result with rr_query_
    #first_result and then uses text to speech to write a wav file with the
    #response text
    def rr_process(self, text, startTextHackSorry = ""):
        answer = self.rr_query_first_result(text)
        #print newText in the Gui
        if answer == "STATS":
            status = "an OKAY"
            if self.gameState.rapport < 5 or self.gameState.anger > 7 or self.gameState.sad > 7 or self.gameState.fear > 7:
                status = "a BAD"
            if self.gameState.rapport > 6 and self.gameState.anger < 6 and self.gameState.sad < 6 and self.gameState.fear < 6:
                status = "a GOOD" 
            answer = "According to facial analysis, the hostage taker currently is at:\n    Rapport: " + str(self.gameState.rapport) + "\n    Anger: " + str(self.gameState.anger) + "\n    Sad: " + str(self.gameState.sad) + "\n    Fear: " + str(self.gameState.fear) + "\n\nIt appears that you are doing " + status + " job!"
        if startTextHackSorry != "":
            answer = startTextHackSorry
        try:
            with open(join(dirname(__file__), 'output.wav'), 'wb') as audio_file:
                output = self.text_to_speech.synthesize(answer, accept='audio/wav', voice="en-GB_KateVoice")
                audio_file.write(output)
        #Ignore audio problems if they exist instead of
        #interrupting the user
        except:
            pass
        return answer

    def hostageTakerVoice(self, text):
        try:
            with open(join(dirname(__file__), 'output.wav'), 'wb') as audio_file:
                output = self.text_to_speech.synthesize(text, accept='audio/wav', voice="en-US_MichaelVoice")
                audio_file.write(output)

        #Ignore audio problems if they exist instead of
        #interrupting the user
        except:
            pass

        self.play_wav("output.wav")

    #Play an audio file
    #todo: this has output.wav hardcoded but takes a param filename...lol
    def play_wav(self, filename):
        try:
            with open(join(dirname(__file__), filename), 'rb') as audio_file:
                if platform == "linux" or platform == "linux2" or platform == "darwin":
                    Popen(["play", 'output.wav'])
                elif platform == "win32":
                    Popen(["sox", 'output.wav', '-t', 'waveaudio'], shell = True)
        except:
            #e = sys.exc_info()[0]
            #print "something went wrong " +  str(e)
            pass

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

    def call_speech_to_text(self):
        if not self.recording:
            self.recording = True
            self.record_audio()
            result = ""
            with open('input_audio.wav') as audio_file:
                result = self.speech_to_text.recognize(audio_file, content_type='audio/wav',timestamps=True,word_confidence=True)
            result = result['results'][0]['alternatives'][0]['transcript']
            return result
        else:
            self.recording = False
            return 0

    def record_audio(self):
        with self.recorder.open('input_audio.wav', 'wb') as recFile:
            recFile.start_recording()
            count = 0
            while self.recording:
                time.sleep(1)
                count += 1
                if count > 14:
                    self.recording = False
            recFile.stop_recording()
