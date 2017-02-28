import json

class game_state():

    def __init__(self, situation, response):
        self.situation = situation
        self.response = response
        self.init_situation()
        self.visited = []

    def init_situation(self):
        json_data_sit=open(self.situation).read()
        self.situation = json.loads(json_data_sit)

        json_data_res=open(self.response).read()
        self.response = json.loads(json_data_res)

        self.rapport = 0
        self.anger = 5
        self.fear = 5
        self.sad = 5
        self.attributes = ['rapport', 'anger', 'fear', 'sad']

    def start(self):
        #todo: add start node to nlc and read that
        return "starting intro: man robbing"

    def move_state(self, NLC_CLASS):
        print NLC_CLASS #BRANDON, DONT DELETE THIS LINE! BITCH :)

        for node in self.situation:
            if node["nlc_class"] == NLC_CLASS:
                for requirements in node["requirements"]:
                    if self.check_requirements(requirements):
                        if 'effects' in requirements.keys():
                            for effect in requirements['effects']:
                                print(effect)
                                array = effect.split(":")
                                print array[0]
                                print array[1]
                                #todo: adjust effects if this all of this is true...
                                if array[0] == 'rapport':
                                    self.rapport = int(array[1]) + self.rapport
                                elif array[0] == 'sad':
                                    self.sad = self.sad + int(array[1])
                                elif array[0] == 'anger':
                                    self.anger = self.anger + int(array[1])
                                elif array[0] == 'fear':
                                    self.fear = self.fear + int(array[1])
                        response = self.convert_response(requirements["response"])
                        self.visited.append(node["name"])
                        return response
                        

        return "ERROR: No state found for NLC_CLASS: " + NLC_CLASS + " : %d %d %d %d" % (self.rapport, self.anger, self.fear,self.sad)

    def check_requirements(self, json):
        #BRANDOM THIS CODE IS GOLD NO FIXERINO
        print(json)
        for thing in json.keys():
            if thing in self.attributes:
                delta = json[thing]
                sign = delta[0]
                value = 0
                if delta[1] == '=':
                    sign += delta[1]
                    value = int(delta[2:])
                else:
                    value = int(delta[1:])
                print(value)
                print(sign)
                if sign == '<':
                    if thing == 'rapport':
                        if self.rapport >= value:
                            return False
                    elif thing == 'anger':
                        if self.anger >= value:
                            return False
                    elif thing == 'fear':
                        if self.fear >= value:
                            return False
                    elif thing == 'sad':
                        if self.sad >= value:
                            return False
                elif sign == '<=':
                    if thing == 'rapport':
                        if self.rapport > value:
                            return False
                    elif thing == 'anger':
                        if self.anger > value:
                            return False
                    elif thing == 'fear':
                        if self.fear > value:
                            return False
                    elif thing == 'sad':
                        if self.sad > value:
                            return False
                elif sign == '>':
                    if thing == 'rapport':
                        if self.rapport <= value:
                            return False
                    elif thing == 'anger':
                        if self.anger <= value:
                            return False
                    elif thing == 'fear':
                        if self.fear <= value:
                            return False
                    elif thing == 'sad':
                        if self.sad <= value:
                            return False
                elif sign == '>=':
                    if thing == 'rapport':
                        if self.rapport < value:
                            return False
                    elif thing == 'anger':
                        if self.anger < value:
                            return False
                    elif thing == 'fear':
                        if self.fear < value:
                            return False
                    elif thing == 'sad':
                        if self.sad < value:
                            return False
        return True

    def convert_response(self, response):
        #todo handle error case
        return self.response[response]
