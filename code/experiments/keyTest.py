#Even when I write something as simple as that it turns out to be a complete mess.
#But at least it works (mostly).

import tdlib as tdl
import threading, os, colors, time

WIDTH, HEIGHT = 30, 5
FPS_LIMIT = 30 #For a C I N E M A T I C experience.
MID_WIDTH, MID_HEIGHT = WIDTH//2, HEIGHT//2
mainConsole = tdl.init(width = WIDTH, height = HEIGHT, title = "Keyboard Test")
#shiftConsole = tdl.Console(width = WIDTH, height = 1)
curKey = "None"
shiftPressed = False
'''
class ShiftUpdater(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        
        while True:
            
            #shiftInput = tdl.event.key_wait()
            #if shiftInput.keychar == "SHIFT":
            
            if shiftPressed:
                message = "Shift is being pressed"
                x = MID_WIDTH - len(message) // 2
                shiftConsole.draw_str(x, 0, message)
                print("Shift Down")
                Update()
                foundShiftStop = False
                while not foundShiftStop:
                    for event in tdl.event.get():
                        if event.type == "KEYUP" and event.keychar == "SHIFT":
                            foundShiftStop = True
                            print("Shift UP")
                            shiftConsole.clear()
                            resetShiftState()
                            Update()
            else:
                time.sleep(0.001)
    
    def exitThread(self):
        os._exit(1)
'''

def Update(toClear = False):
    if toClear:
        mainConsole.clear()
        print("Main clear")
    message = "Key Pressed = " + curKey
    mainConsole.draw_str(MID_WIDTH - len(message)//2, MID_HEIGHT, message, fg = colors.green)
    #mainConsole.blit(shiftConsole, 0 ,3, width = WIDTH, height = 1)
    tdl.flush()

def resetShiftState():
    global shiftPressed
    shiftPressed = False

def mainLoop():
    global curKey, shiftPressed
    Update(True)
    #updater = ShiftUpdater()
    #updater.start()
    while not tdl.event.is_window_closed():
        inputKey = tdl.event.key_wait().keychar
        if not inputKey.upper() in ("SHIFT", "ESCAPE"):
            curKey = inputKey
            Update(True)
        elif inputKey.upper() == "SHIFT":
            shiftPressed = True
        elif inputKey.upper() == "ESCAPE":
            break
    #updater.exitThread()
    os._exit(1)

if __name__ == "__main__":
    mainLoop()
            
        