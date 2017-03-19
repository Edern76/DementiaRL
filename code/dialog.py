import textwrap
import code.constants as const
from copy import copy
'''
HOW TO CREATE DIALOG FOR AN NPC :
    1) Create choices associated with a certain screen
    2) Create list containing these choices, even if there is only one choice.
    3) Create screen associated to these choices and pass the list you created earlier to it.
    4) Repeat 1, 2 and 3 until you have all the screens you want
    5) Create a list containing all of these screens
    6) Create a new dialog tree and pass the list of all its screens to it.
    7) Import said tree into main and associate it to the NPC of your choice
    
FOLLOWING THESE STEPS IN THE EXACT ORDER THEY ARE WRITTEN IN IS CRUCIAL. Stuff WILL break if you don't. 
It is highly advised to write down all the screens with their respective choices and text, and how they are linked together, before starting to implement them.

'''
def formatText(text, w):
    splittedText = text.splitlines()
    outputText = []

    for splitLine in splittedText:
        wrappedLine = textwrap.wrap(splitLine, width = w, drop_whitespace = True)
        for toPrint in wrappedLine:
            outputText.append(toPrint)
        outputText.append('BREAK')
    
    return outputText

class DialogTree:
    def __init__(self, screenList, name, origScreen):
        self.screenList = screenList
        self.name = name
        self.origScreen = origScreen
        self.currentScreen = origScreen
        
        for screen in self.screenList:
            screen.parentTree = self
        
dummyTree = DialogTree([], 'Dummy / DO NOT USE', None)
        
class DialogScreen:
    def __init__(self, idT,  dialogText, choicesList, prevScreen = None):
        '''
        idT stands for 'idText', becuase 'id' was reserved to a Python built-in symbol.
        ''' 
        self.dialogText = formatText(dialogText, const.DIAL_TEXT_WIDTH)
        self.idT = idT
        self.choicesList = choicesList
        self.parentTree = dummyTree
        self.prevScreen = prevScreen
        
        for choice in self.choicesList:
            choice.parentScreen = self

dummyScreen = DialogScreen('dummy', 'This is only a dummy screen so as choices can temporarily attach to it. Please do not use it', [])
       
class DialogChoice:
    def __init__(self, idT, text):
        self.idT = idT
        self.text = text #Please make sure this text is on a single line
        self.parentScreen = dummyScreen
        
    def select(self):
        rootTree = self.parentScreen.parentTree
        if self.idT == 'INTRO':
            rootTree.currentScreen = copy(rootTree.origScreen)
            return 'OK'
        elif self.idT == 'BACK':
            if self.parentScreen.prevScreen is not None:
                rootTree.currentScreen = copy(self.parentScreen.prevScreen)
                return 'OK'
            else:
                raise AttributeError('No previous screen found')
        elif self.idT == 'END':
            return 'END'
        elif self.idT == 'SHOP':
            return 'SHOP'
        
        else:
            for screen in rootTree.screenList:
                if screen.idT == self.idT:
                    rootTree.currentScreen = copy(screen)
                    return 'OK'
                else:
                    continue
            raise AttributeError("Couldn't find screen with ID {} in the {} screens of {}'s dialog tree".format(self.idT, len(rootTree.screenList), rootTree.name))
            
         
######################PUKIL THE DEBUGGER#########################
'''
@race : Human
@gender : Male
@age : Old/Very old
@profession : Former 'debugger'
'''


#######Intro Screen########
pukIntText = "'It is a rare event to encounter a new face around here, and a even rarer one to find a new face which doesn't belongs to something which wants nothing but your death. \n I am Pukil the Debugger, but you can call me Pukil if you want. Make yourself at home here, but please tell me if you see any bug'"
pukIntId = 'intro'

pukIntCh1 = DialogChoice(idT = 'stairs', text = 'What do you think about stairs ?')
pukIntCh2 = DialogChoice(idT = 'debug', text = "Why is your nickname the 'debugger' ?")
pukIntCh3 = DialogChoice(idT = 'END', text = "Farewell.")

pukIntClist = [pukIntCh1, pukIntCh2, pukIntCh3]

pukIntScr = DialogScreen(idT = pukIntId, dialogText = pukIntText, choicesList= pukIntClist)
############################

########'Stairs' Screen ########
pukStrText = "'No... No.... Not again.... NOT AGAIN !' \n *He seems to have lost all bounds with the reality as he repeats the same words over and over. It would be better to leave him alone for now.*"
pukStrId = 'stairs'

pukStrCh = DialogChoice(idT = 'END', text = '(End conversation)')
pukStrClist = [pukStrCh]

pukStrScr = DialogScreen(idT = pukStrId, dialogText = pukStrText, choicesList=pukStrClist, prevScreen= pukIntScr)
################################

########'Debug' Screen ########
pukDbgText = "'I hate bugs more than anything in this world. So, I used to walk down the everchanging corridors of this darned place, and to splat any bugs that entered my vision, ignoring the other abominations which roam this site.'"
pukDbgId = 'debug'

pukDbgCh1 = DialogChoice(idT = 'bugs', text = "It seemed you were quite effective, since I didn't see any bug around there.")
pukDbgCh2 = DialogChoice(idT = 'dangerous', text = "Why did you ignore the monsters around you ? They are way more dangerous than mere insects.")
pukDbgCh3 = DialogChoice(idT = 'stop', text = "You used to ? Why did you stopped ?")
pukDbgCh4 = DialogChoice(idT = 'BACK', text = '(Back)')

pukDbgClist = [pukDbgCh1, pukDbgCh2, pukDbgCh3, pukDbgCh4]
pukDbgScr = DialogScreen(idT = pukDbgId, dialogText = pukDbgText, choicesList = pukDbgClist, prevScreen= pukIntScr)

###############################

########'Bugs' Screen########
pukBugText = "'It's not because you haven't seen them that they're not here. They're everywhere, all around us, and they will always be.'"
pukBugId = 'bugs'

pukBugCh = DialogChoice(idT = 'BACK', text = 'Sure...')

pukBugClist = [pukBugCh]
pukBugScr = DialogScreen(idT = pukBugId, dialogText = pukBugText, choicesList = pukBugClist, prevScreen= pukDbgScr)
#############################

########'Dangerous' Screen########
pukDgrText = "'That's where you're wrong. Bugs are way more powerful than any monster you'll encounter, and they can't be killed by swords or magic. They are the ones you should be afraid of.'"
pukDgrId = 'dangerous'

pukDgrCh = DialogChoice(idT = 'BACK', text = '(Back)')

pukDgrClist = [pukDgrCh]
pukDgrScr = DialogScreen(idT = pukDgrId, dialogText = pukDgrText, choicesList = pukDgrClist, prevScreen= pukDbgScr)
##################################

########'Stop' Screen########
pukStpText = "'Because I have grown old, in case you couldn't tell. Age made me too weak for such a task, it was time for me to get replaced by people more competent than I am.'"
pukStpId = 'stop'

pukStpCh = DialogChoice(idT = 'BACK', text = '(Back)')

pukStpClist = [pukStpCh]
pukStpScr = DialogScreen(idT = pukStpId, dialogText = pukStpText, choicesList = pukStpClist, prevScreen= pukDbgScr)
#############################

pukScrList = [pukIntScr, pukStrScr, pukDbgScr, pukBugScr, pukDgrScr, pukStpScr]

pukTree = DialogTree(screenList= pukScrList, name = 'Pukil', origScreen= pukScrList[0])


######################AYETH THE INSECTOID MERCHANT#########################
'''
@race : Insectoid
@gender : Female
@age : Child
@profession : Merchant

TO-DO : Add more dialog than jusy the 'enter shop' option     
'''

ayeIntText = 'Greetings adventurer ! Would you buy me a little something ? I make the best pies of all [INSERT WORLD NAME HERE] !'
ayeIntId = 'intro'
ayeIntCh1 = DialogChoice(idT= 'SHOP', text = 'Sure, let me take a look at your wares. (Enter shop)')
ayeIntCh2 = DialogChoice(idT = 'END', text = "I'm busy right now, maybe at a later time ? (End conversation)")

ayeIntClist = [ayeIntCh1, ayeIntCh2]
ayeIntScr = DialogScreen(idT= 'intro', dialogText= ayeIntText, choicesList = ayeIntClist)

ayeScrList = [ayeIntScr]
ayeTree = DialogTree(screenList = ayeScrList, name = 'Ayeth', origScreen= ayeScrList[0])
