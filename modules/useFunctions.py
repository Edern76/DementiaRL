import colors
from main import message

def castHeal(target, healAmount = 5):
    if target.Fighter.hp == target.Fighter.maxHP:
        message('You are already at full health')
        return 'cancelled'
    else:
        message('You are healed for {} HP !'.format(healAmount), colors.light_green)
        target.Fighter.heal(healAmount)
    