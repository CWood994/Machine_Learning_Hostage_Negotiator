import json
from watson_developer_cloud import NaturalLanguageClassifierV1

#setup nlc
natural_language_classifier = NaturalLanguageClassifierV1(
    username='d977a91e-8653-4432-ad9a-cb92f0a1c5aa',
    password='EGtyKkWV6Dsg')

#setup simulation json
json_data=open("jsonTest.json").read()
situation = json.loads(json_data)
 
#classifiers = natural_language_classifier.list()        
#print(json.dumps(classifiers, indent=2))   

# create a classifier
# with open('../resources/weather_data_train.csv', 'rb') as training_data:
#     print(json.dumps(natural_language_classifier.create(
# training_data=training_data, name='weather'), indent=2))
 
# replace 2374f9x68-nlc-2697 with your classifier id
#status = natural_language_classifier.status('2374f9x68-nlc-2697')
#print(json.dumps(status, indent=2))

#if status['status'] == 'Available':
    #simState = simState(situation)
    #simStart()
    
def simStart():

    print("initial prompt")
    
    #while simState.isEndState != true:
    
    print(simState.voiceText)
    
    #get input
    input_string = raw_input()
    outputCategory = get_response_category(input_string)
    
    simState.moveState(situation, outputCategory)
    
    #end while
    
    print("end Sim")
    
    
    
def get_response_category(input):
    
    classes = natural_language_classifier.classify('2374f9x68-nlc-2697', input_string)
    #print(json.dumps(classes, indent=2))
    preCateg = json.dumps(classes, indent=2)
    categories = json.loads(preCateg)
    
    #matching logic?
    category = categories["nlc"]["something"]["nlc_category"]

    return category

    

    
class simState: 

    def __init__(self, json):
        self.currentState = json["exampleSimStates"]["simStates"]["exSimState1"]
        self.voiceText = json["exampleSimStates"]["simStates"]["exSimState1"]["stateText"]
        self.isEndState = json["exampleSimStates"]["simStates"]["exSimState1"]["isEndState"]
        self.modifier1 = 0
        self.modifier2 = 0
        self.modifier3 = 0
        self.modifier4 = 0
        self.modifier5 = 0
    
    
    
    
    def moveState(self, json, cateResponse):
        nextState = json["exampleSimStates"]["simStates"][self.currentState]["relationships"][cateResponse]["gotoState"]
        self.modifier1 = json["exampleSimStates"]["simStates"][self.currentState]["relationships"][cateResponse]["modiferValues"][1]
        self.modifier2 = json["exampleSimStates"]["simStates"][self.currentState]["relationships"][cateResponse]["modiferValues"][2]
        self.modifier2 = json["exampleSimStates"]["simStates"][self.currentState]["relationships"][cateResponse]["modiferValues"][3]
        self.modifier2 = json["exampleSimStates"]["simStates"][self.currentState]["relationships"][cateResponse]["modiferValues"][4]
        self.modifier2 = json["exampleSimStates"]["simStates"][self.currentState]["relationships"][cateResponse]["modiferValues"][5]
        
        self.currentState = json["exampleSimStates"]["simStates"][nextState]
        self.voiceText = json["exampleSimStates"]["simStates"][nextState]["stateText"]

    
    
if True:#status['status'] == 'Available':
    simState = simState(situation)
    simStart()

        

    