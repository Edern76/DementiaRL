import colors
class Branch:
    def __init__(self, shortName, name = None, maxDepth = 99999, branchesFrom = None, branchesTo = None, lightStairsColor = colors.white, darkStairsColor = colors.dark_gray):
        """
        A branch of the dungeon. Please note that the main dugneon is also considered as a branch.
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


mainDungeon = Branch(name = "Main", branchesTo = None, shortName = "main")
gluttonyDungeon = Branch(name = "Gluttony Dungeon", maxDepth = 5, branchesFrom = (mainDungeon, 1), shortName = "glutt", lightStairsColor = colors.desaturated_chartreuse, darkStairsColor = colors.darkest_chartreuse)

mainDungeon.branchesTo.append((gluttonyDungeon, 1))
    