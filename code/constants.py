from math import *
from random import randint
import colors

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


FIRECAMP_TILES = {(0, 0): {'char': chr(15), 'fg': colors.orange, 'bg': colors.darker_grey, 'dark_fg': colors.darker_orange, 'dark_bg': colors.darkest_grey},
                  (1, 0): {'char': chr(254), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey},
                  (0, 1): {'char': chr(254), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey},
                  (-1, 0): {'char': chr(254), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey},
                  (0, -1): {'char': chr(254), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey},
                  (1, 1): {'char': chr(226), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey},
                  (1, -1): {'char': chr(232), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey},
                  (-1, 1): {'char': chr(227), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey},
                  (-1, -1): {'char': chr(229), 'fg': colors.light_grey, 'bg': colors.darker_grey, 'dark_fg': colors.dark_grey, 'dark_bg': colors.darkest_grey}}

SLEEP_REGEN = .5 #regenerate .5*vit % of health when sleeping 1 turn

def exponentialProgress(level, levelDivisor=8):
    return (exp(level/levelDivisor)-exp(1/levelDivisor))/100

def sigmoidProgress(level, startSlowness = 50, increaseSlowness = 30):
    c = 100*exp((1-startSlowness)/increaseSlowness)
    return (((100+c)/(1+exp(-(level-startSlowness)/increaseSlowness))) - c)/100



if __name__ == '__main__':
    for i in range(10):
        level = i*10
        test = 15 + randint(level//2, level//2 + level)
        sigmo = sigmoidProgress(level)
        sigmoTest = test + round(test*sigmo)
        print(level, test, sigmo, sigmoTest)





