class UnusableMethodException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message
    

class IllegalTileInvasion(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        warningToPrint = ("A room cannot claim a tile that doesn't belong to it. \n")
        finalMessage = warningToPrint + self.message
        return finalMessage