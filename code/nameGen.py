from random import randint
from constants import *


def humanLike(length = randint(6, 12)):
    #Generates pronouncable, human sounding like names (in theory)
    finalName = []
    for loop in range(length):
        if loop == 0:
            finalName[loop] = alphabet[randint(0, len(alphabet)-1)]
        else:
            previousChar = finalName[loop - 1]
            allowedLetters = []
            if previousChar == "c":
                extrasAllowed = ["h", "r", "l"]
                allowedLetters.extend(extrasAllowed)
                allowedLetters.extend(vowels)
            elif previousChar == "g":
                extrasAllowed = ["r", "l"]
                allowedLetters.extend(extrasAllowed)
                allowedLetters.extend(vowels)
            elif previousChar == "k":
                extrasAllowed = ["r"]
                allowedLetters.extend(extrasAllowed)
                allowedLetters.extend(vowels)
            elif previousChar == "s":
                if (not loop - 1 == 0) and (finalName[loop-2] != "s"):
                    extrasAllowed = ["s"]
                    allowedLetters.extend(extrasAllowed)
                allowedLetters.extend(vowels)
            
#WIP