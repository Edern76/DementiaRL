from math import *

alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", 'x', "y", "z"]

vowels = ["a", "e", "i", "o", "u", "y"]
consonants = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "z"]

killerSyn = ['slayer', 'bane', 'killer', 'butcher', 'executioner', 'exterminator', 'assassin', 'liquidator', 'annihilator', 'destructor', 'headhunter', 'torturer', 'massacrer']

K_LIMIT = 2
W_LIMIT = 1
X_LIMIT = 1
Z_LIMIT = 1

MAX_HIGH_CULTIST_MINIONS = 2

DIAL_TEXT_START = 30
DIAL_TEXT_WIDTH = 170 - int(DIAL_TEXT_START) * 2

ACTION_COSTS = {'Drop': 50, 'Equip': 150, 'Eat': 25, 'Drink': 25, 'Read': 50, 'Pick Up': 25, 'Unequip': 150}
WATER_WALK_COST = 50

def exponentialProgress(level, levelDivisor=8):
    return (exp(level/levelDivisor)-exp(1/levelDivisor))/100

def sigmoidProgress(level, startSlowness = 50, increaseSlowness = 30):
    c = 100*exp((1-startSlowness)/increaseSlowness)
    return (((100+c)/(1+exp(-(level-startSlowness)/increaseSlowness))) - c)/100