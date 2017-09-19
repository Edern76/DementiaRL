import copy
import code.custom_except
from random import randint
from code.constants import *
import colors
#import code.dunbranches as dBr
from math import *

#GameObject template: x, y, char, name, color, blocks, Fighter, AI, Player, Ghost, flying, Item, alwaysVisible, darkColor, Equipment, pName, Essence,
#                     socialComp, shopComp, questList, Stairs, alwaysAlwaysVisible, size, sizeChar, sizeColor, sizeDarkColor, smallChar, ProjectileComp

#Item template: useFunction, arg1, arg2, arg3, stackable, amount, weight, description, pic, itemtype, identified, unIDName, unIDpName, unIDdesc, useText

#Equipment template: slot, type, powerBonus, armorBonus, maxHP_Bonus, accuracyBonus, evasionBonus, criticalBonus, maxMP_Bonus, strengthBonus, dexterityBonus,
#                    vitalityBonus, willpowerBonus, ranged, rangedPower, maxRange, ammo, meleeWeapon, armorPenetrationBonus, slow, enchant, staminaBonus,
#                    stealthBonus

rarityList = ['junk', 'common', 'uncommon', 'rare', 'epic', 'legendary']

class Rarity:
    def __init__(self, rarity, color):
        self.rarity = rarity
        self.color = color
        self.index = rarityList.index(self.rarity)
    
    def __str__(self):
        return self.rarity
    
    def __eq__(self, string):
        return self.rarity == string
    
    def __ne__(self, string):
        return self.rarity != string
    
    def __lt__(self, string):
        return self.index < rarityList.index(string)
    
    def __le__(self, string):
        return self.index < rarityList.index(string)
    
    def __gt__(self, string):
        return self.index < rarityList.index(string)
    
    def __ge__(self, string):
        return self.index < rarityList.index(string)
    
    def __hash__(self):
        return self.index


junk = Rarity('junk', colors.copper)
common = Rarity('common', colors.silver)
uncommon = Rarity('uncommon', colors.gold)
rare = Rarity('rare', colors.blue)
epic = Rarity('epic', colors.violet)
legendary = Rarity('legendary', colors.orange)

rarity = {junk: 15, common: 50, uncommon: 15, rare: 10, epic: 7, legendary: 1003}
raritySmallAdd = {'junk': -2, 'common': 0, 'uncommon': 2, 'rare': 3, 'epic': 5, 'legendary': 8}
rarityBigAdd = {'junk': -10, 'common': 0, 'uncommon': 10, 'rare': 15, 'epic': 20, 'legendary': 30}

rarityCombo = {'rare': {'2 passive': 15}, 'epic': {'2 passive': 35, '1 active': 35, 'none': 30}, 'legendary': {'3 passive + 1 active': 25, '2 passive + 1 active': 70, '1 active': 5}}
noActiveRarityCombo = {'rare': {'2 passive': 15}, 'epic': {'2 passive': 70, 'none': 30}, 'legendary': {'3 passive': 70, '2 passive': 30}}

itemTypes = ['weapon', 'potion', 'armor', 'shield', 'food', 'scroll', 'spellbook', 'ranged weapon']

### weapons ###
weaponTypes = ['dagger', 'sword', 'axe', 'flail', 'mace', 'hammer', 'gloves', 'spear']

weaponSize = {'dagger': {'dagger': 70, 'stiletto': 15, 'misericorde': 15},
              'sword': {'shortsword': 35, 'longsword': 40, 'katana': 15, 'great sword': 10},
              'axe': {'axe': 85, 'greataxe': 15},
              'flail': {'flail': 85, 'peasant flail': 15},
              'mace': {'mace': 85, 'great mace': 5, 'morning star': 10},
              'hammer': {'warhammer': 85, 'maul': 15},
              'gloves': {'cestus': 85, 'knuckles': 10, 'fighting claws': 5},
              'spear': {'pike': 85, 'halberd': 15}}

weaponDictTemplate = ['pow', 'arm', 'HP', 'acc', 'ev', 'crit', 'MP', 'strength', 'dex', 'vit', 'will', 'ap', 'slow', 'stam', 'stealth']

weaponAttributes = {'dagger': {'type': 'light', 'slot': 'one handed', 'pic': 'dagger.xp', 'pow': 6, 'acc': 15, 'stealth': 7, 'weight': 0.5},
                    'stiletto': {'type': 'light', 'slot': 'one handed', 'pic': 'stiletto.xp', 'pow': 5, 'acc': 20, 'stealth': 10, 'crit': 5, 'weight': 0.5},
                    'misericorde': {'type': 'light', 'slot': 'one handed', 'pic': 'dagger.xp', 'pow': 6, 'acc': 10, 'stealth': 5, 'ap': 1, 'weight': 0.5},
                    
                    'shortsword': {'type': 'light', 'slot': 'one handed', 'pic': 'shortSword.xp', 'pow': 8, 'acc': 5, 'weight': 1.1},
                    'longsword': {'type': 'light', 'slot': 'one handed', 'pic': 'longSword.xp', 'pow': 12, 'weight': 1.9},
                    'katana': {'type': 'light', 'slot': 'one handed', 'pic': 'katana.xp', 'pow': 11, 'ap': 3, 'weight': 1.5},
                    'great sword': {'type': 'heavy', 'slot': 'two handed', 'pic': 'greatSword.xp', 'pow': 18, 'acc': -10, 'weight': 3.5, 'slow': True},
                    
                    'axe': {'type': 'light', 'slot': 'one handed', 'pic': 'axe.xp', 'pow': 9, 'acc': 10, 'weight': 1.3},
                    'greataxe': {'type': 'heavy', 'slot': 'two handed', 'pic': 'greatAxe.xp', 'pow': 20, 'acc': -15, 'weight': 3.3, 'slow': True},
                    
                    'flail': {'type': 'heavy', 'slot': 'one handed', 'pic': 'flail.xp', 'pow': 9, 'ap': 6, 'acc': -5, 'crit': -3, 'weight': 2.4},
                    'peasant flail': {'type': 'heavy', 'slot': 'two handed', 'pic': 'greatFlail.xp', 'pow': 15, 'acc': -25, 'ap': 12, 'weight': 4.2, 'slow': True},
                    
                    'mace': {'type': 'light', 'slot': 'one handed', 'pic': 'mace.xp', 'pow': 8, 'acc': 10, 'ap': 2, 'weight': 1.7},
                    'morning star': {'type': 'light', 'slot': 'one handed', 'pic': 'moringStar.xp', 'pow': 10, 'acc': 5, 'ap': 4, 'weight': 1.8},
                    'great mace': {'type': 'heavy', 'slot': 'two handed', 'pic': 'greatMace.xp', 'pow': 13, 'acc': -10, 'ap': 8, 'weight': 5.0, 'slow': True},
                    
                    'warhammer': {'type': 'heavy', 'slot': 'one handed', 'pic': 'hammer.xp', 'pow': 13, 'crit': 3, 'weight': 1.5},
                    'maul': {'type': 'heavy', 'slot': 'two handed', 'pic': 'greatHammer.xp', 'pow': 19, 'crit': 6, 'weight': 5.7, 'slow': True},
                    
                    'cestus': {'type': 'light', 'slot': 'two handed', 'pic': 'mace.xp', 'pow': 7, 'acc': 15, 'ev': 20, 'crit': -5, 'arm': 2, 'weight': 0.3},
                    'knuckles': {'type': 'light', 'slot': 'two handed', 'pic': 'mace.xp', 'pow': 13, 'acc': 10, 'ev': 15, 'crit': 2, 'weight': 0.7},
                    'fighting claws': {'type': 'light', 'slot': 'two handed', 'pic': 'mace.xp', 'pow': 16, 'acc': 10, 'ev': 25, 'crit': 5, 'weight': 0.6},
                    
                    'pike': {'type': 'light', 'slot': 'one handed', 'pic': 'spear.xp', 'pow': 8, 'acc': 10, 'ev': 10, 'weight': 3.1},
                    'halberd': {'type': 'heavy', 'slot': 'two handed', 'pic': 'halberd.xp', 'pow': 14, 'ap': 2, 'acc': 5, 'weight': 3.9, 'slow': True}
                    }

weaponAdj = {'dagger': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'sharp': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'sharp': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'precise': 12, 'fast': 12, 'sharp': 12, 'discrete': 12}, 
                        'epic': {'precise': 13, 'fast': 13, 'sharp': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'discrete': 13},
                        'legendary': {'deadly': 10, 'precise': 10, 'fast': 10, 'sharp': 10, 'poisoned': 10, 'leech': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'discrete': 10}},
             
             'sword': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'sharp': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'sharp': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'precise': 12, 'fast': 12, 'sharp': 12, 'mighty': 12}, 
                        'epic': {'precise': 13, 'fast': 13, 'sharp': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'mighty': 13},
                        'legendary': {'splash': 10, 'precise': 10, 'fast': 10, 'sharp': 10, 'poisoned': 10, 'leech': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'mighty': 10}},
             
             'axe': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'sharp': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'sharp': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'precise': 12, 'fast': 12, 'sharp': 12, 'mighty': 12}, 
                        'epic': {'precise': 13, 'fast': 13, 'sharp': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'mighty': 13},
                        'legendary': {'splash': 10, 'precise': 10, 'fast': 10, 'sharp': 10, 'poisoned': 10, 'leech': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'mighty': 10}},
             
             'flail': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'weighed': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'weighed': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'two-headed': 12, 'fast': 12, 'weighed': 12, 'mighty': 12}, 
                        'epic': {'two-headed': 13, 'fast': 13, 'weighed': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'mighty': 13},
                        'legendary': {'splash': 9, 'two-headed': 9, 'fast': 9, 'weighed': 9, 'poisoned': 9, 'stunning': 9, 'burning': 9, 'frost': 9, 'electric': 9, 'mighty': 9, 'three-headed': 9}},
             
             'mace': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'weighed': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'weighed': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'precise': 12, 'fast': 12, 'weighed': 12, 'mighty': 12}, 
                        'epic': {'precise': 13, 'fast': 13, 'weighed': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'mighty': 13},
                        'legendary': {'splash': 10, 'precise': 10, 'fast': 10, 'weighed': 10, 'poisoned': 10, 'stunning': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'mighty': 10}},
             
             'hammer': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'weighed': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'weighed': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'spiked': 12, 'fast': 12, 'weighed': 12, 'mighty': 12}, 
                        'epic': {'spiked': 13, 'fast': 13, 'weighed': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'mighty': 13},
                        'legendary': {'splash': 10, 'spiked': 10, 'fast': 10, 'weighed': 10, 'poisoned': 10, 'stunning': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'mighty': 10}},
             
             'gloves': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'weighed': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'weighed': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'precise': 12, 'fast': 12, 'weighed': 12, 'mighty': 12}, 
                        'epic': {'precise': 13, 'fast': 13, 'weighed': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'mighty': 13},
                        'legendary': {'splash': 10, 'precise': 10, 'fast': 10, 'weighed': 10, 'poisoned': 10, 'leech': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'mighty': 10}},
             
             'spear': {'junk': {'regular': 50, 'rusty': 50},
                        'common': {'regular': 80, 'rusty': 10, 'fast': 5, 'sharp': 5},
                        'uncommon': {'regular': 71, 'rusty': 5, 'fast': 12, 'sharp': 12},
                        'rare': {'regular': 50, 'rusty': 2, 'precise': 12, 'fast': 12, 'sharp': 12, 'mighty': 12}, 
                        'epic': {'precise': 13, 'fast': 13, 'sharp': 13, 'poisoned': 12, 'burning': 12, 'frost': 12, 'electric': 12, 'mighty': 13},
                        'legendary': {'deadly': 10, 'precise': 10, 'fast': 10, 'sharp': 10, 'poisoned': 10, 'leech': 10, 'burning': 10, 'frost': 10, 'electric': 10, 'mighty': 10}}}


adjEffects = {'regular': {},
              'rusty': {'pow': -2, 'ap': -2, 'crit': -2},
              'fast': {'acc': 5},
              'sharp': {'pow': 2},
              'discrete': {'stealth': 5},
              'precise': {'crit': 3},
              'frost': {}, #add freeze chance
              'poisoned': {}, #add poison chance
              'burning': {}, #add burn chance
              'electric': {}, #add electric arc chance
              'deadly': {'crit': 8}, #add +1 crit multiplier
              'leech': {}, #add life steal effect
              'mighty': {'strength': 1},
              'splash': {}, #add AOE dmg
              'weighed': {'weight': 1.0, 'pow': 2},
              'two-headed': {'weight': 1.5, 'pow': 3, 'acc': -3}, #multiply weight by 2 if peasant flail
              'three-headed': {'weight': 3.0, 'pow': 6, 'acc': -6}, #same
              'stunning': {}, #add stun chance
              'spiked': {'ap': 2},
              
              'tattered': {'stealth': -2},
              'dark': {'stealth': 5},
              'lightweight': {'ev': 5, 'weight': -0.3},
              'hardened': {'arm': 2, 'weight': 0.2},
              'ethereal': {'ev': 20, 'weight': -1.0}, #add air resist
              'ignited': {'stealth': -5, 'pow': 2}, #add fire resist
              'frozen': {'ev': -5, 'arm': 3, 'weight': 0.3}, #add water resist
              'shadow': {'stealth': 15},
              'nimble': {'dex': 2},
              'runic': {'will': 2},
              'healthful': {'vit': 2},
              'boiled': {'arm': 4},
              'lamellar': {'acc': 5},
              'barbed': {}, #add damage on attack
              'rusted': {'arm': -5},
              'telluric': {'arm': 8, 'weight': 1.0}, #add earth resist
              'padded': {'HP': 10},
              'riveted': {'arm': 5},
              'reinforced': {'arm': 5, 'weight': 0.5},
              'bulky': {'arm': 4, 'stam': 15, 'weight': 0.8}
              }

adjActive = {'regular': {'name': 'none'},
              'rusty': {'name': 'none'},
              'fast': {'name': ' of swiftness'},
              'sharp': {'name': ' of bite'},
              'discrete': {'name': ' of shadows'},
              'precise': {'name': ' of accuracy'},
              'frost': {'name': ' of ice'},
              'poisoned': {'name': ' of poison'},
              'burning': {'name': ' of fire'},
              'electric': {'name': ' of lightning'},
              'deadly': {'name': ' of lethality'},
              'leech': {'name': ' of haemorrhage'},
              'mighty': {'name': ' of devastation'},
              'splash': {'name': ' of blast'},
              'weighed': {'name': ' of mass'},
              'two-headed': {'name': 'none'},
              'three-headed': {'name': 'none'},
              'stunning': {'name': ' of dazing'},
              'spiked': {'name': ' of pain'}}
### weapons ###

rangedWeaponTypes = ['bow', 'crossbow', 'throwing axe', 'throwing knife', 'pistol', 'rifle', 'javelin']


### armors ###
armorTypes = ['cloth', 'leather', 'chainmail', 'scale', 'plate']
armorSlots = ['head', 'legs', 'chest', 'feet', 'hands', 'back']
possibleTypes = {'head': armorTypes, 'legs': armorTypes, 'chest': armorTypes, 'feet': armorTypes, 'hands': armorTypes, 'back': ['leather', 'cloth']}

armorTypeProb = {'junk': {'cloth': 80, 'leather': 20},
                 'common': {'cloth': 70, 'leather': 25, 'chainmail': 5},
                 'uncommon': {'cloth': 30, 'leather': 55, 'chainmail': 15},
                 'rare': {'cloth': 30, 'leather': 20, 'chainmail': 30, 'scale': 20},
                 'epic': {'cloth': 25, 'leather': 15, 'chainmail': 15, 'scale': 40, 'plate': 5},
                 'legendary': {'cloth': 20, 'leather': 10, 'chainmail': 15, 'scale': 20, 'plate': 35}
                 }

armorNames = {'head': {'cloth': 'hood', 'leather': 'hood', 'chainmail': 'coif', 'scale': 'aventail', 'plate': 'great helm'},
              'legs': {'cloth': 'pants', 'leather': 'pants', 'chainmail': 'chausses', 'scale': 'chausses', 'plate': 'greaves'},
              'chest': {'cloth': 'shirt', 'leather': 'tunique', 'chainmail': 'hauberk', 'scale': 'hauberk', 'plate': 'breastplate'},
              'feet': {'cloth': 'shoes', 'leather': 'boots', 'chainmail': 'boots', 'scale': 'sabatons', 'plate': 'sabatons'},
              'hands': {'cloth': 'gloves', 'leather': 'gloves', 'chainmail': 'mittens', 'scale': 'gauntlets', 'plate': 'gauntlets'},
              'back': {'cloth': 'cloak', 'leather': 'cape'},
              }

armorAttributes = {'cloth': {'head': {'pic': 'hood.xp', 'ev': 5, 'stealth': 5, 'weight': 0.1}, #TO-DO add pics
                             'legs': {'ev': 10, 'stealth': 10, 'weight': 0.3}, 
                             'chest': {'ev': 15, 'stealth': 10, 'weight': 0.5},
                             'feet': {'stealth': 5, 'weight': 0.2},
                             'hands': {'stealth': 5, 'dex': 5, 'weight': 0.1},
                             'back': {'stealth': 20, 'ev': 10, 'weight': 0.6}
                             },
                   'leather': {'head': {'pic': 'leatherHood.xp', 'arm': 1, 'stealth': 3, 'weight': 0.5},
                             'legs': {'arm': 3, 'weight': 1.2},
                             'chest': {'arm': 5, 'weight': 1.5},
                             'feet': {'arm': 2, 'weight': 0.9},
                             'hands': {'dex': 4, 'weight': 0.1},
                             'back': {'arm': 3, 'stealth': 7, 'weight': 1.0}
                             },
                   'chainmail': {'head': {'pic': 'coif.xp', 'arm': 5, 'dex': -2, 'weight': 1.2},
                                 'legs': {'arm': 7, 'ev': -7, 'weight': 1.9},
                                 'chest': {'arm': 10, 'ev': -10, 'weight': 2.4},
                                 'feet': {'arm': 3, 'ev': -5, 'weight': 1.3},
                                 'hands': {'arm': 3, 'dex': 3, 'weight': 1.0}
                                 },
                   'scale': {'head': {'pic': 'aventail.xp', 'arm': 8, 'dex': -4, 'weight': 2.1},
                             'legs': {'arm': 10, 'ev': -10, 'weight': 2.7},
                             'chest': {'arm': 13, 'ev': -15, 'weight': 3.4},
                             'feet': {'arm': 7, 'ev': -7, 'weight': 2.4},
                             'hands': {'arm': 5, 'dex': 2, 'weight': 1.9}
                             },
                   'plate': {'head': {'pic': 'greatHelm.xp', 'arm': 12, 'dex': -6, 'weight': 3.5},
                             'legs': {'arm': 14, 'ev': -15, 'weight': 4.1},
                             'chest': {'arm': 17, 'ev': -25, 'weight': 5.4},
                             'feet': {'arm': 11, 'ev': -10, 'weight': 3.0},
                             'hands': {'arm': 9, 'dex': 2, 'weight': 2.1}
                             }
                   }

armorAdj = {'cloth': {'head': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'dark': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'dark': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'dark': 16, 'lightweight': 16, 'hardened': 16}, 
                               'epic': {'dark': 14, 'lightweight': 15, 'hardened': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'dark': 11, 'lightweight': 11, 'hardened': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'shadow': 12, 'nimble': 11, 'runic': 11}},
                        'legs': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'dark': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'dark': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'dark': 16, 'lightweight': 16, 'hardened': 16}, 
                               'epic': {'dark': 14, 'lightweight': 15, 'hardened': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'dark': 11, 'lightweight': 11, 'hardened': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'shadow': 12, 'nimble': 11, 'healthful': 11}},
                        'chest': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'dark': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'dark': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'dark': 16, 'lightweight': 16, 'hardened': 16}, 
                               'epic': {'dark': 14, 'lightweight': 15, 'hardened': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'dark': 11, 'lightweight': 11, 'hardened': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'shadow': 12, 'nimble': 11, 'healthful': 11}},
                        'feet': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'dark': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'dark': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'dark': 16, 'lightweight': 16, 'hardened': 16}, 
                               'epic': {'dark': 14, 'lightweight': 15, 'hardened': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'dark': 13, 'lightweight': 12, 'hardened': 12, 'ethereal': 13, 'ignited': 12, 'frozen': 12, 'shadow': 13, 'nimble': 13}},
                        'hands': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'dark': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'dark': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'dark': 16, 'lightweight': 16, 'hardened': 16}, 
                               'epic': {'dark': 14, 'lightweight': 15, 'hardened': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'dark': 11, 'lightweight': 11, 'hardened': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'shadow': 12, 'nimble': 11, 'runic': 11}},
                        'back': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'dark': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'dark': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'dark': 16, 'lightweight': 16, 'hardened': 16}, 
                               'epic': {'dark': 14, 'lightweight': 15, 'hardened': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'dark': 10, 'lightweight': 10, 'hardened': 10, 'ethereal': 10, 'ignited': 10, 'frozen': 10, 'shadow': 10, 'nimble': 10, 'runic': 10, 'healthful': 10}}
                      },
            'leather': {'head': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'boiled': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'boiled': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'boiled': 16, 'lightweight': 16, 'lamellar': 16}, 
                               'epic': {'boiled': 14, 'lightweight': 15, 'lamellar': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'boiled': 10, 'lightweight': 10, 'lamellar': 10, 'ethereal': 10, 'ignited': 10, 'frozen': 10, 'shadow': 10, 'nimble': 10, 'runic': 10, 'barbed': 10}},
                        'legs': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'boiled': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'boiled': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'boiled': 16, 'lightweight': 16, 'lamellar': 16}, 
                               'epic': {'boiled': 14, 'lightweight': 15, 'lamellar': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'boiled': 11, 'lightweight': 11, 'lamellar': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'shadow': 12, 'nimble': 11, 'healthful': 11}},
                        'chest': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'boiled': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'boiled': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'boiled': 16, 'lightweight': 16, 'lamellar': 16}, 
                               'epic': {'boiled': 14, 'lightweight': 15, 'lamellar': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'boiled': 10, 'lightweight': 10, 'lamellar': 10, 'ethereal': 10, 'ignited': 10, 'frozen': 10, 'shadow': 10, 'nimble': 10, 'healthful': 10, 'barbed': 10}},
                        'feet': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'boiled': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'boiled': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'boiled': 16, 'lightweight': 16, 'lamellar': 16}, 
                               'epic': {'boiled': 14, 'lightweight': 15, 'lamellar': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'boiled': 13, 'lightweight': 12, 'lamellar': 12, 'ethereal': 13, 'ignited': 12, 'frozen': 12, 'shadow': 13, 'nimble': 13}},
                        'hands': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'boiled': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'boiled': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'boiled': 16, 'lightweight': 16, 'lamellar': 16}, 
                               'epic': {'boiled': 14, 'lightweight': 15, 'lamellar': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'boiled': 11, 'lightweight': 11, 'lamellar': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'shadow': 12, 'nimble': 11, 'runic': 11}},
                        'back': {'junk': {'regular': 50, 'tattered': 50},
                               'common': {'regular': 80, 'tattered': 10, 'boiled': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'tattered': 5, 'boiled': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'tattered': 2, 'boiled': 16, 'lightweight': 16, 'lamellar': 16}, 
                               'epic': {'boiled': 14, 'lightweight': 15, 'lamellar': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'shadow': 15},
                               'legendary': {'boiled': 10, 'lightweight': 10, 'lamellar': 10, 'ethereal': 10, 'ignited': 10, 'frozen': 10, 'shadow': 10, 'nimble': 10, 'runic': 10, 'healthful': 10}}
                      },
            'chainmail': {'head': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'riveted': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'riveted': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'riveted': 16, 'lightweight': 16, 'padded': 16}, 
                               'epic': {'riveted': 14, 'lightweight': 15, 'padded': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'riveted': 11, 'lightweight': 11, 'padded': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'telluric': 12, 'healthful': 11, 'runic': 11}},
                        'legs': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'riveted': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'riveted': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'riveted': 16, 'lightweight': 16, 'padded': 16}, 
                               'epic': {'riveted': 14, 'lightweight': 15, 'padded': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'riveted': 13, 'lightweight': 12, 'padded': 13, 'ethereal': 12, 'ignited': 12, 'frozen': 13, 'telluric': 13, 'healthful': 12}},
                        'chest': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'riveted': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'riveted': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'riveted': 16, 'lightweight': 16, 'padded': 16}, 
                               'epic': {'riveted': 14, 'lightweight': 15, 'padded': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'riveted': 13, 'lightweight': 12, 'padded': 13, 'ethereal': 12, 'ignited': 12, 'frozen': 13, 'telluric': 13, 'healthful': 12}},
                        'feet': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'riveted': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'riveted': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'riveted': 16, 'lightweight': 16, 'padded': 16}, 
                               'epic': {'riveted': 14, 'lightweight': 15, 'padded': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'riveted': 13, 'lightweight': 12, 'padded': 12, 'ethereal': 13, 'ignited': 12, 'frozen': 12, 'telluric': 13, 'nimble': 13}},
                        'hands': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'riveted': 5, 'lightweight': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'riveted': 12, 'lightweight': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'riveted': 16, 'lightweight': 16, 'padded': 16}, 
                               'epic': {'riveted': 14, 'lightweight': 15, 'padded': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'riveted': 11, 'lightweight': 11, 'padded': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'telluric': 12, 'nimble': 11, 'runic': 11}}
                          },
            'scale': {'head': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'lamellar': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'lamellar': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'lamellar': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'lamellar': 14, 'padded': 15, 'reinforced': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'lamellar': 11, 'padded': 11, 'reinforced': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'telluric': 12, 'healthful': 11, 'runic': 11}},
                      'legs': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'lamellar': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'lamellar': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'lamellar': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'lamellar': 14, 'padded': 15, 'reinforced': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'lamellar': 13, 'padded': 12, 'reinforced': 13, 'ethereal': 12, 'ignited': 12, 'frozen': 13, 'telluric': 13, 'healthful': 12}},
                      'chest': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'lamellar': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'lamellar': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'lamellar': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'lamellar': 14, 'padded': 15, 'reinforced': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'lamellar': 13, 'padded': 12, 'reinforced': 13, 'ethereal': 12, 'ignited': 12, 'frozen': 13, 'telluric': 13, 'healthful': 12}},
                      'feet': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'lamellar': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'lamellar': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'lamellar': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'lamellar': 14, 'padded': 15, 'reinforced': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'lamellar': 13, 'padded': 12, 'reinforced': 12, 'ethereal': 13, 'ignited': 12, 'frozen': 12, 'telluric': 13, 'nimble': 13}},
                      'hands': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'lamellar': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'lamellar': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'lamellar': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'lamellar': 14, 'padded': 15, 'reinforced': 14, 'ethereal': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'lamellar': 11, 'padded': 11, 'reinforced': 11, 'ethereal': 11, 'ignited': 11, 'frozen': 11, 'telluric': 12, 'nimble': 11, 'runic': 11}}
                      },
            'plate': {'head': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'bulky': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'bulky': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'bulky': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'bulky': 14, 'padded': 15, 'reinforced': 14, 'barbed': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'bulky': 11, 'padded': 11, 'reinforced': 11, 'barbed': 11, 'ignited': 11, 'frozen': 11, 'telluric': 12, 'healthful': 11, 'runic': 11}},
                      'legs': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'bulky': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'bulky': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'bulky': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'bulky': 14, 'padded': 15, 'reinforced': 14, 'barbed': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'bulky': 13, 'padded': 12, 'reinforced': 13, 'barbed': 12, 'ignited': 12, 'frozen': 13, 'telluric': 13, 'healthful': 12}},
                      'chest': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'bulky': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'bulky': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'bulky': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'bulky': 14, 'padded': 15, 'reinforced': 14, 'barbed': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'bulky': 13, 'padded': 12, 'reinforced': 13, 'barbed': 12, 'ignited': 12, 'frozen': 13, 'telluric': 13, 'healthful': 12}},
                      'feet': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'bulky': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'bulky': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'bulky': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'bulky': 14, 'padded': 15, 'reinforced': 14, 'barbed': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'bulky': 13, 'padded': 12, 'reinforced': 12, 'barbed': 13, 'ignited': 12, 'frozen': 12, 'telluric': 13, 'nimble': 13}},
                      'hands': {'junk': {'regular': 50, 'rusted': 50},
                               'common': {'regular': 80, 'rusted': 10, 'bulky': 5, 'padded': 5},
                               'uncommon': {'regular': 71, 'rusted': 5, 'bulky': 12, 'padded': 12},
                               'rare': {'regular': 50, 'rusted': 2, 'bulky': 16, 'padded': 16, 'reinforced': 16}, 
                               'epic': {'bulky': 14, 'padded': 15, 'reinforced': 14, 'barbed': 14, 'ignited': 14, 'frozen': 14, 'telluric': 15},
                               'legendary': {'bulky': 11, 'padded': 11, 'reinforced': 11, 'barbed': 11, 'ignited': 11, 'frozen': 11, 'telluric': 12, 'nimble': 11, 'runic': 11}}
                      }
            }

armorDictTemplate = ['pow', 'arm', 'HP', 'acc', 'ev', 'crit', 'MP', 'strength', 'dex', 'vit', 'will', 'ap', 'stam', 'stealth']
### armors ###

potionTypes = ['heal HP', 'heal MP', 'heal stamina', 'cure poison', 'poison', 'cure fire', 'fire', 'frost', 'speed fast', 'speed slow', 'strength', 'constitution', 'dexterity', 'willpower']


shieldTypes = ['buckler', 'round', 'heater', 'war-door']
shieldMaterials = ['leather', 'wooden', 'copper', 'iron', 'steel', 'crystal']


foodTypes = ['bread', 'herbs', 'rMeat', 'pie', 'pasta', 'meat', 'hBaguette']

class BetterInt:
    def __init__(self, value):
        self.value = value
    
    def __int__(self):
        return self.value
    
    def __iadd__(self, other):
        self.value = self.value + other
    
    def __add__(self, other):
        return self.value + other
    
    def __str__(self):
        return str(self.value)
    
    def __lt__(self, other):
        return self.value < other
    
    def __ne__(self, other):
        return self.value != other

'''
class BetterBool:
    def __init__(self, boolean):
        self.bool = boolean
    
    def __str__(self):
        return str(self.bool)
    
    def __bool__(self):
        return self.bool

class BetterStr:
    def __init__(self, string):
        self.string = string
    
    def __str__(self):
        return self.string
'''
   
class GameObjectTemplate:
    def __init__(self, char, name, color, Item = None, Equipment = None, pName = None):
        self.name = name
        self.pName = pName
        self.char = char
        self.color = color
        self.Item = Item
        self.Equipment = Equipment
    
    def __str__(self):
        text = '{} ({} {})'.format(self.name, self.color, self.char)
        if self.Item:
            text += '\n' + str(self.Item)
        if self.Equipment:
            text += '\n' + str(self.Equipment)
        return text


class ItemTemplate:
    def __init__(self, useFunction, arg1 = None, arg2 = None, arg3 = None, stackable = False, amount = 1, weight = 0, description = 'Placeholder', pic = 'trollMace.xp', itemtype = None, useText = 'Use'):
        self.useFunction = useFunction
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.stackable = stackable
        self.amount = amount
        self.weight = weight
        self.description = description
        self.pic = pic
        self.itemType = itemtype
        self.useText = useText
    
    def __str__(self):
        return '{} weighing {}, can be used by {} which does {}, it is described as "{}"'.format(self.itemType, str(self.weight), self.useText, str(self.useFunction), self.description)

equipmentStatsStrings = ['pow', 'arm', 'HP', 'acc', 'ev', 'crit', 'MP', 'strength', 'dex', 'vit', 'will', 'rangedPow', 'maxRange', 'ap', 'stam', 'stealth']


class EquipmentTemplate:
    def __init__(self, slot, type, powerBonus=0, armorBonus=0, maxHP_Bonus=0, accuracyBonus=0, evasionBonus=0, criticalBonus=0, maxMP_Bonus=0,
                strengthBonus=0, dexterityBonus=0, vitalityBonus=0, willpowerBonus=0, ranged=False, rangedPower=0, maxRange=0, ammo=None, meleeWeapon=False,
                armorPenetrationBonus=0, slow=False, enchant=None, staminaBonus=0, stealthBonus = 0):
        self.slot = slot
        self.type = type
        self.powerBonus = BetterInt(powerBonus)
        self.armorBonus = BetterInt(armorBonus)
        self.maxHP_Bonus = BetterInt(maxHP_Bonus)
        self.accuracyBonus = BetterInt(accuracyBonus)
        self.evasionBonus = BetterInt(evasionBonus)
        self.criticalBonus = BetterInt(criticalBonus)
        self.maxMP_Bonus = BetterInt(maxMP_Bonus)
        self.strengthBonus = BetterInt(strengthBonus)
        self.dexterityBonus = BetterInt(dexterityBonus)
        self.vitalityBonus = BetterInt(vitalityBonus)
        self.willpowerBonus = BetterInt(willpowerBonus)
        self.ranged = ranged
        self.rangedPower = BetterInt(rangedPower)
        self.maxRange = BetterInt(maxRange)
        self.ammo = ammo
        self.meleeWeapon = meleeWeapon
        self.armorPenetrationBonus = BetterInt(armorPenetrationBonus)
        self.slow = slow
        self.enchant = enchant
        self.staminaBonus = BetterInt(staminaBonus)
        self.stealthBonus = BetterInt(stealthBonus)
    
    @property
    def stats(self):
        return [self.powerBonus, self.armorBonus, self.maxHP_Bonus, self.accuracyBonus, self.evasionBonus, self.criticalBonus, self.maxMP_Bonus, self.strengthBonus, self.dexterityBonus, self.vitalityBonus, self.willpowerBonus, self.rangedPower, self.maxRange, self.armorPenetrationBonus, self.staminaBonus, self.stealthBonus]
    
    def __str__(self):
        text =  'A {} equipped on {}, it is {} a melee weapon and {} a ranged weapon. It has some boni:'.format(self.type, self.slot, str(self.meleeWeapon), str(self.ranged))
        
        if self.powerBonus != 0:
            text += '\n' + str('power:' + str(self.powerBonus))
        if self.armorBonus != 0:
            text += '\n' + str('armor:' + str(self.armorBonus))
        if self.maxHP_Bonus != 0:
            text += '\n' + str('HP:' + str(self.maxHP_Bonus))
        if self.accuracyBonus != 0:
            text += '\n' + str('acc:' + str(self.accuracyBonus))
        if self.evasionBonus != 0:
            text += '\n' + str('evasion:' + str(self.evasionBonus))
        if self.criticalBonus != 0:
            text += '\n' + str('crit:' + str(self.criticalBonus))
        if self.maxMP_Bonus != 0:
            text += '\n' + str('MP:' + str(self.maxMP_Bonus))
        if self.strengthBonus != 0:
            text += '\n' + str('strength:' + str(self.strengthBonus))
        if self.dexterityBonus != 0:
            text += '\n' + str('dex:' + str(self.dexterityBonus))
        if self.vitalityBonus != 0:
            text += '\n' + str('const:' + str(self.vitalityBonus))
        if self.willpowerBonus != 0:
            text += '\n' + str('will:' + str(self.willpowerBonus))
        if self.rangedPower != 0 and self.ranged:
            text += '\n' + str('ranged power:' + str(self.rangedPower))
        if self.maxRange != 0 and self.ranged:
            text += '\n' + str('range:' + str(self.maxRange))
        if self.armorPenetrationBonus != 0:
            text += '\n' + str('AP:' + str(self.armorPenetrationBonus))
        if self.staminaBonus != 0:
            text += '\n' + str('stamina:' + str(self.staminaBonus))
        if self.stealthBonus != 0:
            text += '\n' + str('stealth:' + str(self.stealthBonus))
        if self.slow:
            text += '\n' + str('slow!')
        
        return text

class EnchantmentTemplate:
    def __init__(self, name, functionOnAttack = None, buffOnOwner = [], buffOnTarget = [], damageOnOwner = 0, damageOnTarget = 0, power = 0, acc = 0, evas = 0, arm = 0, hp = 0, mp = 0, crit = 0, ap = 0, stren = 0, dex = 0, vit = 0, will = 0, stamina = 0):
        self.name = name
        self.functionOnAttack = functionOnAttack
        self.buffOnOwner = buffOnOwner
        self.buffOnTarget = buffOnTarget
        self.damageOnOwner = damageOnOwner
        self.damageOnTarget = damageOnTarget
        self.power = power
        self.acc = acc
        self.evas = evas
        self.arm = arm
        self.hp = hp
        self.mp = mp
        self.crit = crit
        self.ap = ap
        self.stren = stren
        self.dex = dex
        self.vit = vit
        self.will = will
        self.stamina = stamina


def randItemFrom(randList):
    return randList[randint(0, len(randList) - 1)]

def randomChoiceIndex(chances):
    dice = randint(1, sum(chances))
    runningSum = 0
    choice = 0
    for chance in chances:
        runningSum += chance
        if dice <= runningSum:
            return choice
        choice += 1

def randomChoice(chancesDictionnary):
    chances = chancesDictionnary.values()
    for value in chances:
        if value < 0:
            print(value)
            print(chancesDictionnary.keys())
            print(chancesDictionnary)
            raise ValueError("Negative value in dict")
    strings = list(chancesDictionnary.keys())
    return strings[randomChoiceIndex(chances)]


def generateMeleeWeapon(weaponType = None):
    if weaponType is None:
        weaponType = randItemFrom(weaponTypes)
    
    weapon = randomChoice(weaponSize[weaponType])
    
    weaponRarity = randomChoice(rarity)
    stringRarity = str(weaponRarity)
    
    weaponDict = weaponAttributes[weapon]
    weaponEquipment = EquipmentTemplate(weaponDict['slot'], stringRarity + ' ' + weaponDict['type'] + ' ' + weaponType, meleeWeapon = True)
    
    try:
        weaponEquipment.slow = weaponDict['slow']
    except:
        pass
    
    adj = []
    passiveNumber = 1
    active = False
    try:
        rareCombo = randomChoice(rarityCombo[stringRarity])
    except:
        rareCombo = 'none'
    
    if '2 passive' in rareCombo:
        passiveNumber = 2
    if '3 passive' in rareCombo:
        passiveNumber = 3
    if 'active' in rareCombo:
        active = True
    
    adjDict = weaponAdj[weaponType][stringRarity]
    for i in range(passiveNumber):
        bonus = randomChoice(adjDict)
        while bonus in adj or (bonus == 'fast' and weaponEquipment.slow) or (bonus == 'frost' and 'burning' in adj) or (bonus == 'burning' and 'frost' in adj) or ('headed' in bonus and 'headed' in adj):
            bonus = randomChoice(adjDict)
        adj.append(bonus)
    
    if active:
        activeAdj = randItemFrom(adj)
        i = 0
        weaponAbility = adjActive[activeAdj]['name']
        while 'headed' in activeAdj and i <= 10:
            weaponAbility = adjActive[activeAdj]['name']
            i += 1
    
    addToName = ''
    for adjective in adj:
        if adjective != 'regular':
            addToName += adjective + ' '
    
    endName = ''
    if active:
        if weaponAbility != 'none':
            endName = weaponAbility
    
    i = 0
    for stat in weaponEquipment.stats:
        moddedStat = equipmentStatsStrings[i]
        try:
            dictToUse = raritySmallAdd
            if moddedStat == 'HP' or moddedStat == 'MP' or moddedStat == 'stam':
                dictToUse = rarityBigAdd
            stat.value = weaponDict[equipmentStatsStrings[i]] + randint(-2 + dictToUse[stringRarity], 2 + dictToUse[stringRarity])
            if (stat < 0 and weaponDict[equipmentStatsStrings[i]] > 0) or (stat > 0 and weaponDict[equipmentStatsStrings[i]] < 0): #if a postive value becomes negative or vice versa
                stat.value = 0
        except:
            pass
        i += 1
    
    tempWeight = weaponDict['weight']
    
    i = 0
    for stat in weaponEquipment.stats:
        for adjective in adj:
            dictToUse = raritySmallAdd
            moddedStat = equipmentStatsStrings[i]
            if moddedStat == 'HP' or moddedStat == 'MP' or moddedStat == 'stam':
                dictToUse = rarityBigAdd
            try:
                bonus = adjEffects[adjective][equipmentStatsStrings[i]]
                toAdd = randint(0, dictToUse[stringRarity]//2)
                if bonus < 0 and bonus + toAdd > 0:
                    toAdd = -bonus
                stat += bonus + toAdd
            except:
                pass
        i += 1
    
    for adjective in adj:
        try:
            tempWeight += adjEffects[adjective]['weight']
            if 'headed' in adjective and 'heavy' in weaponEquipment.type:
                tempWeight += adjEffects[adjective]['weight']
        except:
            pass
    
    weaponItem = ItemTemplate('Equip', weight = round(tempWeight, 1), itemtype = 'weapon', useText = 'Equip')

    try:
        weaponItem.description = weaponDict['desc']
    except:
        pass
    try:
        weaponItem.pic = weaponDict['pic']
    except:
        pass
    if 'light' in weaponEquipment.type:
        char = '-'
    else:
        char = '/'
    
    weaponObject = GameObjectTemplate(char, addToName + weapon + endName, weaponRarity.color, Item = weaponItem, Equipment = weaponEquipment)
    return weaponObject

def generateArmor(armorType = None, slot = None):
    armorRarity = randomChoice(rarity)
    stringRarity = str(armorRarity)
    
    if armorType is None:
        armorType = randomChoice(armorTypeProb[stringRarity])
    
    if slot is None:
        slot = randItemFrom(armorSlots)
        while armorType not in possibleTypes[slot]:
            slot = randItemFrom(armorSlots)

    armorDict = armorAttributes[armorType][slot]
    armorEquipment = EquipmentTemplate(slot, stringRarity + ' ' + armorType + ' armor')
    
    adj = []
    passiveNumber = 1
    try:
        rareCombo = randomChoice(rarityCombo[stringRarity])
    except:
        rareCombo = 'none'
    
    if '2 passive' in rareCombo:
        passiveNumber = 2
    if '3 passive' in rareCombo:
        passiveNumber = 3
    
    adjDict = armorAdj[armorType][slot][stringRarity]
    for i in range(passiveNumber):
        bonus = randomChoice(adjDict)
        while bonus in adj or (bonus == 'frozen' and 'ignited' in adj) or (bonus == 'ignited' and 'frozen' in adj) or (bonus == 'etheral' and 'telluric' in adj) or (bonus == 'telluric' and 'ethereal' in adj):
            bonus = randomChoice(adjDict)
        adj.append(bonus)
    
    addToName = ''
    for adjective in adj:
        if adjective != 'regular':
            addToName += adjective + ' '
    
    i = 0
    for stat in armorEquipment.stats:
        moddedStat = equipmentStatsStrings[i]
        try:
            dictToUse = raritySmallAdd
            if moddedStat == 'HP' or moddedStat == 'MP' or moddedStat == 'stam':
                dictToUse = rarityBigAdd
            stat.value = armorDict[equipmentStatsStrings[i]] + randint(-2 + dictToUse[stringRarity], 2 + dictToUse[stringRarity])
            if (stat < 0 and armorDict[equipmentStatsStrings[i]] > 0) or (stat > 0 and armorDict[equipmentStatsStrings[i]] < 0): #if a postive value becomes negative or vice versa
                stat.value = 0
        except:
            pass
        i += 1
    
    tempWeight = armorDict['weight']
    
    i = 0
    for stat in armorEquipment.stats:
        for adjective in adj:
            dictToUse = raritySmallAdd
            moddedStat = equipmentStatsStrings[i]
            if moddedStat == 'HP' or moddedStat == 'MP' or moddedStat == 'stam':
                dictToUse = rarityBigAdd
            try:
                bonus = adjEffects[adjective][equipmentStatsStrings[i]]
                toAdd = randint(0, dictToUse[stringRarity]//2)
                if bonus < 0 and bonus + toAdd > 0:
                    toAdd = -bonus
                stat += bonus + toAdd
            except:
                pass
        i += 1
    
    for adjective in adj:
        try:
            tempWeight += adjEffects[adjective]['weight']
            if 'headed' in adjective and 'heavy' in armorEquipment.type:
                tempWeight += adjEffects[adjective]['weight']
        except:
            pass
    
    if tempWeight < 0:
        tempWeight = 0
    weaponItem = ItemTemplate('Equip', weight = round(tempWeight, 1), itemtype = 'armor', useText = 'Equip')

    try:
        weaponItem.description = armorDict['desc']
    except:
        pass
    try:
        weaponItem.pic = armorDict['pic']
    except:
        pass
    
    weaponObject = GameObjectTemplate(']', addToName + armorNames[slot][armorType], armorRarity.color, Item = weaponItem, Equipment = armorEquipment)
    return weaponObject

if __name__ == '__main__':
    for loop in range(10):
        print(generateArmor())
        print()






