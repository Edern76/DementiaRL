import tdl, textwrap, colors
from code.constants import *


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')
    headerWrapped = textwrap.wrap(header, width)
    headerHeight = len(headerWrapped)
    if header == "":
        headerHeight = 0
    height = len(options) + headerHeight + 1
    window = tdl.Console(width, height)
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    for i, line in enumerate(headerWrapped):
        window.draw_str(0, 0+i, headerWrapped[i])

    y = headerHeight + 1
    letterIndex = ord('a')
    for optionText in options:
        text = '(' + chr(letterIndex) + ') ' + optionText
        window.draw_str(0, y, text, bg=None)
        y += 1
        letterIndex += 1
    

    x = MID_WIDTH - int(width/2)
    y = MID_HEIGHT - int(height/2)
    root.blit(window, x, y, width, height, 0, 0)

    tdl.flush()
    key = tdl.event.key_wait()
    keyChar = key.char
    if keyChar == '':
        keyChar = ' '    
    index = ord(keyChar) - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None

def msgBox(text, width = 50):
    menu(text, [], width)
        
def drawCentered (cons = con , y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    xCentered = (WIDTH - len(text))//2
    cons.draw_str(xCentered, y, text, fg, bg)

def drawCenteredOnX(cons = con, x = 1, y = 1, text = "Lorem Ipsum", fg = None, bg = None):
    centeredOnX = x - (len(text)//2)
    cons.draw_str(centeredOnX, y, text, fg, bg)