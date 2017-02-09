import colors

class Branch:
    def __init__(self, name, maxDepth = 99999, branchesFrom = None, branchesTo = None, stairsColor = colors.white):
        self.name = name
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
        self.stairsColor = stairsColor


mainDungeon = Branch("Main", branchesTo = None)
gluttonyDungeon = Branch("Gluttony Dungeon", maxDepth = 5, branchesFrom = (mainDungeon, 1))

mainDungeon.branchesTo.append((gluttonyDungeon, 1))
    