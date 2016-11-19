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

    def drawGridlines(self, camera,cached):
        # gridlines
        if camera.drawGrid:
            if not cached.vert:
                rawImg = pygame.image.load('coreImgs/vert.png')
                cached.vert = pygame.transform.scale(rawImg, (3, self.rect[3] * camera.gridSize))
            newrect = cached.vert.get_rect()

            xs, ys, ws, hs = camera.getRectForRect(self.rect)
            newrect = newrect.move(0, ys)
            oldpos = 0
            for x in range(xs, xs + ws, camera.gridSize):
                newrect = newrect.move(x - oldpos, 0)
                cached.screen(camera).blit(cached.vert, newrect)
                oldpos = x

            if not cached.horz:
                rawImg = pygame.image.load('coreImgs/horz.png')
                cached.horz = pygame.transform.scale(rawImg, (self.rect[2] * camera.gridSize, 3))
            newrect = cached.horz.get_rect()
            newrect = newrect.move(xs, 0)
            oldpos = 0
            for y in range(ys, ys + hs, camera.gridSize):
                newrect = newrect.move(0, y - oldpos)
                cached.screen(camera).blit(cached.horz, newrect)
                oldpos = y

    def draw(self, screen, camera,cached ,model):
        self.switchTime = 10
        imgs = cached.getImgs(self.imgName)
        curImg = imgs[(self.timer / self.switchTime) % len(imgs)]
        picture = pygame.transform.rotate(curImg, self.rotation*90)
        picture = pygame.transform.scale(picture, (self.rect[2] * camera.gridSize,
                                                   self.rect[3] * camera.gridSize))
        newrect = picture.get_rect()
        newrect = newrect.move(self.rect[0], self.rect[1])
        screen.blit(picture, camera.getRectForRect(newrect))

        self.drawGridlines(camera,cached)

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