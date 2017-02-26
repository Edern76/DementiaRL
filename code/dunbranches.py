import colors
class Branch:
    def __init__(self, shortName, name = None, maxDepth = 99999, branchesFrom = None, branchesTo = None, lightStairsColor = colors.white, darkStairsColor = colors.dark_gray,
                 monsterChances = {'darksoul': 600, 'troll': 200, 'snake': 50, 'cultist': 150}, itemChances = {'potion': 350, 'scroll': 260, 'weapon': 70, 'shield': 70, 'spellbook': 70, 'food': 180},
                 potionChances = {'heal': 70, 'mana': 30}, spellbookChances = {'healSelf': 8, 'fireball': 30, 'lightning': 13, 'confuse': 22, 'ice': 22},
                 scrollChances = {'lightning': 12, 'confuse': 12, 'fireball': 25, 'armageddon': 10, 'ice': 25, 'none': 1}, weaponChances = {'sword': 25, 'axe': 25, 'hammer': 25, 'mace': 25},
                 color_dark_wall = colors.darkest_grey, color_light_wall = colors.darker_grey, color_dark_ground = colors.darkest_sepia, color_dark_gravel = (27, 20, 0),
                 color_light_ground = colors.darker_sepia, color_light_gravel = (50, 37, 0), bossLevels = [3, 6], bossNames = {'High Inquisitor': 3, 'Gluttony': 6}):
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
        self.color_dark_wall = color_dark_wall
        self.color_light_wall = color_light_wall
        self.color_dark_ground = color_dark_ground
        self.color_dark_gravel = color_dark_gravel
        self.color_light_ground = color_light_ground
        self.color_light_gravel = color_light_gravel
        self.bossLevels = bossLevels
        self.bossNames = bossNames

mainDungeon = Branch(name = "Main", branchesTo = None, shortName = "main")
gluttonyDungeon = Branch(name = "Gluttony Dungeon", maxDepth = 5, branchesFrom = (mainDungeon, 1), shortName = "glutt", lightStairsColor = colors.desaturated_chartreuse, darkStairsColor = colors.darkest_chartreuse, itemChances = {'potion': 360, 'scroll': 20, 'weapon': 20, 'shield': 100, 'food': 500}, bossLevels = [5], bossNames = {'Gluttony': 5})

mainDungeon.branchesTo.append((gluttonyDungeon, 1))
    