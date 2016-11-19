import pygame
from Editable import Editable
import os
import types
import random


pygame.font.init()
font = pygame.font.Font(None, 12)
from copy import deepcopy

class Entity(Editable):
    picture = None
    joystick = None
    wiggleLeft=False
    wiggles=True

    def __init__(self, imgName, rect, maxHealth=50, movable=True, cycleTime=100):
        self.isPlayer = False
        self.imgName = imgName
        self.maxHealth = maxHealth
        self.hp = self.maxHealth
        self.rect = rect
        self.movable = movable
        self.facingRight = True
        self.timer = 0
        self.switchTime = cycleTime
        self.dead = False
        self.lastMove = None
        self.targetable = True
        self.joystick = None
        self.wiggleLeft=False
        self.wiggles=True

        # self.draw=draw

        # self.onClick=onClick

    def damage(self, damage):
        if self.hp - damage <= self.maxHealth:
            self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            self.movable = False
        if self.hp > 0:
            self.dead = False
            self.movable = True

    def move(self, xoff, yoff,camera,model,cached):
        if (not model.world.currentArea.doLinesBlock(self.rect[0],self.rect[1],self.rect[0] + xoff, self.rect[1] + yoff) and not model.world.currentArea.isSquareOpaque(self.rect[0] + xoff, self.rect[1] + yoff, 0, 0,camera,cached)) or  model.world.currentArea.isSquareOpaque(
                self.rect[0], self.rect[1], 0, 0,camera,cached): #if not moving off map, unless already off map
            if self.maxHealth / 2 > self.hp:
                model.world.currentArea.addBlood(self.rect[0], self.rect[1],cached)
            self.rect = (self.rect[0] + xoff,
                         self.rect[1] + yoff,
                         self.rect[2],
                         self.rect[3],)
            if self.isPlayer:
                model.world.reveal(self.rect[0], self.rect[1], camera,cached)
            if xoff > 0:
                self.facingRight = True
            elif xoff < 0:
                self.facingRight = False
            self.lastMove = (xoff, yoff)

    def drawHP(self, screen, camera):
        if self.isPlayer and self.hp < self.maxHealth:
            text = font.render(str(self.hp) + "/" + str(self.maxHealth), 1, (220, 0, 0))
            center = camera.getXYForXY(self.rect[0] + self.rect[2] / 2.0, self.rect[1] + self.rect[3])
            textpos = text.get_rect(centerx=center[0], centery=center[1])
            screen.blit(text, textpos)

    def draw(self, screen, camera,cached,model):
        if self.wiggles and random.random()<.01:
            self.wiggleLeft= not self.wiggleLeft
        if not model.world.currentArea.isShrouded(self.rect,camera):
            self.forcedraw(screen, camera,cached,model)

    def forcedraw(self, screen, camera,cached,model):
        imgs = cached.getImgs(self.imgName)
        portrait = cached.portrait(self.imgName)
        if imgs:
            if not self.dead:
                curImg = imgs[(self.timer / self.switchTime) % len(imgs)]
                drawimg = curImg
                if not self.facingRight:
                    drawimg = pygame.transform.flip(curImg, True, False)
                newrect = curImg.get_rect()
                if not self.rawScaling:
                    drawimg = pygame.transform.scale(drawimg, (camera.gridSize*self.rect[2], int((float(newrect[3])/newrect[2])*self.rect[3]*camera.gridSize)))

                newrect = curImg.get_rect()
                if not self.rawScaling:
                    newrect[0], newrect[1]= (self.rect[0], self.rect[1])
                    newrect = camera.getRectForRect(newrect)
                    newrect = (newrect[0] ,(newrect[1] - (drawimg.get_height() - (self.rect[3] * camera.gridSize))))
                    #drawimg = pygame.transform.rotate(drawimg,self.rotation*90)
                    #drawimg = pygame.transform.scale(drawimg,(drawimg.get_width()*self.rect[2],drawimg.get_height()*self.rect[3]))
                    #newrect = (newrect[0] ,(newrect[1] - (self.rect[3]-1) * camera.gridSize))

                else:
                    newrect[0], newrect[1]= (self.rect[0], self.rect[1])
                    newrect = camera.getRectForRect(newrect)
                    offset = camera.getRectForRect(self.rect)
                    newrect=(offset[0],offset[1],offset[2],offset[3])
                    drawimg = pygame.transform.rotate(drawimg,self.rotation*90)
                    drawimg=pygame.transform.scale(drawimg,(offset[2],offset[3]))

                screen.blit(drawimg, (newrect[0]+self.wiggleLeft*1,newrect[1]))
            else:
                if not portrait:  # something monsterous, draw generic bones
                    deadImg = pygame.transform.scale(cached.getImgs('coreImgs/bones.png')[0],
                                                     (self.rect[2] * camera.gridSize,
                                                      self.rect[3] * camera.gridSize))
                    newrect = deadImg.get_rect()
                    newrect = newrect.move(self.rect[0], self.rect[1])
                    screen.blit(deadImg, camera.getRectForRect(newrect))
                else:  # a main humanoid player
                    deadImg = pygame.transform.rotate(imgs[0], -90)
                    newrect = deadImg.get_rect()
                    newImg = pygame.transform.scale(deadImg, (camera.gridSize, int((float(newrect[3])/newrect[2])*camera.gridSize)))
                    newrect = newImg.get_rect()
                    newrect = newrect.move(self.rect[0], self.rect[1])
                    screen.blit(newImg, camera.getRectForRect(newrect))
        self.drawHP(screen, camera)

    def click(self, x, y, clicktype, camera):
        if self.targetable:
            if camera.inBounds((self.rect[0], self.rect[1],self.rect[2], self.rect[3]), x, y):
                self.onClick(x, y, clicktype, camera)
                return self
    def onDeletePress(self,camera,cached,model):
        if not self.dead:
            self.dead = True
            self.movable = False
            if camera.battleManager:
                camera.battleManager.removePlayer(self)
                camera.target = camera.battleManager.getCurPlayer()
            else:
                camera.target = None
        elif not self.isPlayer:
            self.markedForDeletion = True
            camera.target = None
    def duplicateTo(self,x,y,camera, model):
        duplicate= deepcopy(self)
        duplicate.rect = (x,y, self.rect[2],self.rect[3])
        if duplicate.isPlayer:
            model.world.players.append(duplicate)
        else:
            model.world.currentArea.entities.append(duplicate)
        camera.target=duplicate
