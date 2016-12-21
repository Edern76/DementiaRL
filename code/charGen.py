import tdl, colors, textwrap
from code.constants import *
from code.menu import *

BASE_POWER = 1
BASE_ACCURACY = 20
BASE_EVASION = 1
BASE_ARMOR = 0
BASE_MAXHP = 0
BASE_MAXMP = 0
BASE_CRITICAL = 5

power = BASE_POWER
accuracy = BASE_ACCURACY
evasion = BASE_EVASION
armor = BASE_ARMOR
maxHP = BASE_MAXHP
maxMP = BASE_MAXMP
critical = BASE_CRITICAL

def description(text):
    wrappedText = textwrap.wrap(text, 25)
    line = 0
    for lines in wrappedText:
        line += 1
        drawCentered(cons = root, y = 35 + line, text = lines, fg = colors.white, bg = None)

def applyBonus(list, chosenList):
    global power, accuracy, evasion, armor, maxHP, maxMP, critical
    power += list[chosenList][0]
    accuracy += list[chosenList][1]
    evasion += list[chosenList][2]
    armor += list[chosenList][3]
    maxHP += list[chosenList][4]
    maxMP += list[chosenList][5]
    critical += list[chosenList][6]

def removeBonus(list, chosenList):
    global power, accuracy, evasion, armor, maxHP, maxMP, critical
    power -= list[chosenList][0]
    accuracy -= list[chosenList][1]
    evasion -= list[chosenList][2]
    armor -= list[chosenList][3]
    maxHP -= list[chosenList][4]
    maxMP -= list[chosenList][5]
    critical -= list[chosenList][6]

#Bonus template: [power, accuracy, evasion, armor, maxHP, maxMP, critical]

def characterCreation():
    races =['Human', 'Minotaur']
    racesDescription = ['A random human',
                        'Minotaurs are tougher and stronger than Humans, but less smart']
    racesBonus = [[0, 0, 0, 0, 0, 0, 0], #Human
                  [5, -8, -4, 0, 20, -15, 0]] #Minotaur
    MAX_RACES = 1
    actualRaces = 0
    selectedRaces = [False, False]
    
    classes = ['Knight', 'Barbarian', 'Rogue', 'Mage ']
    classesDescription = ['A warrior who wears armor and yields shields',
                          'A brutal fighter who is mighty strong',
                          'A rogue who is stealthy and backstabby (probably has a french accent)',
                          'A wizard who zaps everything']
    classesBonus = [[0, 0, 0, 1, 60, 30, 0], #Knight
                    [1, 0, 0, 0, 80, 30, 0], #Barbarian
                    [0, 8, 10, 0, 45, 40, 3], #Rogue
                    [0, 0, 0, 0, 35, 50, 0]] #Mage
    classesLevelUp = [[0, 0, 0, 1, 7, 3, 0],
                      [1, 0, 0, 0, 10, 3, 0],
                      [0, 2, 1, 0, 5, 5, 0],
                      [0, 0, 0, 0, 3, 7, 0]]
    MAX_CLASSES = 1
    actualClasses = 0
    selectedClasses = [False, False, False, False]

    attributes = ['Strength', 'Dexterity', 'Constitution', 'Willpower']
    attributesDescription = ['Strength augments the power of your attacks',
                             'Dexterity augments your accuracy and your evasion',
                             'Constitution augments your maximum health',
                             'Willpower augments your energy']
    attributesBonus = [[1, 0, 0, 0, 0, 0, 0], #strength
                       [0, 2, 1, 0, 0, 0, 0], #dex
                       [0, 0, 0, 0, 5, 0, 0], #vitality
                       [0, 0, 0, 0, 0, 5, 0]] #willpower
    MAX_ATTRIBUTES_POINTS = 10
    MAX_PER_ATTRIBUTES = 5
    actualAttributesPoints = 0
    actualPerAttributes = [0, 0, 0, 0]
    selectedAttributes = [False, False, False, False]
    
    traits = ['Placeholder']
    traitsDescription = ['This is for placeholding']
    traitsBonus= [[0, 0, 0, 0, 0, 0, 0]]
    MAX_TRAITS = 2
    actualTraits = 0
    selectedTraits = [False]
    
    skills = ['Light weapons', 'Heavy weapons', 'Missile weapons', 'Throwing weapons', 'Magic ', 'Armor wielding', 'Athletics', 'Concentration', 'Dodge ', 'Critical ', 'Accuracy']
    skillsDescription = ['Light weapons', 'Heavy weapons', 'Missile weapons', 'Throwing weapons', 'Magic ', 'Armor wielding', 'Athletics', 'Concentration', 'Dodge ', 'Critical ', 'Accuracy']
    skillsBonus = [[0, 0, 0, 0, 0, 0, 0], #light
                   [0, 0, 0, 0, 0, 0, 0], #heavy
                   [0, 0, 0, 0, 0, 0, 0], #missile
                   [0, 0, 0, 0, 0, 0, 0], #throwing
                   [0, 0, 0, 0, 0, 0, 0], #magic
                   [0, 0, 0, 0, 0, 0, 0], #armor
                   [0, 0, 0, 0, 20, 0, 0], #athletics
                   [0, 0, 0, 0, 0, 20, 0], #concentration
                   [0, 0, 3, 0, 0, 0, 0], #dodge
                   [0, 0, 0, 0, 0, 0, 3], #crit
                   [0, 10, 0, 0, 0, 0, 0]] #accuracy
    MAX_SKILLS = 2
    MAX_PER_SKILLS = 1
    actualSkills = 0
    actualPerSkills = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    selectedSkills = [False, False, False, False, False, False, False, False, False, False, False]
    
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
            if selectedRaces[choice]:
                drawCentered(cons = root, y = 14 + choice, text = races[choice], fg = colors.azure, bg = None)
            else:
                drawCentered(cons = root, y = 14 + choice, text = races[choice], fg = colors.white, bg = None)

        drawCentered(cons = root, y = 19, text = '-- CLASS --', fg = colors.white, bg = None)
        for choice in range(len(classes)):
            if selectedClasses[choice]:
                drawCentered(cons = root, y = 21 + choice, text = classes[choice], fg = colors.azure, bg = None)
            else:
                drawCentered(cons = root, y = 21 + choice, text = classes[choice], fg = colors.white, bg = None)
        
        # Attributes and traits
        leftX = (WIDTH // 4)
        drawCenteredOnX(cons = root, x = leftX, y = 33, text = '-- ATTRIBUTES --', fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = leftX, y = 34, text = str(actualAttributesPoints) + '/' + str(MAX_ATTRIBUTES_POINTS), fg = colors.white, bg = None)
        for choice in range(len(attributes)):
            if selectedAttributes[choice]:
                drawCenteredOnX(cons = root, x = leftX, y = 36 + choice, text = attributes[choice], fg = colors.azure, bg = None)
            else:
                drawCenteredOnX(cons = root, x = leftX, y = 36 + choice, text = attributes[choice], fg = colors.white, bg = None)
            drawCenteredOnX(cons = root, x = leftX - 10, y = 36 + choice, text = str(actualPerAttributes[choice]) + '/' + str(MAX_PER_ATTRIBUTES), fg = colors.white, bg = None)

        drawCenteredOnX(cons = root, x = leftX, y = 45, text = '-- TRAITS --', fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = leftX, y = 46, text = str(actualTraits) + '/' + str(MAX_TRAITS), fg = colors.white, bg = None)
        for choice in range(len(traits)):
            if selectedTraits[choice]:
                drawCenteredOnX(cons = root, x = leftX, y = 48 + choice, text = traits[choice], fg = colors.azure, bg = None)
            else:
                drawCenteredOnX(cons = root, x = leftX, y = 48 + choice, text = traits[choice], fg = colors.white, bg = None)
        
        # Skills
        rightX = WIDTH - (WIDTH // 4)
        drawCenteredOnX(cons = root, x = rightX, y = 33, text = '-- SKILLS --', fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = rightX, y = 34, text = str(actualSkills) + '/' + str(MAX_SKILLS), fg = colors.white, bg = None)
        for choice in range(len(skills)):
            if selectedSkills[choice]:
                drawCenteredOnX(cons = root, x = rightX, y = 36 + choice, text = skills[choice], fg = colors.azure, bg = None)
            else:
                drawCenteredOnX(cons = root, x = rightX, y = 36 + choice, text = skills[choice], fg = colors.white, bg = None)
        
        drawCentered(cons = root, y = 33, text = '-- DESCRIPTION --', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 90, text = 'Start Game', fg = colors.white, bg = None)
        drawCentered(cons = root, y = 91, text = 'Cancel', fg = colors.white, bg = None)

        #Displaying stats
        eightScreen = WIDTH//8
        drawCenteredOnX(cons = root, x = eightScreen * 1, y = 82, text = 'Power: ' + str(power), fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = eightScreen * 2, y = 82, text = 'Accuracy: ' + str(accuracy), fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = eightScreen * 3, y = 82, text = 'Evasion: ' + str(evasion), fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = eightScreen * 4, y = 82, text = 'Armor: ' + str(armor), fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = eightScreen * 5, y = 82, text = 'Max HP: ' + str(maxHP), fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = eightScreen * 6, y = 82, text = 'Max MP: ' + str(maxMP), fg = colors.white, bg = None)
        drawCenteredOnX(cons = root, x = eightScreen * 7, y = 82, text = 'Critical: ' + str(critical), fg = colors.white, bg = None)
        
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
                drawCenteredOnX(cons = root, x = leftX, y = 30 + index, text = attributes[index - previousListLen], fg = colors.black, bg = colors.white)
                description(attributesDescription[index - previousListLen])
            else:
                previousListLen = len(races) + len(classes) + len(attributes)
                drawCenteredOnX(cons = root, x = leftX, y = 38 + index, text = traits[index - previousListLen], fg = colors.black, bg = colors.white)
                description(traitsDescription[index - previousListLen])
        if rightIndexMin <= index <= rightIndexMax:
            previousListLen = len(races) + len(classes) + len(attributes) + len(traits)
            drawCenteredOnX(cons = root, x = rightX, y = 25 + index, text = skills[index - previousListLen], fg = colors.black, bg = colors.white)
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
        #adding choice bonus
        if key.keychar.upper() == 'ENTER':
            if midIndexMin <= index <= midIndexMax:
                if index + 1 <= len(races):
                    if actualRaces < MAX_RACES:
                        previousListLen = 0
                        selectedRaces[index] = True
                        applyBonus(racesBonus, index)
                        actualRaces += 1
                else:
                    if actualClasses < MAX_CLASSES:
                        previousListLen = len(races)
                        selectedClasses[index - previousListLen] = True
                        applyBonus(classesBonus, index - previousListLen)
                        levelUpStats = classesLevelUp[index - previousListLen]
                        actualClasses += 1
            if leftIndexMin <= index <= leftIndexMax:
                if index + 1 <= len(races) + len(classes) + len(attributes):
                    if actualAttributesPoints < MAX_ATTRIBUTES_POINTS:
                        previousListLen = len(races) + len(classes)
                        if actualPerAttributes[index - previousListLen] < MAX_PER_ATTRIBUTES:
                            applyBonus(attributesBonus, index - previousListLen)
                            selectedAttributes[index - previousListLen] = True
                            actualAttributesPoints += 1
                            actualPerAttributes[index - previousListLen] +=1
                else:
                    if actualTraits < MAX_TRAITS:
                        previousListLen = len(races) + len(classes) + len(attributes)
                        selectedTraits[index - previousListLen] = True
                        applyBonus(traitsBonus, index - previousListLen)
                        actualTraits += 1
            if rightIndexMin <= index <= rightIndexMax:
                if actualSkills < MAX_SKILLS:
                    previousListLen = len(races) + len(classes) + len(attributes) + len(traits)
                    if actualPerSkills[index - previousListLen] < MAX_PER_SKILLS:
                        applyBonus(skillsBonus, index - previousListLen)
                        selectedSkills[index - previousListLen] = True
                        actualSkills += 1
                        actualPerSkills[index - previousListLen] += 1
            if index == maxIndex - 1:
                createdCharacter = [power, accuracy, evasion, armor, maxHP, maxMP, critical]
                return createdCharacter, levelUpStats, actualPerSkills, skillsBonus
            if index == maxIndex:
                return 'cancelled', 'cancelled', 'cancelled', 'cancelled'
        #removing choice bonus
        if key.keychar.upper() == 'BACKSPACE':
            if midIndexMin <= index <= midIndexMax:
                if index + 1 <= len(races):
                    if actualRaces > 0:
                        previousListLen = 0
                        selectedRaces[index - previousListLen] = False
                        removeBonus(racesBonus, index)
                        actualRaces -= 1
                else:
                    if actualClasses > 0:
                        previousListLen = len(races)
                        selectedClasses[index - previousListLen] = False
                        removeBonus(classesBonus, index - previousListLen)
                        levelUpStats = [0, 0, 0, 0, 0, 0, 0]
                        actualClasses -= 1
            if leftIndexMin <= index <= leftIndexMax:
                if index + 1 <= len(races) + len(classes) + len(attributes):
                    if actualAttributesPoints > 0:
                        previousListLen = len(races) + len(classes)
                        if actualPerAttributes[index - previousListLen] > 0:
                            removeBonus(attributesBonus, index - previousListLen)
                            selectedAttributes[index - previousListLen] = False
                            actualAttributesPoints -= 1
                            actualPerAttributes[index - previousListLen] -=1
                else:
                    if actualTraits > 0:
                        previousListLen = len(races) + len(classes) + len(attributes)
                        selectedTraits[index - previousListLen] = False
                        removeBonus(traitsBonus, index - previousListLen)
                        actualTraits -= 1
            if rightIndexMin <= index <= rightIndexMax:
                if actualSkills > 0:
                    previousListLen = len(races) + len(classes) + len(attributes) + len(traits)
                    if actualPerSkills[index - previousListLen] > 0:
                        removeBonus(skillsBonus, index - previousListLen)
                        selectedSkills[index - previousListLen] = False
                        actualSkills -= 1
                        actualPerSkills[index - previousListLen] -= 1
        if index > maxIndex:
            index = 0
        if index < 0:
            index = maxIndex