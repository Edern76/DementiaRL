import copy
import code.custom_except
from random import randint
from code.constants import *
from code.classes import *
import colors
import os, sys

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    listDir = list(datadir)
    for loop in range(4):
        del listDir[len(listDir) - 1]
    print(listDir)
    dir = ''
    for loop in range(len(listDir) - 1):
        dir += listDir[loop]
    print(dir)
    return dir

SPELL_GEN_DEBUG = False
BUFF_POTENTIAL_ATTENUATION_COEFFICIENT = 2

curDir = findCurrentDir()
relSpellsPath = "assets\\spells"
absSpellsPath = os.path.join(curDir, relSpellsPath)
        
    
    


'''
HOW SPELL GEN IS GOING TO WORK (Spoiler : In a way way more complex than what's needed)



                                                                                                                                      
                                                                                                                                     Pure attack ---- Roll amount
                                                                                                                                   /
                                                                                                           Bad effect (high chance)
                                                                                                          /                        \ Debuff ---- Roll turn duration
                                                                                                         /
                 Attack ---- Target/Zone choice ---- Number of effects = randint(1,3) - For each effect /
              /                                                                                         \                            Heal ---- Roll amount
             /                                                                                           \                         /
            /                                                                                             \Good effect (low chance)
           /                                                                                                                       \ Buff ---- Roll turn duration
          /
         /  
TypeSelect                        (Had lot of !!FUN!! making this)
        \    
         \                                                                                                                         Heal ---- Roll amount
          \                                                                                                                      /
           \                                                                                            Good effect (high chance)
            \                                                                                         /                          \
             \                                                                                       /                            Buff  ---- Roll turn duration
              Defense ---- Target/Zone choice ---- Number of effects = randint(1,3) - For each effect
                                                                                                    \                          Attack ---- Roll amount
                                                                                                     \                       /
                                                                                                      Bad effect (low chance)
                                                                                                                             \
                                                                                                                               Debuff ---- Roll turn duration

If a spell has an effect that doesn't fit its type (Good effect on attack spell, bad effect on defense spell), it is considered as "impure" and therefore has reduced MP and skill requirements than a normal spell.




'''
baseTypeList = BetterList("Attack", "Defense")
nameAOE = {}
nameAttack = {}
nameBuff = {}
nameHeal = {}

targetSelect = WeightedChoice("Select", 25)
targetSelf = WeightedChoice("Self", 25)
targetClosest = WeightedChoice("Closest", 25)
targetFarthest = WeightedChoice("Farthest", 25)

zoneSingle = WeightedChoice("SingleTile", 20)
zoneCross = WeightedChoice("Cross", 20)
zoneX = WeightedChoice("X", 20)
zoneAOE = WeightedChoice("AOE", 20)
zoneLine = WeightedChoice('Line', 20)

nameAOE[zoneSingle] = 'bolt'
nameAOE[zoneCross] = 'cross'
nameAOE[zoneX] = 'strikes'
nameAOE[zoneAOE] = 'blast'
nameAOE[zoneLine] = 'ray'

attFire = WeightedChoice("Fire damage", 20)
attPhy = WeightedChoice("Physical damage", 20)
attPoi = WeightedChoice("Poison damage", 20)
attIce = WeightedChoice('Ice damage', 20)
attElec = WeightedChoice('Lightning damage', 20)

nameAttack[attFire.name] = ['fire', 'burning']
nameAttack[attPhy.name] = ['death', '']
nameAttack[attPoi.name] = ['poison', 'toxic']
nameAttack[attIce.name] = ['frost', 'cold']
nameAttack[attElec.name] = ['lightning', 'electric']

buffHunger = WeightedChoice("Hunger", 25)
buffAttack = WeightedChoice("Power", 25)
buffDefense = WeightedChoice("Armor", 25)
buffSpeed = WeightedChoice("Speed", 25)

nameBuff[buffHunger.name] = ['nourishing', 'hungering']
nameBuff[buffAttack.name] = ['strengthening', 'weakening']
nameBuff[buffDefense.name] = ['shielding', 'exposing']
nameBuff[buffSpeed.name] = ['hastening', 'slowing']

healHP = WeightedChoice("Heal HP", 25)
healMP = WeightedChoice("Heal MP", 25)
healFire = WeightedChoice("Cure fire", 25)
healPoison = WeightedChoice("Cure poison", 25)

nameHeal[healHP.name] = 'health'
nameHeal[healMP.name] = 'mana'
nameHeal[healFire.name] = 'fire cure'
nameHeal[healPoison.name] = 'poison cure'

baseTargetList = EvenBetterList(targetSelect, targetSelf, targetClosest, targetFarthest)
baseZoneList = EvenBetterList(zoneSingle, zoneCross, zoneX, zoneAOE, zoneLine)

baseAttackList = EvenBetterList(attFire, attPhy, attPoi, attIce, attElec) #Porbably want to add more stuff here
baseBuffList = EvenBetterList(buffHunger, buffAttack, buffDefense, buffSpeed) #Common list for buffs/debuffs
baseHealList = EvenBetterList(healHP, healMP , healFire , healPoison)

def createSpell():
    valid = False
    while not valid:
        spellLevel = randint(1,5)
        valid = True
        isImpure = False
        
        typeList = copy.copy(baseTypeList)
        targetList = copy.copy(baseTargetList)
        zoneList = copy.copy(baseZoneList)
        
        attackList = copy.copy(baseAttackList)
        buffList = copy.copy(baseBuffList)
        healList = copy.copy(baseHealList)
        
        type = typeList.randFrom()
        
        if type == "Attack":
            targetList.removeFrom(targetSelf)
            zoneSingle.prob = 25
        elif type == "Defense":
            targetList.removeFrom(targetClosest)
            targetList.removeFrom(targetFarthest)
            zoneSingle.prob = 75
        else:
            print(type)
            raise ValueError("Invalid spell type")
        
        target = targetList.randFrom()
        if target.name == 'Self':
            zoneList.removeFrom(zoneLine)
        zone = zoneList.randFrom()
        
        if spellLevel > 3:
            maxEffects = 3
        elif spellLevel >= 2:
            maxEffects = 2
        else:
            maxEffects = 1
        noOccult = False
        noNormal = False
        effects = [None, None, None]
        potential = 0
        curMaxCount = 0
        bestEffect = None
        for loop in range(maxEffects):
            isBuff = False

            curEffectImpure = False
            if type == "Attack":
                if maxEffects == 1:
                    effectAlign = "Bad"
                else:
                    dice = randint(0, 100)
                    if dice < 80:
                        effectAlign = "Bad"
                    else:
                        effectAlign = "Good"
                        isImpure = True
                        curEffectImpure = True
            elif type == "Defense":
                if maxEffects == 1:
                    effectAlign = "Good"
                else:
                    dice = randint(0, 100)
                    if dice < 80:
                        effectAlign = "Good"
                    else:
                        effectAlign = "Bad"
                        isImpure = True
                        curEffectImpure = True
            
            if effectAlign == "Good":
                dice = randint(0, 1)
                if dice == 0:
                    eff = buffList.randFrom()
                    buffList.removeFrom(eff)
                    effName = eff.name
                    #buffList.
                    effName += "+"
                    isBuff = True
                else:
                    eff = healList.randFrom()
                    healList.removeFrom(eff)
                    effName = eff.name
                    if effName == "Heal HP":
                        noOccult = True
                        healList.removeFrom(healList[0]) #Removes "HealMP" from the list, because spending MP to recover MP is either useless (if you recover less MP than you spend) or gamebreakingly overpowered (if you recover more MP than you spend)
                    elif effName == "Heal MP":
                        noNormal = True
                        healList.removeFrom(healList[0]) #Removes "HealHP" from the list. Same as above.
                    
            else:
                dice = randint(0, 1)
                if dice == 0:
                    eff = buffList.randFrom()
                    buffList.removeFrom(eff)
                    effName = eff.name
                    effName += '-'
                    isBuff = True
                else:
                    eff = attackList.randFrom()
                    attackList.removeFrom(eff)
                    effName = eff.name
            

            
            if not isBuff:
                effAmount = randint(spellLevel, spellLevel * 5)  * randint(2, 3) #should take into account player and/or dungeon level with the sigmoid progression
                effCounter = effAmount
                if not curEffectImpure:
                    potential += effAmount
                elif potential - effAmount > 0:
                    print("POTENTIAL BEFORE : " + str(potential))
                    print("AMOUNT : " + str(effAmount))
                    print("ITERAITON : " +str(loop))
                    potential -= effAmount
                    print("POTENTIAL AFTER : " + str(potential))
                else:
                    print("POTENTIAL BEFORE : " + str(potential))
                    print("AMOUNT : " + str(effAmount))
                    print("ITERAITON : " +str(loop))
                    print("TOO MUCH, RESETTING POTENTIAL")
                    potential = 0
                    print("POTENTIAL AFTER : " + str(potential))
            else:
                '''
                if eff.name in ["CureFire", "CurePoison"]:
                    bonus = randint(2, 3)
                else:
                    bonus = 1
                '''
                bonus = 1
                effAmount = (randint(spellLevel, spellLevel * 2) * randint(1, 3) * bonus) + 1 #should take into account player and/or dungeon level with the sigmoid progression
                effCounter = effAmount // 2
                if not curEffectImpure:
                    potential += (effAmount // BUFF_POTENTIAL_ATTENUATION_COEFFICIENT)
                elif potential - (effAmount // BUFF_POTENTIAL_ATTENUATION_COEFFICIENT) > 0:
                    print("POTENTIAL BEFORE : " + str(potential))
                    print("AMOUNT : " + str(effAmount))
                    print("ITERAITON : " +str(loop))
                    potential -= (effAmount // BUFF_POTENTIAL_ATTENUATION_COEFFICIENT)
                    print("POTENTIAL AFTER : " + str(potential))
                else:
                    print("POTENTIAL BEFORE : " + str(potential))
                    print("AMOUNT : " + str(effAmount))
                    print("ITERAITON : " +str(loop))
                    print("TOO MUCH, RESETTING POTENTIAL")
                    potential = 0
                    print("POTENTIAL AFTER : " + str(potential))
            
            if not curEffectImpure and effCounter > curMaxCount:
                curMaxCount = effCounter
                bestEffect = eff.name
            effects[loop] = NumberedEffect(effName, effAmount)
        
        if isImpure:
            spellLevel -= 1
        
        if bestEffect == "Fire damage":
            spellColor = colors.red
        elif bestEffect == "Poison damage":
            spellColor = colors.purple
        elif bestEffect == 'Ice damage':
            spellColor = colors.light_violet
        elif bestEffect == 'Lightning damage':
            spellColor = colors.light_cyan
        else:
            spellColor = colors.white
        
        if potential == 0:
            valid = False 
            print("DISCARDING !")
            print("REALLY GOING TO DISCARD !")
            print("DISCARDED")
           
        else:
            cost = (potential // 4 + randint(2, 10)) * spellLevel
            dice = randint(1, 100)
            if (dice <= 80 or noOccult) and not noNormal:
                ressource = "MP"
            else:
                ressource = "HP"
            
            resultSpell = SpellTemplate(spellLevel, cost, type, ressource)
            resultSpell.impure = isImpure
            resultSpell.eff1 = effects[0]
            resultSpell.eff2 = effects[1]
            resultSpell.eff3 = effects[2]
            
            resultSpell.targeting = target.name
            resultSpell.zone = zone.name
            
            resultSpell.color = spellColor
            
            name = ''
            if isImpure:
                name += 'impure '
                
            for eff in effects:
                try:
                    ind = 1
                    if '+' in eff.name:
                        ind = 0
                    tempName = copy.copy(eff.name[:len(eff.name)-1])
                    name += nameBuff[tempName][ind] + ' '
                except:
                    pass
                
            chosen = []
            for eff in effects:
                try:
                    chosen.append(nameAttack[eff.name])
                except:
                    pass
            if chosen:
                if len(chosen) > 1:
                    if chosen[len(chosen)-1][0] == 'death':
                        chosen.reverse()
                    for eff in chosen[:len(chosen)-1]:
                        if eff[1] != '':
                            name += eff[1] + ' '
                name += chosen[len(chosen)-1][0]
            name += nameAOE[zone] + ' '
            
            for eff in effects:
                try:
                    name += 'of ' + nameHeal[eff.name] + ' '
                except:
                    pass
            
            resultSpell.name = name
            
            return resultSpell

def convertColorString(string):
    color = {'r': '', 'g': '', 'b': ''}
    currentColor = 'r'
    for char in string:
        if char in '0123456789':
            color[currentColor] += char
        elif char == ',':
            if currentColor == 'r':
                currentColor = 'g'
            elif currentColor == 'g':
                currentColor = 'b'
        elif char == ')':
            return (int(color['r']), int(color['g']), int(color['b']))

def readSpellFile(fileName):  #without .txt
    '''
    name
    color (tuple)
    level (int) #level needed in the major type to cast. will be divided by 2 to get level needed in subType
    ressource (MP/HP/stamina)
    ressourceCost (int)
    type (School)
    subtype
    impure (True/False)
    targeting (Select/Self/Closest/Farthest)
    zone (SingleTile, Cross, X, AOE, Line, Cone)
    eff1,amount1  (string, int) WITHOUT SPACE
    eff2,amount2    default: None or *
    eff3,amount3    default: None or *
    #always keep this line filled
    '''
    
    file = open(os.path.join(absSpellsPath, fileName+'.txt'), 'r')
    file = [line[:len(line)-1] for line in file]
    print(file)
    template = SpellTemplate()
    
    template.name = file[0]
    template.color = convertColorString(file[1])
    template.level = int(file[2])
    template.ressource = file[3]
    template.cost = file[4]
    template.type = file[5]
    if file[6] != '*':
        template.subtype = file[6]
    if file[7] == 'True':
        template.impure = True
    else:
        template.impure = False
    template.targeting = file[8]
    template.zone = file[9]
    
    for i in range(3):
        if file[10+i] != 'None' and file[10+i] != '*' and file[10+i] != '':
            textList = file[10+i].split(',')
            effect = NumberedEffect(textList[0], str(textList[1]))
        else:
            effect = None
        
        if i == 0:
            template.eff1 = effect
        elif i == 1:
            template.eff2 = effect
        else:
            template.eff3 = effect
    
    return template


'''
@Fire is the simple minded school. It revolves around dealing damage in area of effects and burning its targets, and, when used at its best,
can wreak havoc on hordes of foes, all of this while empowering it's master's strength.

@Air is subtler. While it can damage and stun its targets with electricity, it can also be used to fasten movements and increase dexterity,
or to push back enemies.

@Water is all about control. Rarely damaging, it can however slow or even freeze its targets. Water mages are also often the ones with the
most willpower.

@Earth is not as smart as Air and Water, but draws its powers from earth's energy flux. It is a passive school, based on vital strength,
and can either regenerate wounded tissues or poison enemies.

@Arcane or Light magic is more about energy. While it can blind or damage enemies, it will most often be used to gather mana or to block
certain areas thaks to force fields.

@Necromancy is the school of the undead. Unlike most other schools, it drains energy directly from the caster's vital energy, so as to raise 
dead foes to life or to wither its targets.

@Dark magic is schools of shadows, and, like the Necromancy school, draws its powers from the caster's vital energy. No harm can be suffered from
its spells directly, but it can conceal the caster, or even make him invisible.
'''

if __name__ == '__main__':
    templates = ['fireball']
    for loop in range(10):
        spell = createSpell()
        print('====  ' + spell.name + '  ====', spell, sep = '\n\n')
        print()
    for name in templates:
        print('====  ' + name + '  ====')
        print(readSpellFile(name))
        
        
    
    
    
    
    
    