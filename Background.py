__author__ = 'tyoung'
import pygame
from Shadows import FoWMap
from Editable import Editable
from copy import deepcopy


class Background(Editable):
    def __init__(self, imgName, rect, hasShadows):
        self.imgName = imgName
        self.rect = rect
        self.hasShadows = hasShadows
        self.FoW = FoWMap(rect, hasShadows)
        self.blood = []
        self.timer = 0
        self.switchTime = 50

    def draw(self, screen, camera,cached ,model):
        self.switchTime = 10
        num_imgs = cached.getNumImgs(self.imgName)
        img_idx = (self.timer / self.switchTime) % num_imgs
        size = (self.rect[2] * camera.tileSize, self.rect[3] * camera.tileSize)
        picture = cached.getImg(self.imgName, idx = img_idx, rotation = self.rotation*90, size=size)
        newrect = picture.get_rect()
        newrect = newrect.move(self.rect[0], self.rect[1])
        screen.blit(picture, camera.gridRectToCameraRect(newrect))

    def drawFoW(self, screen, camera,cached):
        if self.FoW and camera.drawShadows:
            self.FoW.draw(screen, camera,cached)

    def click(self, x, y, clicktype, camera,targetShadow):
        camera.target = None
        if targetShadow and self.FoW and camera.drawShadows:
            self.FoW.click(x, y, clicktype, camera)
        return self


    def reveal(self, x, y, camera,cached, parentArea):
        if self.FoW and camera.drawShadows:
            self.FoW.reveal(x, y, camera,cached, parentArea,self)

    def move(self, xoff, yoff,camera,model,cached):
        self.rect = (self.rect[0] + xoff,
                     self.rect[1] + yoff,
                     self.rect[2],
                     self.rect[3],)
        self.FoW.rect=self.rect
        self.lastMove = (xoff, yoff)

    def duplicateTo(self,x,y,camera, model):
        duplicate= deepcopy(self)

        duplicate.rect = (x,y, self.rect[2],self.rect[3])
        duplicate.FoW.rect = (x,y, self.rect[2],self.rect[3])
        #duplicate.FoW = FoWMap(rect, hasShadows, parentArea,self)
        model.world.currentArea.backgrounds.append(duplicate)
        camera.target=duplicate

    def rotateBy(self, dR):
        if dR%2==1:
            self.rect = ( self.rect[0],self.rect[1],self.rect[3],self.rect[2])
        self.rotation=(self.rotation+dR)%4
        self.FoW = self.FoW = FoWMap(self.rect, self.hasShadows)


    def resize(self,dw,dh,camera,model,cached):
        self.rect = (self.rect[0],
                     self.rect[1],
                     max(self.rect[2]+dw,1),
                     max(self.rect[3]+dh,1),)
        self.FoW = FoWMap(self.rect, self.hasShadows)