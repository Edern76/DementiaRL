import colors

branches = []

class Branch:
    def __init__(self, shortName, name = None, maxDepth = 99999, branchesFrom = None, branchesTo = None, lightStairsColor = colors.white, darkStairsColor = colors.dark_gray,
                 monsterChances = {'darksoul': 600, 'ogre': 200, 'snake': 50, 'cultist': 150, 'highCultist' : 0}, 
                 itemChances = {'potion': 350, 'scroll': 260, 'weapon': 70, 'shield': 70, 'spellbook': 70, 'food': 180},
                 potionChances = {'heal': 70, 'mana': 30}, 
                 spellbookChances = {'healSelf': 8, 'fireball': 30, 'lightning': 13, 'confuse': 22, 'ice': 22},
                 scrollChances = {'lightning': 12, 'confuse': 12, 'fireball': 25, 'armageddon': 10, 'ice': 25, 'none': 1}, 
                 weaponChances = {'sword': 25, 'axe': 25, 'hammer': 25, 'mace': 25},
                 foodChances = {'bread' : 500, 'herbs' : 501, 'rMeat' : 300, 'pie' : 200, 'pasta' : 200, 'meat' : 100, 'hBaguette' : 10}, # TO-DO : Add dumb stuff here with very low chances of spawning (maybe more on Gluttony's branch ?) and dumb effects, aka easter eggs.
                 color_dark_wall = colors.darkest_grey, color_light_wall = colors.darker_grey, color_dark_ground = colors.darkest_sepia, color_dark_gravel = (27, 20, 0),
                 color_light_ground = colors.darker_sepia, color_light_gravel = (50, 37, 0), bossLevels = [3, 6], bossNames = {'High Inquisitor': 3, 'Gluttony': 6}, fixedMap = None, genType = 'dungeon', genFeatures = ['chasms'],
                 maxRooms = 30, roomMinSize = 6, roomMaxSize = 15):
        """
        A branch of the dungeon. Please note that the main dungeon is also considered as a branch.
        @type shortName: str
        @param shortName: Abbreviated name of the branch, used in save file naming.
        """
        self.name = name
        self.shortName = shortName
        print("shortName = ", shortName)
        self.maxDepth = maxDepth
        if branchesFrom is not None:
            (self.origBranch, self.origDepth) = branchesFrom
        else:
            (self.origBranch, self.origDepth) = None, None
        self.branchesTo = []
        if branchesTo is not None:
            for (branch, depth) in branchesTo:
                if depth <= self.maxDepth:
                    self.branchesTo.append((branch, depth))
                else:
                    raise ValueError("Depth of branch greater than max depth.")
        self.lightStairsColor = lightStairsColor
        self.darkStairsColor = darkStairsColor
        self.monsterChances = monsterChances
        self.itemChances = itemChances
        self.potionChances = potionChances
        self.scrollChances = scrollChances
        self.spellbookChances = spellbookChances
        self.weaponChances = weaponChances
        self.foodChances = foodChances
        self.color_dark_wall = color_dark_wall
        self.color_light_wall = color_light_wall
        self.color_dark_ground = color_dark_ground
        self.color_dark_gravel = color_dark_gravel
        self.color_light_ground = color_light_ground
        self.color_light_gravel = color_light_gravel
        self.bossLevels = bossLevels
        self.bossNames = bossNames
        self.fixedMap = fixedMap
        self.genType = genType
        self.genFeatures = genFeatures
        self.appeared = False
        self.maxRooms = maxRooms
        self.roomMinSize = roomMinSize
        self.roomMaxSize = roomMaxSize
        
        branches.append(self)

mainDungeon = Branch(shortName = "main", name = "Main", branchesTo = None)
gluttonyDungeon = Branch(shortName = "glutt", name = "Gluttony Dungeon", maxDepth = 5, branchesFrom = (mainDungeon, 1), lightStairsColor = colors.desaturated_chartreuse, darkStairsColor = colors.darkest_chartreuse, monsterChances = {'darksoul': 400, 'ogre': 200, 'starveling': 250, 'cultist': 150}, itemChances = {'potion': 360, 'scroll': 20, 'weapon': 20, 'shield': 100, 'food': 500}, bossLevels = [5], bossNames = {'Gluttony': 5})
hiddenTown = Branch(shortName = 'town',name = "Hidden Refuge", maxDepth = 1, branchesFrom = (mainDungeon, 1),lightStairsColor = colors.azure, darkStairsColor = colors.darker_azure, fixedMap = 'town')
greedDungeon = Branch(shortName = 'greed', name = 'Greed Cavern', maxDepth = 5, branchesFrom= (mainDungeon, 2), lightStairsColor = colors.yellow, darkStairsColor = colors.darker_yellow, genType = 'cave', monsterChances = {'darksoul': 400, 'ogre': 100, 'snake': 10, 'cultist': 150, 'greedyFiend' : 200}, color_light_wall = colors.darker_yellow, color_dark_wall = colors.darkest_yellow, color_light_ground = colors.darker_sepia, color_dark_ground = colors.darkest_sepia, itemChances = {'potion': 100, 'scroll': 150, 'weapon': 50, 'shield': 50, 'food': 90, 'money' : 300}, genFeatures = ['mines'])
wrathDungeon = Branch(shortName = "wrath", name = "Wrath Lair", maxDepth = 5, branchesFrom = (mainDungeon, 2), lightStairsColor = colors.dark_red, darkStairsColor = colors.darkest_red, monsterChances = {'darksoul': 400, 'ogre': 400, 'cultist': 200}, itemChances = {'potion': 360, 'scroll': 20, 'weapon': 400, 'shield': 20, 'food': 200}, bossLevels = [5], bossNames = {'Wrath': 5}, genFeatures = ['holes'])
temple = Branch(shortName='temple', name = 'The Temple', maxDepth=5, branchesFrom=(mainDungeon, 4), lightStairsColor = colors.han, darkStairsColor = colors.darker_han, monsterChances = {'darksoul': 300, 'ogre': 200, 'snake': 50, 'cultist': 450}, itemChances = {'potion': 320, 'scroll': 360, 'weapon': 50, 'shield': 20, 'spellbook': 100, 'food': 150}, genFeatures = ['temple'], color_light_wall = colors.lighter_grey, color_dark_wall = colors.dark_grey, color_light_ground = colors.grey, color_dark_ground = colors.darker_grey, color_light_gravel = (140, 140, 140), color_dark_gravel = (76, 76, 76), roomMinSize = 10, roomMaxSize = 20)

mainDungeon.branchesTo.append((gluttonyDungeon, 1))
mainDungeon.branchesTo.append((hiddenTown, 1))
mainDungeon.branchesTo.append((greedDungeon, 2))
mainDungeon.branchesTo.append((wrathDungeon, 2))
mainDungeon.branchesTo.append((temple, 4))

def reinitializeBranches():
    for branch in branches:
        print("Reinitializing {}".format(branch.name))
        branch.appeared = False
    