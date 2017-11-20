import colors

branches = []

branchMapTemplate = {'wallFG': colors.grey, 'wallDarkFG': colors.darker_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.sepia, 'groundDarkBG': colors.darker_sepia,
                     'gravelFG': (50, 37, 0), 'gravelDarkFG': (27, 20, 0), 'gravelChars': [chr(176), chr(177)],
                     'stairsColor': colors.white, 'stairsDarkColor': colors.dark_grey,
                     'chasm': True, 'chasmColor': (0, 0, 16),
                     'dungeon': True, 'caves': False,
                     'mines': False, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': False, 'pillarChar': 'o', 'pillarColor': colors.darker_grey, 'pillarDarkColor': (16, 16, 16),
                     'holes': False,
                     'doors': True, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darkest_flame,
                     'fixedMap': None}

class Branch:
    def __init__(self, shortName, name = None, maxDepth = 99999, branchesFrom = None, branchesTo = None,
                 monsterChances = {'darksoul': 600, 'ogre': 200, 'snake': 50, 'cultist': 150, 'highCultist' : 0}, 
                 itemChances = {'potion': 150, 'scroll': 200, 'weapon': 100, 'shield': 50, 'spellbook': 100, 'food': 250, 'armor': 150},
                 potionChances = {'heal': 70, 'mana': 30}, 
                 spellbookChances = {'healSelf': 8, 'fireball': 30, 'lightning': 13, 'confuse': 22, 'ice': 22},
                 scrollChances = {'lightning': 12, 'confuse': 12, 'fireball': 25, 'armageddon': 10, 'ice': 25, 'none': 1}, 
                 #weaponChances = {'sword': 25, 'axe': 25, 'hammer': 25, 'mace': 25},
                 foodChances = {'bread' : 500, 'herbs' : 501, 'rMeat' : 300, 'pie' : 200, 'pasta' : 200, 'meat' : 100, 'hBaguette' : 10}, # TO-DO : Add dumb stuff here with very low chances of spawning (maybe more on Gluttony's branch ?) and dumb effects, aka easter eggs.
                 bossLevels = [], bossNames = {}, #bossLevels = [3, 6], bossNames = {'High Inquisitor': 3, 'Gluttony': 6},
                 maxRooms = 12, roomMinSize = 6, roomMaxSize = 15, maxTunWidth = 2, sightMalus = 0,
                 mapGeneration = branchMapTemplate):
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
        self.monsterChances = monsterChances
        self.itemChances = itemChances
        self.potionChances = potionChances
        self.scrollChances = scrollChances
        self.spellbookChances = spellbookChances
        #self.weaponChances = weaponChances
        self.foodChances = foodChances
        self.bossLevels = bossLevels
        self.bossNames = bossNames
        self.mapGeneration = mapGeneration
        self.appeared = False
        self.maxRooms = maxRooms
        self.roomMinSize = roomMinSize
        self.roomMaxSize = roomMaxSize
        self.maxTunWidth = maxTunWidth
        self.sightMalus = sightMalus
        
        branches.append(self)

mainDungeon = Branch(shortName = "main", name = "Main", branchesTo = None)

gluttMapTemplate = {'wallFG': colors.grey, 'wallDarkFG': colors.darker_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.sepia, 'groundDarkBG': colors.darker_sepia,
                     'gravelFG': (50, 37, 0), 'gravelDarkFG': (27, 20, 0), 'gravelChars': [chr(176), chr(177)],
                     'stairsColor': colors.desaturated_chartreuse, 'stairsDarkColor': colors.darkest_chartreuse,
                     'chasm': True, 'chasmColor': (0, 0, 16),
                     'dungeon': True, 'caves': False,
                     'mines': False, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': False, 'pillarChar': 'o', 'pillarColor': colors.grey, 'pillarDarkColor': colors.darker_grey,
                     'holes': False,
                     'doors': True, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darker_flame,
                     'fixedMap': None}

gluttonyDungeon = Branch(shortName = "glutt", name = "Gluttony Dungeon", maxDepth = 5, branchesFrom = (mainDungeon, 1), monsterChances = {'darksoul': 400, 'ogre': 200, 'starveling': 250, 'cultist': 150}, itemChances = {'potion': 340, 'scroll': 20, 'weapon': 20, 'armor': 100, 'food': 450, 'shield': 70}, bossLevels = [5], bossNames = {'Gluttony': 5}, mapGeneration = gluttMapTemplate)

townMapTemplate = {'wallFG': colors.grey, 'wallDarkFG': colors.darker_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.sepia, 'groundDarkBG': colors.darker_sepia,
                     'gravelFG': (50, 37, 0), 'gravelDarkFG': (27, 20, 0), 'gravelChars': [chr(176), chr(177)],
                     'stairsColor': colors.azure, 'stairsDarkColor': colors.darker_azure,
                     'chasm': True, 'chasmColor': (0, 0, 16),
                     'dungeon': True, 'caves': False,
                     'mines': False, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': False, 'pillarChar': 'o', 'pillarColor': colors.grey, 'pillarDarkColor': colors.darker_grey,
                     'holes': False,
                     'doors': True, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darker_flame,
                     'fixedMap': 'town'}

hiddenTown = Branch(shortName = 'town',name = "Hidden Refuge", maxDepth = 1, branchesFrom = (mainDungeon, 1), mapGeneration = townMapTemplate)

greedMapTemplate = {'wallFG': colors.grey, 'wallDarkFG': colors.darker_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.sepia, 'groundDarkBG': colors.darker_sepia,
                     'gravelFG': (50, 37, 0), 'gravelDarkFG': (27, 20, 0), 'gravelChars': [chr(176), chr(177)],
                     'stairsColor': colors.yellow, 'stairsDarkColor': colors.darker_yellow,
                     'chasm': False, 'chasmColor': (0, 0, 16),
                     'dungeon': False, 'caves': False,
                     'mines': True, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': False, 'pillarChar': chr(254), 'pillarColor': colors.darkest_sepia, 'pillarDarkColor': (14, 11, 7),
                     'holes': False,
                     'doors': False, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darker_flame,
                     'fixedMap': None}

greedDungeon = Branch(shortName = 'greed', name = 'Greed Mines', maxDepth = 5, branchesFrom= (mainDungeon, 2), monsterChances = {'darksoul': 400, 'ogre': 100, 'snake': 10, 'cultist': 150, 'greedyFiend' : 200}, itemChances = {'potion': 100, 'scroll': 100, 'weapon': 50, 'shield': 50, 'food': 90, 'money' : 300, 'armor': 50}, mapGeneration = greedMapTemplate)

wrathMapTemplate = {'wallFG': colors.grey, 'wallDarkFG': colors.darker_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.sepia, 'groundDarkBG': colors.darker_sepia,
                     'gravelFG': (50, 37, 0), 'gravelDarkFG': (27, 20, 0), 'gravelChars': [chr(176), chr(177)],
                     'stairsColor': colors.dark_red, 'stairsDarkColor': colors.darkest_red,
                     'chasm': True, 'chasmColor': (0, 0, 16),
                     'dungeon': True, 'caves': False,
                     'mines': False, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': False, 'pillarChar': 'o', 'pillarColor': colors.grey, 'pillarDarkColor': colors.darker_grey,
                     'holes': True,
                     'doors': True, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darker_flame,
                     'fixedMap': None}

wrathDungeon = Branch(shortName = "wrath", name = "Wrath Ruins", maxDepth = 5, branchesFrom = (mainDungeon, 2), monsterChances = {'darksoul': 400, 'ogre': 400, 'cultist': 200}, itemChances = {'potion': 310, 'scroll': 20, 'weapon': 400, 'shield': 20, 'food': 200, 'armor': 50}, bossLevels = [5], bossNames = {'Wrath': 5}, mapGeneration = wrathMapTemplate)

templeMapTemplate = {'wallFG': colors.light_grey, 'wallDarkFG': colors.dark_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.dark_grey, 'groundDarkBG': colors.darkest_grey,
                     'gravelFG': (140, 140, 140), 'gravelDarkFG': (76, 76, 76), 'gravelChars': [chr(254), chr(250)],
                     'stairsColor': colors.han, 'stairsDarkColor': colors.darker_han,
                     'chasm': True, 'chasmColor': (0, 0, 16),
                     'dungeon': True, 'caves': False,
                     'mines': False, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': True, 'pillarChar': 'o', 'pillarColor': colors.light_grey, 'pillarDarkColor': colors.dark_grey,
                     'holes': False,
                     'doors': True, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darkest_flame,
                     'fixedMap': None}

temple = Branch(shortName='temple', name = 'The Temple', maxDepth=5, branchesFrom=(mainDungeon, 4), monsterChances = {'darksoul': 300, 'ogre': 200, 'snake': 50, 'cultist': 450}, itemChances = {'potion': 320, 'scroll': 360, 'weapon': 50, 'shield': 20, 'spellbook': 100, 'food': 150}, roomMinSize = 10, roomMaxSize = 20, mapGeneration = templeMapTemplate)

lustMapTemplate = {'wallFG': colors.grey, 'wallDarkFG': colors.darker_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.sepia, 'groundDarkBG': colors.darker_sepia,
                     'gravelFG': (50, 37, 0), 'gravelDarkFG': (27, 20, 0), 'gravelChars': [chr(254), chr(250)],
                     'stairsColor': colors.darker_fuchsia, 'stairsDarkColor': colors.darkest_fuchsia,
                     'chasm': False, 'chasmColor': (0, 0, 16),
                     'dungeon': True, 'caves': False,
                     'mines': False, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': False, 'pillarChar': 'o', 'pillarColor': colors.grey, 'pillarDarkColor': colors.darker_grey,
                     'holes': False,
                     'doors': True, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darker_flame,
                     'fixedMap': None}

lustDungeon = Branch(shortName = "lust", name = "Lust Tunnels", maxDepth = 5, branchesFrom = (mainDungeon, 1), maxRooms = 22, roomMinSize = 5, roomMaxSize = 12, maxTunWidth = 0, sightMalus = 11, mapGeneration = lustMapTemplate)

shrineMapTemplate = {'wallFG': colors.light_grey, 'wallDarkFG': colors.dark_grey, 'wallBG': colors.darker_grey, 'wallDarkBG': (16, 16, 16), 'wallChar': '#',
                     'groundBG': colors.dark_grey, 'groundDarkBG': colors.darkest_grey,
                     'gravelFG': (140, 140, 140), 'gravelDarkFG': (76, 76, 76), 'gravelChars': [chr(254), chr(250)],
                     'stairsColor': colors.han, 'stairsDarkColor': colors.darker_han,
                     'chasm': True, 'chasmColor': (0, 0, 16),
                     'dungeon': True, 'caves': False,
                     'mines': False, 'mineWallFG': colors.dark_sepia, 'mineWallDarkFG': colors.darkest_sepia, 'mineWallBG': colors.darkest_sepia, 'mineWallDarkBG': (14, 11, 7),
                     'pillars': True, 'pillarChar': 'o', 'pillarColor': colors.light_grey, 'pillarDarkColor': colors.dark_grey,
                     'holes': False,
                     'doors': True, 'doorChar': '+', 'doorColor': colors.darker_flame, 'doorDarkColor': colors.darkest_flame,
                     'fixedMap': 'shrine'}

shrine = Branch(shortName='shrine', name = 'The Shrine', maxDepth=1, branchesFrom=(temple, 5), monsterChances = {}, itemChances = {}, roomMinSize = 10, roomMaxSize = 20, mapGeneration = shrineMapTemplate)

mainDungeon.branchesTo.append((gluttonyDungeon, 7))
mainDungeon.branchesTo.append((hiddenTown, 1))
mainDungeon.branchesTo.append((greedDungeon, 9))
mainDungeon.branchesTo.append((wrathDungeon, 13))
mainDungeon.branchesTo.append((temple, 4))
mainDungeon.branchesTo.append((lustDungeon, 5))
temple.branchesTo.append((shrine, 5))
shrine.branchesTo.append((mainDungeon, 1))

def reinitializeBranches():
    for branch in branches:
        print("Reinitializing {}".format(branch.name))
        branch.appeared = False

'''
Dungeon map:
                                5        5        5        5        5        5        5
                              Lust    Glutt    Greed    Sloth     Wrath    Envy    Pride
                                |        |        |        |        |        |        |
Main -3- Temple -4- Shrine --- Main -2- Main -2- Main -2- Main -2- Main -2- Main -2- Main -2- ?End?

/!\ add 1 floor to the count here: bosses floor are not counted
'''

def getFloorBranches(branch, floor): # !! floor is the one being generated
    branchList = []
    for br, lvl in branch.branchesTo:
        if lvl == floor:
            branchList.append(br)
    if not ((branch == temple and floor == 5) or (branch == mainDungeon and floor == 4) or floor == branch.maxDepth + 1): #after bosses
        branchList.append(branch)
    
    origBranch = None
    if branch != mainDungeon:
        if branch.origBranch and floor == 1:
            origBranch = branch.origBranch
        else:
            origBranch = branch
    elif floor == 5:
        origBranch = shrine
    elif floor <= 1:
        origBranch = None
    else:
        origBranch = mainDungeon
    return branchList, origBranch

if __name__ == '__main__':
    for i in range(15):
        brList, origBr = getFloorBranches(temple, i)
        try:
            name = origBr.name
        except:
            name = None
        print(i, [branch.name for branch in brList], name)
        
        
        
        
        
