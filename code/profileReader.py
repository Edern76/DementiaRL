import pstats
from tkinter import *
from tkinter.filedialog import *

Tk().withdraw()
path = askopenfilename(defaultextension = '.profile', filetypes= [('All files', '.*'), ('Profile files', '.profile')])
stats = pstats.Stats(path)
stats.strip_dirs().sort_stats('time').print_stats()
input()

