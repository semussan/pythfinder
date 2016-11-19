__author__ = 'tyoung'
import os
import pygame
from pygame.locals import *


class Cached():
    _fogImgs=None
    _imgs={}
    _portraits={}
    _bloodImgs = None
    _screen = None
    _sounds = {}
    _soundChannels= {}
    vert = None
    horz = None
    _gSoundImg = None
    _lSoundImg = None
    _playerToJoystick={}
    _playerLastPress={}
    def clear(self):
        self._fogImgs=None
        self._imgs={}
        self._portraits={}
        self._bloodImgs = None
        self._sounds = {}
        self.vert = None
        self.horz = None
        self._gSoundImg = None
        self._lSoundImg = None
        self._playerToJoystick={}
        self._playerLastPress={}

    def fogImgs(self,camera):
        if not self._fogImgs:
            self.loadFogImgs(camera)
        return self._fogImgs
    def loadFogImgs(self,camera):
        if not self._fogImgs:
            self._fogImgs = []
        self._fogImgs = [None for x in range(3)]
        for level, imgKey  in enumerate(self._fogImgs):
            trans = pygame.Surface( (camera.gridSize, camera.gridSize,))
            trans.set_alpha(level * 128)
            trans.fill((10, 10, 10))
            self._fogImgs[level] = trans

    def bloodImgs(self):
        if not self._bloodImgs:
            self.loadBloodImgs()
        return self._bloodImgs
    def loadBloodImgs(self):
        bloodDir = './coreImgs/blood/'
        filelist = [bloodDir + f for f in os.listdir(bloodDir)]
        self._bloodImgs = []
        for filename in filelist:
            self._bloodImgs.append(pygame.image.load(filename))

    def getAllFiles(self, fileName):
        if fileName:
            folder, filePart = os.path.split(fileName)
            namePart = filePart.split('.')[0]
            files = [folder + '/' + f for f in os.listdir(folder) if os.path.isfile(folder + '/' + f) and namePart in f]
            return files
        else:
            return []


    def loadImgs(self, imgName):
        self._imgs[imgName] = []
        self._portraits[imgName] = None
        for f in [f for f in self.getAllFiles(imgName) if '.png' in f]:
            if 'P.png' in f:
                self._portraits[imgName] = pygame.image.load(f)
            else:
                self._imgs[imgName].append(pygame.image.load(f))

    def getImgs(self, imgName):
        if imgName not in self._imgs:
            self.loadImgs(imgName)
        return self._imgs[imgName]

    def portrait(self, imgName):
        if imgName not in self._imgs:  # net checking portrait, b/c ther emight not actually be any portrait file
            self.loadImgs(imgName)

        return None if imgName not in self._portraits or not self._imgs[imgName] else self._portraits[imgName]

    def bgsoundChannels(self):
        if not self._sounds:
            _sounds={}
        return self._sounds
    def bgsounds(self):
        if not self._soundChannels:
            self._soundChannels = {}
        return self._soundChannels
    def screen(self,camera):
        if not self._screen:
            self._screen = pygame.display.set_mode((camera.resx, camera.resy), DOUBLEBUF)
        return self._screen