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

    def start(self):
        #todo: add start node to nlc and read that
        return "starting intro: man robbing"

    def move_state(self, NLC_CLASS):
        print NLC_CLASS #BRANDON, DONT DELETE THIS LINE! BITCH :)

        for node in self.situation:
            if node["nlc_class"] == NLC_CLASS:
                for requirements in node["requirements"]:
                    if self.check_requirements(requirements):
                        response = self.convert_response(requirements["response"])
                        self.visited.append(node["name"])
                        return response
                        

        return "ERROR: No state found for NLC_CLASS: " + NLC_CLASS + " : %d %d %d %d" % (self.rapport, self.anger, self.fear,self.sad)

    def check_requirements(self, json):
        for thing in json:
            if thing == "effects":
                for effect in json[thing]:
                    array = effect.split(":")
                    print array[0]
                    print array[1]
                    #todo: adjust effects if this all of this is true...
            if thing == "rapport":
                pass #todo all of this shit
            if thing == "sad":
                pass
            if thing == "anger":
                pass
            if thing == "fear":
                pass
            if thing == "nodes":
                # check if all in self.vistited
                pass

        return True

    def convert_response(self, response):
        #todo handle error case
        return self.response[response]