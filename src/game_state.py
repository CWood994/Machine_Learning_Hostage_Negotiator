import json
import thread
import time
from sys import platform
from subprocess import Popen




class game_state():

    def __init__(self, situation, response, utils):
        self.utils = utils
        self.situation = situation
        self.response = response
        self.init_situation()
        self.visited = []
        self.isTerminal = False
        self.log = []

    def init_situation(self):
        json_data_sit=open(self.situation).read()
        self.situation = json.loads(json_data_sit)

        json_data_res=open(self.response).read()
        self.response = json.loads(json_data_res)

        self.rapport = 1
        self.anger = 5
        self.fear = 5
        self.sad = 5
        self.attributes = ['rapport', 'anger', 'fear', 'sad']

    def anal_tones(self, tones):
        log_text = "\n"
        for tone in tones:
            print tone
            if tone[0] == "Fear" and tone[1] > .70:
                self.fear += 1
                log_text += "Your language shows Fear! \n"
            if tone[0] == "Anger" and tone[1] > .70:
                self.anger += 1
                self.sad += 1
                self.fear += 1
                log_text += "Your language shows Anger! \n"

            if tone[0] == "Sadness" and tone[1] > .70:
                self.sad += 1
                log_text += "Your language shows Sadness! \n"

        self.log.append(log_text)

    def start(self):
        #todo: add start node to nlc and read that
        print self.convert_response("START_SCENARIO")
        try:
            self.utils.rr_process("DO_NOT_USE", self.convert_response("START_SCENARIO"))
            self.utils.play_wav('output.wav')
        except:
            print "COULD NOT PLAY START SCENARIO, MAYBE START_SCENARIO NOT IN RESPONSE JSON"
    def startText(self):
        return self.convert_response("START_SCENARIO")


    def move_state(self, NLC_CLASS, text):
        print NLC_CLASS #BRANDON, DONT DELETE THIS LINE! BITCH :)

        for node in self.situation:
            if node["nlc_class"] == NLC_CLASS:
                for requirements in node["requirements"]:
                    if self.check_requirements(requirements):
                        log_text = text + " -> " + NLC_CLASS
                        if self.visited.count(requirements["name"]) < 2:
                            if 'effects' in requirements.keys():
                                for effect in requirements['effects']:
                                    print(effect)
                                    array = effect.split(":")
                                    #todo: adjust effects if this all of this is true...
                                    if array[0] == 'rapport':
                                        log_text += "\n    Rapport: " + str(self.rapport)  + " " + array[1] 
                                        self.rapport = int(array[1]) + self.rapport
                                    elif array[0] == 'sad':
                                        log_text += "\n    Sad: " + str(self.sad)  + " " + array[1] 
                                        self.sad = self.sad + int(array[1])
                                    elif array[0] == 'anger':
                                        log_text += "\n    Anger: " + str(self.anger)  + " " + array[1] 
                                        self.anger = self.anger + int(array[1])
                                    elif array[0] == 'fear':
                                        log_text += "\n    Fear: " + str(self.fear)  + " " + array[1] 
                                        self.fear = self.fear + int(array[1])
                        else:
                            log_text += "\n     PREVIOUSLY VISITED NODE X2"
                            log_text += "\n         Anger: " + str(self.anger)  + " +1"
                            log_text += "\n         Rapport: " + str(self.rapport)  + " -1"  
                            #self.rapport -= 1 #way too hard for the time being
                            self.anger += 1
                            self.rapport -= 1
                            if self.rapport <0 or self.sad > 9 or self.anger > 9 or self.fear > 9:
                                self.isTerminal = True
                            self.log.append(log_text)
                            return "I won't repeat myself! Pay attention!"
                        self.log.append(log_text)
                        if "terminal" in requirements:
                            self.log.append("\nHOSTAGES RELEASED!")
                            self.isTerminal = True
                        try:
                            response = self.convert_response(requirements["response"])
                        except:
                            temp = "ERROR: reponse not found for: " + requirements["response"]
                            print temp
                            self.log.append(text)
                            self.log.append(temp)
                            response = "You're giving me a headache!"
                        self.visited.append(requirements["name"])
                        if self.rapport <0 or self.sad > 9 or self.anger > 9 or self.fear > 9:
                            self.log.append("\nSTATS EXCEEDED MAX / MIN VALUE")
                            response += "\nEVERYONE IS DEAD NOW!"
                            self.isTerminal = True
                            thread.start_new_thread(self.playGun,())
                        return response

                        

        print "ERROR: No state found for NLC_CLASS: " + NLC_CLASS + " : %d %d %d %d" % (self.rapport, self.anger, self.fear,self.sad)
        return "Quit playing games with me!"

    def playGun(self):
        time.sleep(4)

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            Popen(["play", 'gun.wav'])
        elif platform == "win32":
            Popen(["sox", 'gun.wav', '-t', 'waveaudio'], shell = True)


    def check_requirements(self, json):
        for requirement in json.keys():
            if requirement in self.attributes:
                delta = json[requirement]
                sign = delta[0]
                value = 0
                if delta[1] == '=':
                    sign += delta[1]
                    value = int(delta[2:])
                else:
                    value = int(delta[1:])
                if sign == '<':
                    if getattr(self, requirement) >= value:
                        return False
                elif sign == '<=':
                    if getattr(self, requirement) > value:
                        return False
                elif sign == '>':
                    if getattr(self, requirement) <= value:
                        return False
                elif sign == '>=':
                    if getattr(self, requirement) < value:
                        return False
            if requirement == "nodes":
                for node in json[requirement]:
                    if node not in self.visited:
                        return False
        return True

    def convert_response(self, response):
        #todo handle error case
        return self.response[response]
