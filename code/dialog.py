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

prologueScr1 = "The story you're about to witness takes place in Ashotara, a world filled with deadly monstrosities and dangerous beasts, a world constantly riven by conflicts between kingdoms, a world where chaos governs the very life of each of its inhabitants. \n \n \n \n And still, this world has yet to know the greatest peril it has ever experienced. \n"
prologueScr2 = "Zarg was revered as one of the most powerful mages of Ashotara. He always put his powers at the service of the greater good, and despite having been promised countless times fortunes by the rulers of the many kingdoms of Ashotara for doing so, he never picked a side in any of the many armed conflicts driven by greed, hatred or envy. \n However, despite his tremendous powers, Zarg was still a human. And as all humans, his mind was susceptible to temptation. Indeed, he was constantly obsessed with finding ways to increase his magical abilities, so as to be able to protect the defenseless from any opponent, no matter how strong or numerous they could be. Though his motives were noble, little did he know that such lust for might would lead him to walk the path of his former foes. \n \n \n Therefore, when he learnt about the existence of the Cube of Dohrr'Ien, a mysterious artifact from another dimension, enclosing unmatched amounts of pure energy so prodigious that they could turn a mere mortal into a god, he immediately set out on a journey through the tallest mountains and the deepest seas, through the greatest perils and the direst ordeals, to go where no man ever had the courage to go in order to retrieve the Cube."
prologueScr3 = "Finally, he reached the colossal spire erected by otherworldly forces, in which the Cube was emprisoned. The said edifice was heavily guarded by undescriptible abominations, which revealed themselves to be a formidable threat, even for Zarg. \n \n \n Yet, battle after battle, he kept on progressing little by little, until he finally managed to reach the very top of the tower, where the Cube was waiting for him."
prologueScr4 = "But the inner workings of the Cube were beyond the reach of any mortal from Ashotara, no matter how powerful they might be. \n \n \n Zarg was no exception, and thus when after countless tries he finally managed to break the seal which kept the energy inside the Cube, he did indeed ascend to godhood, but acccomplishing this feat that no mortal had achieved before cost him his sanity. \n From now on, Zarg, previously known as the Magical Guardian, would be called the God of Madness."
prologueScr5 = "He used his newfound divine abilites to torment the inhabitants of Ashotara from the Dohrr'Ien Spire, which he had made his lair. \n \n \n Worried by the amplitude of the destruction he inflicted in so little time, rulers of the kingdoms of Ashotara agreed to temporarily set aside their discords and form a temporary Alliance to find out a way to stop the God of Madness from causing even more damage."
prologueScr6 = "Gigantic armies were sent to assault the Spire, but were dispatched one after one by Zarg and his minions without any effort. \n \n \n After having suffered such overwhelming defeats, the Alliance understood pure strength and sheer numbers could not defeat Zarg, and decided to resort to cunning instead."
prologueScr7 = "A small party of accomplished adventurers was sent to infiltrate the Spire and find a way to deal with Zarg once and for all. Though they didn't manage to kill him, they found out the God's weakness : if the Cube of Dohrr'Ien were to be destroyed, Zarg's divine powers would vanish. They also unveiled his intentions : to destroy all sapient life in Ashotara. \n \n \n Having been upset by these uninvited guests, Zarg built a magical barrier around his lair, and with the help of a spell, he addressed himself to the entirety of Ashotara in those terms :"
prologueScr8 = '"I have grown tired of being disturbed by you weaklings, and I have become bored because none of those who dared to irk me in my own home were able to put up a decent fight. \n \n \n Therefore, I hereby order you to send me your strongest warrior. They will be the only one able to cross the barrier I created around my domain."'
prologueScr9 = "The alliance deemed that the strongest warrior of Ashotara was a human paladin : a combatant fighting using both conventional weapons and magic. \n \n \n This hero is this world's last hope. As Zarg is waiting for his opponent, the hero finishes preparing himself for the battle that will decide the fate of Ashotara. He knows he has no right to error."

prologueScreens = [prologueScr1, prologueScr2, prologueScr3, prologueScr4, prologueScr5, prologueScr6, prologueScr7, prologueScr8, prologueScr9]

'''
def doNothing():
    pass
'''
class DialogTree:
    def __init__(self, screenList, name, origScreen, character = None):
        self.screenList = screenList
        self.name = name
        self.origScreen = origScreen
        self.currentScreen = origScreen
        self.character = character
        
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
        self.onEnterFunctionName = "Erwan"
        
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

######################GENERAL GUILLEM#########################

guilIntText = "Greetings, [HERO_NAME]. This battle's outcome and along with it this world's future repose from now on solely on your shoulders. So please don't overlook anything in your preparations and tell me once you're ready."
guilIntId = "intro"

guilIntCh1 = DialogChoice(idT = 'ready', text = 'I am ready to take Zarg on. Please remind me the plan one last time.')
guilIntCh2 = DialogChoice(idT = 'happened', text = "What happened to the ones who snuck into Zarg's tower to unveil his plans ? Did they directly fought him ?")
guilIntCh3 = DialogChoice(idT = 'fought', text = 'I heard you fought a few times by the side of Zarg, before all of this started. What do you know about him ?')
guilIntCh4 = DialogChoice(idT = 'END', text = "I am not ready yet. I'll make my last preparations and come find you again once I'm done.")

guilIntClist = [guilIntCh1, guilIntCh2, guilIntCh3, guilIntCh4]
guilIntScr = DialogScreen(idT = guilIntId, dialogText = guilIntText, choicesList= guilIntClist)

########

guilRdyText = "Very well. You shall cross the barrier, get to the tower and climb until you find the Cube. Zarg will probably be there too, but your main objective is to destroy the Cube, since Zarg won't be able to carry on with his plan if he is deprived from his divine abilities."
guilRdyId = "ready"

guilRdyCh1 = DialogChoice(idT = "destroy", text = "Haven't you tried destroying the barrier to get the army through ?")
guilRdyCh2 = DialogChoice(idT = "fight", text = "What if I can't manage to destroy the Cube and have to fight Zarg while he still has his godly powers ?")
guilRdyCh3 = DialogChoice(idT = "zarg", text = "Once the cube is destroyed, what should I do with Zarg ?")
guilRdyCh4 = DialogChoice(idT = "understood", text = "Understood. Then I'll go to the armory to grab a weapon and then I'll be off.")

guilRdyClist = [guilRdyCh1, guilRdyCh2, guilRdyCh3, guilRdyCh4]
guilRdyScr = DialogScreen(idT = guilRdyId, dialogText = guilRdyText, choicesList = guilRdyClist, prevScreen = guilIntScr)

########

guilDstrText = "Of course we did so multiple times, but even with the help of the finest siege weapons of Ashotara we couldn't even make a dent in it."
guilDstrId = "destroy"

guilDstrCh1 = DialogChoice(idT = "BACK", text="(Back)")

guilDstrClist = [guilDstrCh1]
guilDstrScr = DialogScreen(idT = guilDstrId, dialogText = guilDstrText, choicesList = guilDstrClist, prevScreen= guilRdyScr)

########

guilFgtText = "Sadly, this is the most probable scenario, as Zarg will do everything to prevent you from reach the Cube. If that happens, I don't know if even you can be a match for him in a direct fight, so stay on the defensive, and look for an opportunity to get to the cube."
guilFgtId = "fight"

guilFgtCh1 = DialogChoice(idT = "BACK", text = "(Back)")


guilFgtClist = [guilFgtCh1]
guilFgtScr = DialogScreen(idT = guilFgtId, dialogText = guilFgtText, choicesList = guilFgtClist, prevScreen = guilRdyScr)

########

guilZrgText = "Keeping him alive would prove too much of a risk. There's little to no chance that he would turn back to his normal self anyway. I guess I don't need to explain further."
guilZrgId = "zarg"

guilZrgCh1 = DialogChoice(idT = "BACK", text = "(Back)")


guilZrgClist = [guilZrgCh1]
guilZrgScr = DialogScreen(idT = guilZrgId, dialogText = guilZrgText, choicesList = guilZrgClist, prevScreen = guilRdyScr)


########

guilUdrText = "A regular weapon is unlikely to do anything to a god. Here, let me give you Equinox, my trusty sword, it is the pride of the Guillem familly. Having been passed from generation to generation, it has defeated many terrible foes and absorbed their energy. Being the ruin of the God of Madness would make a perfect addition to its legned."
guilUdrId = "understood"

guilUdrCh1 = DialogChoice(idT = "END", text = "Very well. I shall proudly wear your sword, and when I'll return it to you it will be known as " + '"Equinox, the Scourge of the Gods" .')


guilUdrClist = [guilUdrCh1]
guilUdrScr = DialogScreen(idT = guilUdrId, dialogText = guilUdrText, choicesList = guilUdrClist, prevScreen = guilRdyScr)
guilUdrScr.onEnterFunctionName = 'markForEquinoxDrop'

########

guilHpnText = "After discovering his weakness, they were spotted by the God of Madness and indeed had to confront him head on. Of course they were no match for him, and soon realized that they had to retreat. Some were killed during the fight with Zarg, others died on the way back home due to their wounds, or because of unexpected ordeals, so well that though they were eight when they set out on their journey, only two came back alive."
guilHpnId = "happened"

guilHpnCh1 = DialogChoice(idT = "uncover", text = "While fighting him, did they discover anything else that could be useful to me in the upcoming battle ?")
guilHpnCh2 = DialogChoice(idT = "BACK", text = "(Back)")

guilHpnClist = [guilHpnCh1, guilHpnCh2]
guilHpnScr = DialogScreen(idT = guilHpnId, dialogText = guilHpnText, choicesList = guilHpnClist, prevScreen = guilIntScr)

########

guilUcvText = "Unfornately no, since it was more of a one-sided slaughter than a fight."
guilUcvId = "uncover"

guilUcvCh1 = DialogChoice(idT = "chosen", text = "Sounds like they weren't up to the task. Why were they chosen instead of more competent warriors ?")
guilUcvCh2 = DialogChoice(idT = "involved", text = "Were you involved in this ?")
guilUcvCh3 = DialogChoice(idT = "BACK", text = "(Back)")

guilUcvClist = [guilUcvCh1, guilUcvCh2, guilUcvCh3]
guilUcvScr = DialogScreen(idT = guilUcvId, dialogText = guilUcvText, choicesList = guilUcvClist, prevScreen = guilHpnScr)

########

guilChsText = "Back then, our goal wasn't to defeat him outright, but to gather as much information on him, so as to establish a plan that would then allow us to vanquish him. Therefore, instead of picking people fit for fighting him head on - since attacking him directly without knowing anything about his powers would have been suicide - we picked people fit for surviving the long expedition through harsh environments towards the Spire and for gathering intelligence inside the Spire without getting detected. Unfortunately, even though they each were among the best in their respective specialities, this wasn't enough to decieve a god, and you already know the rest."
guilChsId = "chosen"

guilChsCh1 = DialogChoice(idT = "BACK", text = "(Back)")


guilChsClist = [guilChsCh1]
guilChsScr = DialogScreen(idT = guilChsId, dialogText = guilChsText, choicesList = guilChsClist, prevScreen = guilUcvScr)

########

guilInvlText = "No, all of this was thightly kept secret from me until the survivors of the Spire infiltration came back. In fact, even the King's counselors and most of the lords didn't knew about this, and I guess it was the same situation for the other members of the Alliance."
guilInvlId = "involved"

guilInvlCh1 = DialogChoice(idT = "BACK", text = "(Back)")


guilInvlClist = [guilInvlCh1]
guilInvlScr = DialogScreen(idT = guilInvlId, dialogText = guilInvlText, choicesList = guilInvlClist, prevScreen = guilUcvScr)

########

guilFogText = "I did accompany him on a few adventures way back in the day, before I enlisted in the army, but he was a completly different man back then. The only thing he had in common with the God of Madness he is now was his incredible power : even when he was still only an human, little to no opponent stood a chance against him. I don't even want to imagine how stronger he has grown now that he has become a deity, so be careful when you face him and stick to the plan."
guilFogId = "fought"

guilFogCh1 = DialogChoice(idT = "friend", text = "Was he your friend ?")
guilFogCh2 = DialogChoice(idT = "BACK", text = "(Back)")

guilFogClist = [guilFogCh1, guilFogCh2]
guilFogScr = DialogScreen(idT = guilFogId, dialogText = guilFogText, choicesList = guilFogClist, prevScreen = guilIntScr)

########

guilFrdText = "The Zarg I used to know has died long ago, so such concerns are irrelevant to the current situation. But if you really want to know, I considered him both as a friend and as a mentor."
guilFrdId = "friend"

guilFrdCh1 = DialogChoice(idT = "INTRO", text = "...")


guilFrdClist = [guilFrdCh1]
guilFrdScr = DialogScreen(idT = guilFrdId, dialogText = guilFrdText, choicesList = guilFrdClist, prevScreen = guilFogScr)

########

guilScrList = [guilIntScr, guilRdyScr, guilDstrScr, guilFgtScr, guilUcvScr, guilChsScr, guilZrgScr, guilUdrScr, guilHpnScr, guilInvlScr, guilFogScr, guilFrdScr]
guilTree = DialogTree(screenList=guilScrList, name="Guillem", origScreen=guilScrList[0])


