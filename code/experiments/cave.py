import tdl
from random import *

WIDTH, HEIGHT, LIMIT = 150, 80, 20
MAP_WIDTH, MAP_HEIGHT = 140, 60
MID_MAP_WIDTH, MID_MAP_HEIGHT = MAP_WIDTH//2, MAP_HEIGHT//2
MID_WIDTH, MID_HEIGHT = int(WIDTH/2), int(HEIGHT/2)

if __name__ == '__main__':
    root = tdl.init(WIDTH, HEIGHT, 'Dementia')
    
class Tile:
    def __init__(self, blocked):
        self.blocked = blocked

myMap = [[Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

def generateMap():
    pass

def update():
    root.clear()
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if myMap[x][y].blocked:
                root.draw_char(x, y, char = '#')
            else:
                root.draw_char(x, y, char = '.')
    tdl.flush()
    
if __name__ == '__main__':
    generateMap()
    while not tdl.event.is_window_closed():
        
        Update()
                
