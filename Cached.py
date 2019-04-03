__author__ = 'tyoung'
import os
import pygame
from pygame.locals import *


class Cached():
    _fogImgs=None
    _imgs=[{},{}]
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
        self._imgs=[{},{}]
        self._portraits={}
        self._bloodImgs = None
        self._sounds = {}
        self.vert = None
        self.horz = None
        self._gSoundImg = None
        self._lSoundImg = None
        self._playerToJoystick={}
        self._playerLastPress={}

    def calc_derivs(self, camera):
        self.loadFogImgs(camera)

    def fogImgs(self,camera):
        if not self._fogImgs:
            self.loadFogImgs(camera)
        return self._fogImgs

    def loadFogImgs(self,camera):
        if not self._fogImgs:
            self._fogImgs = []
        self._fogImgs = [None for x in range(3)]
        for level, imgKey  in enumerate(self._fogImgs):
            trans = pygame.Surface( (camera.tileSize, camera.tileSize,)).convert()
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
            self._bloodImgs.append(pygame.image.load(filename).convert_alpha())

    def getAllFiles(self, fileName):
        if fileName:
            folder, filePart = os.path.split(fileName)
            namePart = filePart.split('.')[0]
            files = [folder + '/' + f for f in os.listdir(folder) if os.path.isfile(folder + '/' + f) and namePart in f]
            return files
        else:
            return []


    def loadImgs(self, imgName, flipped = False, rotation = 0, size = None):
        flip_index = int(flipped)
        if imgName not in self._imgs[flip_index]:
            self._imgs[flip_index][imgName] = {}
        if rotation not in self._imgs[flip_index][imgName]:
            self._imgs[flip_index][imgName][rotation] = {}
        if size not in self._imgs[flip_index][imgName][rotation]:
            self._imgs[flip_index][imgName][rotation][size] = []
        self._portraits[imgName] = None
        for f in [f for f in self.getAllFiles(imgName) if '.png' in f]:
            if 'P.png' in f:
                self._portraits[imgName] = pygame.image.load(f).convert_alpha()
            else:
                img = pygame.image.load(f).convert_alpha()
                actual_size = size 
                if not size:
                    actual_size = (img.get_width(), img.get_height())
                img = pygame.transform.rotate(img,rotation)
                img = pygame.transform.scale(img, actual_size)
                #img = img.convert_alpha()
                self._imgs[flip_index][imgName][rotation][size].append(img)

    def getImg(self, imgName, size = None, flipped = False, rotation = 0, idx = 0):
        flip_index = int(flipped)
        if imgName not in self._imgs[flip_index] or rotation not in self._imgs[flip_index][imgName] or size not in self._imgs[flip_index][imgName][rotation]:
            self.loadImgs(imgName,flipped = flipped, rotation = rotation, size = size)

        return self._imgs[flip_index][imgName][rotation][size][idx]

    def getImgRect(self, imgName, index, flipped = False, rotation = 0, size = None):
        flip_index = int(flipped)
        if imgName not in self._imgs[flip_index]:
            self.loadImgs(imgName,flipped = flipped)
        size = self._imgs[flip_index][imgName][rotation][size][index].get_rect()
        return size

    def getNumImgs(self, imgName, flipped = False):
        flip_index = int(flipped)
        if imgName not in self._imgs[flip_index]:
            self.loadImgs(imgName,flipped = flipped)
        return len(self._imgs[flip_index][imgName][0][None])


    def portrait(self, imgName):
        if imgName not in self._imgs[0]:  # net checking portrait, b/c ther emight not actually be any portrait file
            self.loadImgs(imgName)

        return None if imgName not in self._portraits or not self._imgs[0][imgName] else self._portraits[imgName]

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
            self._screen = pygame.display.set_mode((camera.resx, camera.resy), DOUBLEBUF, RESIZABLE)
        return self._screen