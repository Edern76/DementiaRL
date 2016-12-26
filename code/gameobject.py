from code.constants import *
from code.sharedvariables import *
import math
import colors

pathfinder = None

def closestMonster(max_range):
    closestEnemy = None
    closestDistance = max_range + 1

    for object in objects:
        if object.Fighter and not object == player and (object.x, object.y) in visibleTiles:
            dist = player.distanceTo(object)
            if dist < closestDistance:
                closestEnemy = object
                closestDistance = dist
    return closestEnemy

class GameObject:
    "A generic object, represented by a character"
    def __init__(self, x, y, char, name, color = colors.white, blocks = False, Fighter = None, AI = None, Player = None, Ghost = False, Item = None, alwaysVisible = False, darkColor = None, Equipment = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
        self.Fighter = Fighter
        self.Player = Player
        self.ghost = Ghost
        self.Item = Item
        self.alwaysVisible = alwaysVisible
        self.darkColor = darkColor
        if self.Fighter:  #let the fighter component know who owns it
            self.Fighter.owner = self
        self.AI = AI
        if self.AI:  #let the AI component know who owns it
            self.AI.owner = self
        if self.Player:
            self.Player.owner = self
        if self.Item:
            self.Item.owner = self 
        self.Equipment = Equipment
        if self.Equipment:
            self.Equipment.owner = self

    def moveTowards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def move(self, dx, dy):
        if self.Fighter and self.Fighter.frozen:
            pass
        elif not isBlocked(self.x + dx, self.y + dy) or self.ghost:
            self.x += dx
            self.y += dy
    
    def draw(self):
        if (self.x, self.y) in visibleTiles:
            con.draw_char(self.x, self.y, self.char, self.color, bg=None)
        elif self.alwaysVisible and myMap[self.x][self.y].explored:
            con.draw_char(self.x, self.y, self.char, self.darkColor, bg=None)
        
    def clear(self):
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)

    def distanceTo(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def distanceToCoords(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
            
    def sendToBack(self): #used to make anything appear over corpses
        global objects
        objects.remove(self)
        objects.insert(0, self)
    
    def moveAstar(self, destX, destY):
        global tilesinPath, pathfinder
        self.astarPath = pathfinder.get_path(self.x, self.y, destX, destY)
        tilesinPath.extend(self.astarPath)
        if len(self.astarPath) != 0:
            if DEBUG:
                print(self.name + "'s path :", end = " ")
                for (x,y) in self.astarPath:
                    print (str(x) + "/" + str(y) + ";", end = " ", sep = " ")
                    print()
            (x, y) = self.astarPath[0]
            self.x = x
            self.y = y
            if DEBUG:
                print(self.name + " moved to " + str(self.x) + ', ' + str(self.y))
            
        else:
            self.moveTowards(destX, destY)
            if DEBUG:
                print(self.name + " found no Astar path")

class Fighter: #All NPCs, enemies and the player
    def __init__(self, hp, armor, power, accuracy, evasion, xp, deathFunction=None, maxMP = 0, knownSpells = None, critical = 5, lootFunction = None, lootRate = 0):
        self.baseMaxHP = hp
        self.hp = hp
        self.baseArmor = armor
        self.basePower = power
        self.deathFunction = deathFunction
        self.xp = xp
        self.baseAccuracy = accuracy
        self.baseEvasion = evasion
        self.baseCritical = critical
        self.lootFunction = lootFunction
        self.lootRate = lootRate 
        
        self.frozen = False
        self.freezeCooldown = 0
        
        self.burning = False
        self.burnCooldown = 0
        
        self.healCountdown = 10
        self.MPRegenCountdown = 10
        
        self.baseMaxMP = maxMP
        self.MP = maxMP
        
        if knownSpells != None:
            self.knownSpells = knownSpells
        else:
            self.knownSpells = []
        
        self.spellsOnCooldown = []

    @property
    def power(self):
        bonus = sum(equipment.powerBonus for equipment in getAllEquipped(self.owner))
        return self.basePower + bonus
 
    @property
    def armor(self):
        bonus = sum(equipment.armorBonus for equipment in getAllEquipped(self.owner))
        return self.baseArmor + bonus
 
    @property
    def maxHP(self):
        bonus = sum(equipment.maxHP_Bonus for equipment in getAllEquipped(self.owner))
        return self.baseMaxHP + bonus

    @property
    def accuracy(self):
        bonus = sum(equipment.accuracyBonus for equipment in getAllEquipped(self.owner))
        return self.baseAccuracy + bonus

    @property
    def evasion(self):
        bonus = sum(equipment.evasionBonus for equipment in getAllEquipped(self.owner))
        return self.baseEvasion + bonus

    @property
    def critical(self):
        bonus = sum(equipment.criticalBonus for equipment in getAllEquipped(self.owner))
        return self.baseCritical + bonus

    @property
    def maxMP(self):
        bonus = sum(equipment.maxMP_Bonus for equipment in getAllEquipped(self.owner))
        return self.baseMaxMP + bonus
        
    def takeDamage(self, damage):
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            death=self.deathFunction
            if death is not None:
                death(self.owner)
            if self.owner != player:
                player.Fighter.xp += self.xp

    def toHit(self, target):
        attack = randint(1, 100)
        hit = False
        criticalHit = False
        if target.Fighter.evasion < 1:
            currentEvasion = 1
        else:
            currentEvasion = target.Fighter.evasion
        if self.accuracy < 1:
            currentAccuracy = 1
        else:
            currentAccuracy = self.accuracy
        hitRatio = int((currentAccuracy / currentEvasion) * 100)
        if DEBUG:
            message(self.owner.name.capitalize() + ' rolled a ' + str(attack) + ' over ' + str(hitRatio), colors.violet)
        if attack <= hitRatio and attack < 96:
            hit = True
            if attack <= self.critical:
                criticalHit = True
        return hit, criticalHit

    def attack(self, target):
        [hit, criticalHit] = self.toHit(target)
        if hit:
            if criticalHit:
                damage = (self.power - target.Fighter.armor) * 3
            else:
                damage = self.power - target.Fighter.armor
            if not self.frozen:
                if not self.owner.Player:
                    if damage > 0:
                        if criticalHit:
                            message(self.owner.name.capitalize() + ' critically hits you for ' + str(damage) + ' hit points!', colors.dark_orange)
                        else:
                            message(self.owner.name.capitalize() + ' attacks you for ' + str(damage) + ' hit points.', colors.orange)
                        target.Fighter.takeDamage(damage)
                    else:
                        message(self.owner.name.capitalize() + ' attacks you but it has no effect!')
                else:
                    if damage > 0:
                        if criticalHit:
                            message('You critically hit ' + target.name + ' for ' + str(damage) + ' hit points!', colors.darker_green)
                        else:
                            message('You attack ' + target.name + ' for ' + str(damage) + ' hit points.', colors.dark_green)
                        target.Fighter.takeDamage(damage)
                        weapon = getEquippedInSlot('right hand')
                        if weapon is not None:
                            if weapon.burning:
                                applyBurn(target, chance = 25)
                    
                    else:
                        message('You attack ' + target.name + ' but it has no effect!', colors.grey)
        else:
            if not self.owner.Player:
                message(self.owner.name.capitalize() + ' missed you!', colors.white)
            else:
                message('You missed ' + target.name + '!', colors.grey)
        
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.maxHP:
            self.hp = self.maxHP

class BasicMonster: #Basic monsters' AI
    def takeTurn(self):
        monster = self.owner
        if (monster.x, monster.y) in visibleTiles and not monster.Fighter.frozen: #chasing the player
            if monster.distanceTo(player) >= 2:
                monster.moveAstar(player.x, player.y)
            elif player.Fighter.hp > 0 and not monster.Fighter.frozen:
                monster.Fighter.attack(player)
        else:
            if not monster.Fighter.frozen:
                monster.move(randint(-1, 1), randint(-1, 1)) #wandering

class SplosionAI:
    def takeTurn(self):
        monster = self.owner
        if (monster.x, monster.y) in visibleTiles: #chasing the player
            if monster.distanceTo(player) >= 3:
                monster.moveTowards(player.x, player.y)
            elif player.Fighter.hp > 0 and not monster.Fighter.frozen:
                monsterArmageddon(monster.name, monster.x, monster.y)
        else:
            monster.move(randint(-1, 1), randint(-1, 1))

class ConfusedMonster:
    def __init__(self, old_AI, numberTurns=CONFUSE_NUMBER_TURNS):
        self.old_AI = old_AI
        self.numberTurns = numberTurns
 
    def takeTurn(self):
        if self.numberTurns > 0:  
            self.owner.move(randint(-1, 1), randint(-1, 1))
            self.numberTurns -= 1
 
        else:
            self.owner.AI = self.old_AI
            message('The ' + self.owner.name + ' is no longer confused!', colors.red)

class Player:
    def __init__(self, actualPerSkills, levelUpStats, skillsBonus):
        self.actualPerSkills = actualPerSkills
        self.levelUpStats = levelUpStats
        self.skillsBonus = skillsBonus
        if DEBUG:
            print('Player component initialized')
        
    def changeColor(self):
        self.hpRatio = ((self.owner.Fighter.hp / self.owner.Fighter.maxHP) * 100)
        if self.hpRatio < 95 and self.hpRatio >= 75:
            self.owner.color = (120, 255, 0)
        elif self.hpRatio < 75 and self.hpRatio >= 50:
            self.owner.color = (255, 255, 0)
        elif self.hpRatio < 50 and self.hpRatio >= 25:
            self.owner.color = (255, 120, 0)
        elif self.hpRatio < 25 and self.hpRatio > 0:
            self.owner.color = (255, 0, 0)
        elif self.hpRatio == 0:
            self.owner.color = (120, 0, 0)

class Item:
    def __init__(self, useFunction = None,  arg1 = None, arg2 = None, arg3 = None):
        self.useFunction = useFunction
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def pickUp(self):
        if len(inventory)>=26:
            message('Your bag already feels really heavy, you cannot pick up ' + self.owner.name + '.', colors.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', colors.green)
            equipment = self.owner.Equipment
            if equipment and getEquippedInSlot(equipment.slot) is None:
                equipment.equip()

    def use(self):
        if self.owner.Equipment:
            self.owner.Equipment.toggleEquip()
            return
        if self.useFunction is None:
            message('The' + self.owner.name + 'cannot be used !')
            return 'cancelled'
        else:
            if self.arg1 is None:
                if self.useFunction() != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg2 is None and self.arg1 is not None:
                if self.useFunction(self.arg1) != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg3 is None and self.arg2 is not None:
                if self.useFunction(self.arg1, self.arg2) != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
            elif self.arg3 is not None:
                if self.useFunction(self.arg1, self.arg2, self.arg3) != 'cancelled':
                    inventory.remove(self.owner)
                else:
                    return 'cancelled'
                
    def drop(self):
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', colors.yellow)
        if self.owner.Equipment:
            self.owner.Equipment.unequip()
            
def moveOrAttack(dx, dy):
    global FOV_recompute
    x = player.x + dx
    y = player.y + dy
    
    target = None
    for object in objects:
        if object != player:
            if object.Fighter and object.x == x and object.y == y:
                target = object
                break #Since we found the target, there's no point in continuing to search for it
    
    if target is not None:
        player.Fighter.attack(target)
    else:
        player.move(dx, dy)

def checkLevelUp():
    global FOV_recompute
    levelUp_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.Fighter.xp >= levelUp_xp:
        player.level += 1
        player.Fighter.xp -= levelUp_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', colors.yellow)
        
        #applying Class specific stat boosts
        player.Fighter.basePower += player.Player.levelUpStats[0]
        player.Fighter.baseAccuracy += player.Player.levelUpStats[1]
        player.Fighter.baseEvasion += player.Player.levelUpStats[2]
        player.Fighter.baseArmor += player.Player.levelUpStats[3]
        player.Fighter.baseMaxHP += player.Player.levelUpStats[4]
        player.Fighter.hp += player.Player.levelUpStats[4]
        player.Fighter.baseMaxMP += player.Player.levelUpStats[5]
        player.Fighter.MP += player.Player.levelUpStats[5]
        player.Fighter.baseCritical += player.Player.levelUpStats[6]
        
        choice = None
        while choice == None:
            choice = menu('Level up! Choose a skill to raise: \n',
                ['Light Weapons (from ' + str(player.Player.actualPerSkills[0]) + ')',
                 'Heavy Weapons (from ' + str(player.Player.actualPerSkills[1]) + ')',
                 'Missile Weapons (from ' + str(player.Player.actualPerSkills[2]) + ')',
                 'Throwing Weapons (from ' + str(player.Player.actualPerSkills[3]) + ')',
                 'Magic (from ' + str(player.Player.actualPerSkills[4]) + ')',
                 'Armor wielding (from ' + str(player.Player.actualPerSkills[5]) + ')',
                 'Athletics (from ' + str(player.Player.actualPerSkills[6]) + ')',
                 'Concentration (from ' + str(player.Player.actualPerSkills[7]) + ')',
                 'Dodge (from ' + str(player.Player.actualPerSkills[8]) + ')',
                 'Critical (from ' + str(player.Player.actualPerSkills[9]) + ')',
                 'Accuracy (from ' + str(player.Player.actualPerSkills[10]) + ')',], LEVEL_SCREEN_WIDTH)
            if choice != None:
                if player.Player.actualPerSkills[choice] < 5:
                    player.Fighter.basePower += skillsBonus[choice][0]
                    player.Fighter.baseAccuracy += skillsBonus[choice][1]
                    player.Fighter.baseEvasion += skillsBonus[choice][2]
                    player.Fighter.baseArmor += skillsBonus[choice][3]
                    player.Fighter.baseMaxHP += skillsBonus[choice][4]
                    player.Fighter.hp += skillsBonus[choice][4]
                    player.Fighter.baseMaxMP += skillsBonus[choice][5]
                    player.Fighter.MP += skillsBonus[choice][5]
                    player.Fighter.baseCritical += skillsBonus[choice][6]

                    player.Player.actualPerSkills[choice] += 1
                    
                    FOV_recompute = True
                    Update()
                    break

                elif player.Player.actualPerSkills[choice] >= 5:
                    choice = None
            