__author__ = 'tyoung'
import pygame
import os, sys
from copy import deepcopy
import types
pygame.font.init()
font = pygame.font.Font(None, 10)


class Editable():
    imgName = None
    isPlayer = False
    picture = None
    interactionString = None
    rotation = 0
    lastMove = None
    switchTime = 100
    movable = True
    maxHealth=1
    description=""
    hp=1
    blocking = True
    onClick = lambda self, x, y, clicktype, camera: False
    rect=(0,0,0,0)
    markedForDeletion=False
    rawScaling=True

    def onClick(self, x, y, clicktype, camera):
        pass

    def loadImgs(self, name):
        self.imgName = name

    def damage(self, damage):
        pass

    def move(self, xoff, yoff,camera,model,cached):
            self.rect = (self.rect[0] + xoff,
                         self.rect[1] + yoff,
                         self.rect[2],
                         self.rect[3],)
            self.lastMove = (xoff, yoff)

    def drawHP(self, screen, camera):
        pass

    def draw(self, screen, camera,model):
        pass
    def update(self):
        self.timer += 2

    def click(self, x, y, clicktype, camera):
        if self.targetable:
            if camera.inBounds((0, 0, self.rect[2], self.rect[3]), x, y):
                self.onClick(x, y, clicktype, camera)
                return self

    def getBounds(self):
        return self.rect

    def isClicked(self, x, y,camera):
        if camera.inBounds((self.rect[0], self.rect[1],self.rect[2], self.rect[3]), x, y):
            return self
    def onDeletePress(self,camera,cached,model):
        self.markedForDeletion = True
        camera.target = None
        pass
    def duplicateTo(self,x,y,camera, model):
        pass

    def resize(self,dw,dh,camera,model,cached):
        self.rect = (self.rect[0],
                     self.rect[1],
                     max(self.rect[2]+dw,1),
                     max(self.rect[3]+dh,1),)
    def rotateBy(self, dR):
        if dR%2==1:
            self.rect = ( self.rect[0],self.rect[1],self.rect[3],self.rect[2])
        self.rotation=(self.rotation+dR)%4
    def interaction(self ,model, camera, cached):
        if self.interactionString:
            try:
                exec self.interactionString
            except Exception,e:
                print str(e)




