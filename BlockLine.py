from Editable import Editable
import pygame
from copy import deepcopy
class BlockLine(Editable):
    def __init__(self,rect,isVert):
        self.isVert=isVert;
        self.rect=rect;

    def draw(self, screen, camera,cached ,model):
        newrect = camera.getRectForRect(self.rect)
        if self.isVert:
            pygame.draw.line(screen, (180,0,0), (newrect[0],newrect[1]), (newrect[0],newrect[1]+newrect[3]),2)
        else:
            pygame.draw.line(screen, (180,0,0), (newrect[0],newrect[1]), (newrect[0]+newrect[2],newrect[1]),2)
    def resize(self,dw,dh,camera,model,cached):
        if self.isVert:
            dw=0
        else:
            dh=0
        self.rect = (self.rect[0],
                     self.rect[1],
                     max(self.rect[2]+dw,1),
                     max(self.rect[3]+dh,1),)

    def duplicateTo(self,x,y,camera, model):
        duplicate= deepcopy(self)

        duplicate.rect = (x,y, self.rect[2],self.rect[3])
        model.world.currentArea.blocklines.append(duplicate)
        camera.target=duplicate
    def rotateBy(self, dR):
        if dR%2==1:
            self.rect = ( self.rect[0],self.rect[1],self.rect[3],self.rect[2])
        self.rotation=(self.rotation+dR)%4
        self.isVert=not self.isVert