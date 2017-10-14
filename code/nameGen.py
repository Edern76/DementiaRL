from random import randint
from code.constants import *

'''
Relatively nice sounding names list:
Pukil
Ayeth
Eiela
Lunace
'''
def humanLike(length = randint(6, 12)):
    #Generates pronouncable, human sounding like names (in theory)
    finalName = []
    limitedLetters = {'k' : 0, 'x' : 0, 'w' : 0, 'z' : 0}
    for loop in range(length):
        allowedLetters = []
        extrasAllowed = []
        if loop == 0:
            letterToAdd = alphabet[randint(0, len(alphabet)-1)]
        else:
            previousChar = finalName[loop - 1]
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
                if (not loop - 1 == 0) and (finalName[loop-2] != "s"): #We don't want our name starting with a double "s", nor having any triple "s"
                    extrasAllowed = ["s"]
                    allowedLetters.extend(extrasAllowed)
                    allowedLetters.extend(vowels)
                else:
                    allowedLetters.extend(vowels)
            elif previousChar == "y":
                extrasAllowed = list(vowels) #SUPER IMPORTANT : ALWAYS use newList = list(listToCopy) instead of newList = listToCopy. The latter makes that newList is just a reference to listToCopy, so that any changes made to newList are made to listToCopy too, whereas the former actually creates a new independant list. If the list contains objects from custom classes, use copy.deepcopy(listToCopy) instead (you need to import the copy module before)
                extrasAllowed.remove("y")
                extrasAllowed.extend(consonants)
                extrasAllowed.remove("h")
                allowedLetters = extrasAllowed
            elif previousChar == "e" or previousChar == "a":
                extrasAllowed = ["i"]
                allowedLetters.extend(extrasAllowed)
                allowedLetters.extend(consonants)
            elif previousChar == "o":
                extrasAllowed = ["u", "i", "a", "y"] #Allowing "y" here might produce some exotic results. Unless it really produces unpronouncable stuff, I think it is okay to let it in but YMMV.
                allowedLetters.extend(extrasAllowed)
                allowedLetters.extend(consonants)
            elif previousChar == "i":
                extrasAllowed = ["a", "e", "o"] #Not sure about "e" here. "a" should definitely be in there and I'm pretty confident about "o"
                allowedLetters.extend(extrasAllowed)
                allowedLetters.extend(consonants)
            elif previousChar in vowels:
                allowedLetters = list(consonants)
            elif previousChar in consonants:
                allowedLetters = list(vowels)
                
            if limitedLetters["k"] >= K_LIMIT and "k" in allowedLetters:
                allowedLetters.remove("k")
            if limitedLetters["x"] >= X_LIMIT and "x" in allowedLetters:
                allowedLetters.remove("x")
            if limitedLetters["w"] >= W_LIMIT and "w" in allowedLetters:
                allowedLetters.remove("w")
            if limitedLetters["z"] >= Z_LIMIT and "z" in allowedLetters:
                allowedLetters.remove("z")
            
            if len(allowedLetters) > 1:
                letterToAdd = allowedLetters[randint(0, len(allowedLetters) - 1)]
            elif len(allowedLetters) != 0:
                letterToAdd = allowedLetters[0]
            else:
                print("Alphabet : ", alphabet, ", vowels : ", vowels, ", consonnants : ", consonants, ", finalName : ", finalName)
        
        if letterToAdd in limitedLetters:
            limitedLetters[letterToAdd] += 1
        
        finalName.append(letterToAdd)
    
    finalNameString = "".join(finalName).capitalize()
    return finalNameString

def nemesisSuffix(race, classe):
    choice = randint(0, 3)
    finalSuffix = []
    finalSuffix.extend(' the ')
    if not choice: #class 
        finalSuffix.extend(classe + ' ')
    else:
        finalSuffix.extend(race + ' ')
    finalSuffix.extend(killerSyn[randint(0, len(killerSyn) - 1)])
    finalSuffixString = "".join(finalSuffix)
    return finalSuffixString

def nemesisName(human = True, race = 'human', classe = 'knight'):
    name = ""
    if human:
        name += humanLike(randint(4, 10))
    name += nemesisSuffix(race, classe)
    return name

if __name__ == "__main__":
    for loop in range(10):
        print(nemesisName())
            