import tdl, colors, textwrap
from code.constants import *
from code.menu import *

def description(text):
    wrappedText = textwrap.wrap(text, 25)
    line = 0
    for lines in wrappedText:
        line += 1
        drawCentered(cons = root, y = 35 + line, text = lines, fg = colors.white, bg = None)

def characterCreation():
    races =['Human', 'Minotaur']
    racesDescription = ['A random human', 'Minotaurs are tougher and stronger than Humans, but less smart']
    
    classes = ['Warrior', 'Rogue', 'Mage ']
    classesDescription = ['A warrior who likes to hit stuff in melee', 
                          'A wizard who zaps everything', 
                          'A rogue who is stealthy and backstabby (probably has a french accent)']

    attributes = ['Strength', 'Dexterity', 'Constitution', 'Will']
    attributesDescription = ['Strength augments the power of your attacks',
                             'Dexterity augments your accuracy and your evasion',
                             'Constitution augments your maximum health',
                             'Will augments your energy']
    
    traits = ['Placeholder']
    traitsDescription = ['This is for placeholding']
    
    skills = ['Light weapons', 'Heavy weapons', 'Missile weapons', 'Throwing weapons', 'Magic ', 'Armor wielding', 'Athletics', 'Concentration', 'Dodge ', 'Critical ', 'Accuracy']
    skillsDescription = ['Light weapons', 'Heavy weapons', 'Missile weapons', 'Throwing weapons', 'Magic ', 'Armor wielding', 'Athletics', 'Concentration', 'Dodge ', 'Critical ', 'Accuracy']
    
    #index
    index = 0
    midIndexMin = 0
    midIndexMax = len(races) + len(classes) - 1
    leftIndexMin = midIndexMax + 1
    leftIndexMax = leftIndexMin + len(attributes) + len(traits) - 1
    rightIndexMin = leftIndexMax + 1
    rightIndexMax = rightIndexMin + len(skills) - 1
    maxIndex = len(races) + len(classes) + len(attributes) + len(traits) + len(skills) + 1
    
    while not tdl.event.isWindowClosed():
        root.clear()
        drawCentered(cons = root, y = 6, text = '--- CHARACTER CREATION ---', fg = colors.white, bg = None)
        # Race and Class
        drawCentered(cons = root, y = 12, text = '-- RACE --', fg = colors.white, bg = None)
        for choice in range(len(races)):
            drawCentered(cons = root, y = 14 + choice, text = races[choice], fg = colors.white, bg = None)

        drawCentered(cons = root, y = 19, text = '-- CLASS --', fg = colors.white, bg = None)
        for choice in range(len(classes)):
            drawCentered(cons = root, y = 21 + choice, text = classes[choice], fg = colors.white, bg = None)
        
        # Attributes and traits
        leftX = (WIDTH // 4)
        drawCenteredOnX(cons = root, x = leftX, y = 34, text = '-- ATTRIBUTES --', fg = colors.white, bg = None)
        for choice in range(len(attributes)):
            drawCenteredOnX(cons = root, x = leftX, y = 36 + choice, text = attributes[choice], fg = colors.white, bg = None)

        drawCenteredOnX(cons = root, x = leftX, y = 46, text = '-- TRAITS --', fg = colors.white, bg = None)
        for choice in range(len(traits)):
            drawCenteredOnX(cons = root, x = leftX, y = 48 + choice, text = traits[choice], fg = colors.white, bg = None)
        
        # Skills
        rightX = WIDTH - (WIDTH // 4)
        drawCenteredOnX(cons = root, x = rightX, y = 34, text = '-- SKILLS --', fg = colors.white, bg = None)
        for choice in range(len(skills)):
            drawCenteredOnX(cons = root, x = rightX, y = 36 + choice, text = skills[choice], fg = colors.white, bg = None)
        
        drawCentered(cons = root, y = 34, text = '-- DESCRIPTION --', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 90, text = 'Start Game', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 91, text = 'Cancel', fg = colors.white, bg = None)
        
        # Selection
        if midIndexMin <= index <= midIndexMax:
            if index + 1 <= len(races):
                previousListLen = 0
                drawCentered(cons = root, y = 14 + index, text = races[index - previousListLen], fg = colors.black, bg = colors.white)
                description(racesDescription[index - previousListLen])
            else:
                previousListLen = len(races)
                drawCentered(cons = root, y = 19 + index, text = classes[index - previousListLen], fg = colors.black, bg = colors.white)
                description(classesDescription[index - previousListLen])
        if leftIndexMin <= index <= leftIndexMax:
            if index + 1 <= len(races) + len(classes) + len(attributes):
                previousListLen = len(races) + len(classes)
                drawCenteredOnX(cons = root, x = leftX, y = 31 + index, text = attributes[index - previousListLen], fg = colors.black, bg = colors.white)
                description(attributesDescription[index - previousListLen])
            else:
                previousListLen = len(races) + len(classes) + len(attributes)
                drawCenteredOnX(cons = root, x = leftX, y = 39 + index, text = traits[index - previousListLen], fg = colors.black, bg = colors.white)
                description(traitsDescription[index - previousListLen])
        if rightIndexMin <= index <= rightIndexMax:
            previousListLen = len(races) + len(classes) + len(attributes) + len(traits)
            drawCenteredOnX(cons = root, x = rightX, y = 26 + index, text = skills[index - previousListLen], fg = colors.black, bg = colors.white)
            description(skillsDescription[index - previousListLen])
        if index == maxIndex - 1:
            drawCentered(cons = root, y = 90, text = 'Start Game', fg = colors.black, bg = colors.white)
        if index == maxIndex:
            drawCentered(cons = root, y = 91, text = 'Cancel', fg = colors.black, bg = colors.white)

        tdl.flush()

        key = tdl.event.key_wait()
        if key.keychar.upper() == 'DOWN':
            index += 1
        if key.keychar.upper() == 'UP':
            index -= 1
        if key.keychar.upper() == 'RIGHT' and (leftIndexMin <= index <= leftIndexMax):
            if rightIndexMin <= index + len(attributes) + len(traits) <= rightIndexMax:
                index += len(attributes) + len(traits)
            else:
                index = rightIndexMax
        if key.keychar.upper() == 'LEFT' and (rightIndexMin <= index <= rightIndexMax):
            if leftIndexMin <= index - len(skills) <= leftIndexMax:
                index -= len(skills)
            else:
                index = leftIndexMax
        if key.keychar.upper() == 'ENTER' and index == maxIndex - 1:
            #To be moved at the very end of this statement once selection system is complete
            break
        if index > maxIndex:
            index = 0
        if index < 0:
            index = maxIndex