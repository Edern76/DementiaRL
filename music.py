import simpleaudio as sa
import os, sys

def findCurrentDir():
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return datadir

curDir = findCurrentDir()
relDirPath = "save"
relPath = os.path.join("save", "savegame")
relPicklePath = os.path.join("save", "equipment")
relAssetPath = "assets"
relSoundPath = os.path.join("assets", "sound")
relAsciiPath = os.path.join("assets", "ascii")
relMusicPath = os.path.join("assets", "music")
relMetaPath = os.path.join("metasave", "meta")
relMetaDirPath = "metasave"
absDirPath = os.path.join(curDir, relDirPath)
absFilePath = os.path.join(curDir, relPath)
absPicklePath = os.path.join(curDir, relPicklePath)
absAssetPath = os.path.join(curDir, relAssetPath)
absSoundPath = os.path.join(curDir, relSoundPath)
absAsciiPath = os.path.join(curDir, relAsciiPath)
absMetaPath = os.path.join(curDir, relMetaPath)
absMetaDirPath = os.path.join(curDir, relMetaDirPath)

def playWavSound(sound, forceStop = False):
    if forceStop:
        sa.stop_all()
    soundPath = os.path.join(absSoundPath, sound)
    waveObj = sa.WaveObject.from_wave_file(soundPath)
    try:
        playObj = waveObj.play()
    except SimpleAudioError:
        pass
    return playObj

def runMusic(musicName):
    playObj = None
    while True:
        if playObj is None or not playObj.is_playing():
            playObj = playWavSound(musicName, forceStop=True)