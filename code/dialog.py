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

creditText = "Created by Erwan CASTIONI and Gawein LE GOFF. \n \n Using a modified version of the TDL module by Kyle Stewart and a modified version of the XpLoader module by Sean Hagar \n This software uses libraries from the FFmpeg project under the LGPLv2.1 \n Made with Python 3. \n \n Music from Jukedeck - create your own at http://jukedeck.com \n \n Special thanks to Francesco V. who launched the game once."

prologueScr1 = "The story you're about to witness takes place in Ashotara, a world filled with deadly monstruosities and dangerous beasts, a world constantly riven by conflicts betsween kingdoms, a world where chaos governs the very life of each of its inhabitants. \n \n \n \n And still, this world has yet to know the greatest peril it has ever experienced. \n"
prologueScr2 = "Zarg was revered as one of the most powerful mages of Ashotara. He always put his powers at the service of the greater good, and despite having been promised countless times fortunes by the rulers of the many kingdoms of Ashotara for doing so, he never picked a side in any of the many armed conflicts driven by greed, hatred or envy. \n However, despite his tremendous powers, Zarg was still a human. And as all humans, his mind was susceptible to temptation. Indeed, he was constantly obsessed with finding ways to increase his magical abilities, so as to be able to protect the defenseless from any opponent, no matter how strong or numerous they could be. Though his motives were noble, little did he know that such lust for might would lead him to walk the path of his former foes. \n \n \n Therefore, when he learnt about the existence of the Cube of Dohrr'Ien, a mysterious artifact from another dimension, enclosing unmatched amounts of pure energy so prodigious that they could turn a mere mortal into a god, he immediately set out on a journey through the tallest mountains and the deepest seas, through the greatest perils and the direst ordeals, to go where no man ever had the courage to go in order to retrieve the Cube."
prologueScr3 = "Finally, he reached the colossal spire erected by otherworldly forces, in which the Cube was emprisoned. The said edifice was heavily guarded by undescriptible abominations, which revealed themselves to be a formidable threat, even for Zarg. \n \n \n Yet, battle after battle, he kept on progressing little by little, until he finally managed to reach the very top of the tower, where the Cube was waiting for him."
prologueScr4 = "But the inner workings of the Cube were beyond the reach of any mortal from Ashotara, no matter how powerful they might be. \n \n \n Zarg was no exception, and thus when after countless tries he finally managed to break the seal which kept the energy inside the Cube, he did indeed ascend to godhood, but acccomplishing this feat that no mortal had achieved before cost him his sanity. \n From now on, Zarg, previously known as the Magical Guardian, would be called the God of Madness."
prologueScr5 = "He used his newfound divine abilites to torment the inhabitants of Ashotara from the Dohrr'Ien Spire, which he had made his lair. \n \n \n Worried by the amplitude of the destruction he inflicted in so little time, rulers of the kingdoms of Ashotara agreed to temporarily set aside their discords and form a temporary Alliance to find out a way to stop the God of Madness from causing even more damage."
prologueScr6 = "Gigantic armies were sent to assault the Spire, but were dispatched one after one by Zarg and his minions without any effort. \n \n \n After having suffered such overwhelming defeats, the Alliance understood pure strength and sheer numbers could not defeat Zarg, and decided to resort to cunning instead."
prologueScr7 = "A small party of accomplished adventurers was sent to infiltrate the Spire and find a way to deal with Zarg once and for all. Though they didn't manage to kill him, they found out the God's weakness : if the Cube of Dohrr'Ien were to be destroyed, Zarg's divine powers would vanish. They also unveiled his intentions : to destroy all sapient life in Ashotara. \n \n \n Having been upset by these uninvited guests, Zarg built a magical barrier around his lair, and with the help of a spell, he addressed himself to the entirety of Ashotara in those terms :"
prologueScr8 = '"I have grown tired of being disturbed by you weaklings, and I have become bored because none of those who dared to irk me in my own home were able to put up a decent fight. \n \n \n Therefore, I hereby order you to send me your strongest warrior. They will be the only one able to cross the barrier I created around my domain."'
prologueScr9 = "The alliance deemed that the strongest warrior of Ashotara was a human paladin : a combatant fighting using both conventional weapons and magic. \n \n \n This hero is this world's last hope. As Zarg is waiting for his opponent, the hero finishes preparing himself for the battle that will decide the fate of Ashotara. He knows he has no right to error."

prologueScreens = [prologueScr1, prologueScr2, prologueScr3, prologueScr4, prologueScr5, prologueScr6, prologueScr7, prologueScr8, prologueScr9]
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

TO-DO : Add more dialog than just the 'enter shop' option     
'''

ayeIntText = 'Greetings adventurer ! Would you buy me a little something ? I make the best pies of all [INSERT WORLD NAME HERE] !'
ayeIntId = 'intro'
ayeIntCh1 = DialogChoice(idT= 'SHOP', text = 'Sure, let me take a look at your wares. (Enter shop)')
ayeIntCh2 = DialogChoice(idT = 'END', text = "I'm busy right now, maybe at a later time ? (End conversation)")

ayeIntClist = [ayeIntCh1, ayeIntCh2]
ayeIntScr = DialogScreen(idT= 'intro', dialogText= ayeIntText, choicesList = ayeIntClist)

ayeScrList = [ayeIntScr]
ayeTree = DialogTree(screenList = ayeScrList, name = 'Ayeth', origScreen= ayeScrList[0])

######################TUTORIAL SOLDIERS#########################

####Soldier 1####

sld1IntText = "We're counting on you [HERO_NAME] !" #TO-DO: Make the chat function replace things in brackets by what they stand for.
sld1IntId = "intro"
sld1IntCh1 = DialogChoice(idT = 'END', text="Don't worry, I won't let you down. (End conversation)")

sld1IntClist = [sld1IntCh1]
sld1IntScr = DialogScreen(idT = 'intro', dialogText=sld1IntText, choicesList=sld1IntClist)

sld1ScrList = [sld1IntScr]
sld1Tree = DialogTree(screenList= sld1ScrList, name = "Soldier", origScreen = sld1ScrList[0])

####Soldier 2####

sld2IntText = "All of this is so infuriating, I'm sure we could beat this so called 'god' in the blink of an eye if it wasn't for this damned barrier... " #TO-DO: Make the chat function replace things in brackets by what they stand for.
sld2IntId = "intro"
sld2IntCh2 = DialogChoice(idT = 'END', text=" ... (End conversation)")

sld2IntClist = [sld2IntCh2]
sld2IntScr = DialogScreen(idT = 'intro', dialogText=sld2IntText, choicesList=sld2IntClist)

sld2ScrList = [sld2IntScr]
sld2Tree = DialogTree(screenList= sld2ScrList, name = "Soldier", origScreen = sld2ScrList[0])

