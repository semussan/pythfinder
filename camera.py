import pyconsole
import pygame
from pygame.locals import *
import Tkinter, tkFileDialog, tkSimpleDialog
import os
import sys
import datetime
root = Tkinter.Tk()
root.withdraw()
import math


def isInt(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class camera():
    currentDescriptionTarget = None
    target = None
    battleManager = None
    defSubx = 908
    defSuby = 140

    defPadding = 50
    x = -10
    y = -10
    horzTilesPerScreen = 27
    subx, suby = (defPadding, defPadding)
    subwid = 882
    subhig = 670
    vertTilesPerScreen =  int(math.ceil((horzTilesPerScreen*(float(subhig))/float(subwid))))
    dialogTime = 30  # 6sec * 24    fps
    isFull = False
    drawGrid = True
    drawShadows = True
    resx, resy = (defPadding * 2 + subwid, defPadding * 2 + subhig)
    dialogs = {}
    doStreaming=True
    copyTarget=False
    gridSize=subwid / horzTilesPerScreen
    pausingPlayers=False
    lookingForJoystickTarget = None
    cameraChase = False

    def show(self,target):
        self.addDialog(target, 'right')

    def inBounds(self, rect, x, y):
        return x >= rect[0] and x < rect[0] + rect[2] and y >= rect[1] and y < rect[1] + rect[3]

    def recenter(self, x, y):
        self.x = x - self.horzTilesPerScreen / 2
        self.y = y - (self.subhig / 2) / self.gridSize

    def __init__(self):
        self.recenter(0, 0)

    def toggleFull(self):
        if self.isFull:
            self.subx, self.suby = (self.defPadding, self.defPadding)
            self.resx, self.resy = (self.defPadding * 2 + self.subwid, self.defPadding * 2 + self.subhig)
            pygame.display.set_mode((self.resx, self.resy))
            self.isFull = False
        else:
            self.resx, self.resy = (1920, 1080)
            self.subx, self.suby = (self.defSubx, self.defSuby)
            pygame.display.set_mode((self.resx, self.resy), FULLSCREEN)
            self.isFull = True

    def getCameraCenter(self):
        return (self.x + (self.subx + (self.subwid / 2)) / self.gridSize,
                self.y + (self.suby + (self.subhig / 2)) / self.gridSize)

    def xyToModel(self, x, y):
        return ((x - self.subx) / self.gridSize + self.x,
                (y - self.suby) / self.gridSize + self.y,)

    def getXYForXY(self, x, y):
        return (self.subx + (x - self.x) * self.gridSize,
                self.suby + (y - self.y) * self.gridSize,)

    def getRectForXY(self, x, y):
        return (self.subx + (x - self.x) * self.gridSize,
                self.suby + (y - self.y) * self.gridSize,
                self.gridSize,
                self.gridSize)

    def getRectForRect(self, rect):
        return (self.subx + (rect[0] - self.x) * self.gridSize,
                self.suby + (rect[1] - self.y) * self.gridSize,
                rect[2] * self.gridSize,
                rect[3] * self.gridSize)

    def quickFile(self):
        return tkFileDialog.askopenfilename()

    def quickSaveFile(self):
        return tkFileDialog.asksaveasfilename()

    def quickDialog(self, prompt):
        return tkSimpleDialog.askstring("", prompt)

    def quickInit(self, prompt):
        ret = False
        while not ret:
            str = tkSimpleDialog.askstring("", prompt)
            ret = isInt(str)
        return int(str)

    def drawHighlight(self, rect, color, alpha,cached):
        rect = self.getRectForRect(rect)
        trans = pygame.Surface((rect[2], rect[3],))
        trans.set_alpha(alpha)
        trans.fill(color)
        cached.screen(self).blit(trans, (rect[0], rect[1]))

    def clippedXRange(self,reqStart,reqFin,reoff):
        return range(max(self.x, reqStart)-reoff, min(self.x + self.horzTilesPerScreen,reqFin)-reoff)
    def clippedYRange(self,reqStart,reqFin,reoff):
        return range(max(self.y, reqStart)-reoff, min(self.y + self.vertTilesPerScreen,reqFin)-reoff)

    def addDialog(self, player, side,time = None):
        if time:
            self.dialogTime = time
        self.dialogs[player] = {'timeRemaining': self.dialogTime, 'Side': side}

    ##        def drawGridlines(self):
    ##            #gridlines
    ##            if self.drawGrid:
    ##                    if (self.resx,self.resy) not in self.vert:
    ##                            self.vert[(self.resx,self.resy)]=pygame.image.load('coreImgs/vert.png')
    ##                    picture = pygame.transform.scale(self.vert[(self.resx,self.resy)], (3, self.resy))
    ##                    newrect = picture.get_rect()
    ##                    oldpos=0
    ##                    for x in range(0 + (self.subx%self.gridSize), self.resx, self.gridSize):
    ##                            newrect = newrect.move(x-oldpos,0)
    ##                    cached.screen(self).blit(picture, newrect)
    ##                            oldpos=x
    ##
    ##                    if (self.resx,self.resy) not in self.horz:
    ##                            self.horz[(self.resx,self.resy)]=pygame.image.load('coreImgs/horz.png')
    ##                    picture = pygame.transform.scale(self.horz[(self.resx,self.resy)], (self.resx, 3))
    ##                    newrect = picture.get_rect()
    ##                    oldpos=0
    ##                    for y in range(0 + (self.suby%self.gridSize), self.resy, self.gridSize):
    ##                            newrect = newrect.move(0,y-oldpos)
    ##                            cached.screen(self).blit(picture, newrect)
    ##                            oldpos=y
    def update(self,model):
        if self.cameraChase:
            x = sum([i.rect[0] for i in model.world.players])/len(model.world.players)
            y = sum([i.rect[1] for i in model.world.players])/len(model.world.players)
            self.recenter(x,y)
        for player in self.dialogs:
            self.dialogs[player]['timeRemaining'] -= 1
        self.dialogs = {key: value for key, value in self.dialogs.iteritems() if value['timeRemaining'] >= 0}

    def drawWorld(self, model, console,cached):
        gridSize = self.gridSize
        cached.screen(self).fill((0, 0, 0))
        pygame.draw.rect(cached.screen(self), (10, 10, 10), (self.subx, self.suby, self.subwid, self.subhig),
                         0)  # projector sub-screen outline
        # for x, y, image in model.world.tiles:
        #        screen.blit(image, (self.x+x*gridSize +self.subx,self.y+y*gridSize+self.suby))

        # for x, y, wid, hig, image in model.world._imgs:
        #        picture = pygame.transform.scale(image, (wid*gridSize, hig*gridSize))
        #        rect = picture.get_rect()
        #        rect = rect.move((self.x+x*gridSize +self.subx ,self.y+y*gridSize +self.suby))
        #        screen.blit(picture, rect)
        model.world.draw(cached.screen(self), self,cached,model)



        # black-out borders
        if self.battleManager:
            color = (60, 0, 0)
        elif self.doStreaming:
            color = (0, 0, 60)
        else:
            color = (0, 0, 0)

        pygame.draw.rect(cached.screen(self), color, (0, 0, self.resx, self.suby), 0)
        pygame.draw.rect(cached.screen(self), color, (self.subx + self.subwid, 0, self.resx, self.resy), 0)
        pygame.draw.rect(cached.screen(self), color, (0, self.suby + self.subhig, self.resx, self.resy), 0)
        pygame.draw.rect(cached.screen(self), color, (0, 0, self.subx, self.resy), 0)
        if console.active:
            console.draw()

        model.world.currentArea.drawAfter(cached.screen(self),self,cached)
        screenshot=None
        if self.doStreaming:
            rect = pygame.Rect(int(self.subx), int(self.suby), int(self.subwid), int(self.subhig))
            screenshot = pygame.Surface((int(self.subwid), int(self.subhig)))
            screenshot.blit(cached.screen(self), rect, area=rect)

        # Organize Dialogs
        leftDialogs = []
        rightDialogs = []
        for player in self.dialogs:
            if self.dialogs[player]['Side'].lower() == 'left':
                leftDialogs.append(player)
            else:
                rightDialogs.append(player)
        leftDialogs = sorted(leftDialogs, key=lambda x: -self.dialogs[x]['timeRemaining'])
        rightDialogs = sorted(rightDialogs, key=lambda x: -self.dialogs[x]['timeRemaining'])
        # Draw dialogs
        space = 10
        runningOffset = 0
        borderOffsets = (40, 120)
        for player in leftDialogs:
            portrait=cached.portrait(player.imgName)
            if not portrait:
                portrait=cached.getImgs(player.imgName)[0]
            if portrait:
                newRect = portrait.get_rect()
                newimg= pygame.transform.scale(portrait,(camera.gridSize*8, int((float(newRect[3])/newRect[2])*camera.gridSize*8)))
                newRect = newimg.get_rect()
                newRect = newRect.move(self.subx + runningOffset + borderOffsets[0],
                                       self.suby + self.subhig - newRect[3] - borderOffsets[1])
                cached.screen(self).blit(newimg, newRect)
                if self.doStreaming:
                    screenshot.blit(newimg, newRect)
                runningOffset += space + newRect[2]

        space = 10
        runningOffset = 0
        for player in rightDialogs:
            portrait=cached.portrait(player.imgName)
            if not portrait:
                portrait=cached.getImgs(player.imgName)[0]
            if portrait:
                newRect = portrait.get_rect()
                newimg= pygame.transform.scale(portrait,(camera.gridSize*8, int((float(newRect[3])/newRect[2])*camera.gridSize*8)))
                newRect = newimg.get_rect()
                newRect = newRect.move(self.subx + self.subwid - runningOffset - borderOffsets[0] - newRect[2],
                                       self.suby + self.subhig - newRect[3] - borderOffsets[1])
                cached.screen(self).blit(newimg, newRect)
                if self.doStreaming:
                    screenshot.blit(newimg, newRect)
                runningOffset += space + newRect[2]

        if self.doStreaming:
            outFileName=r"screenshots/" + str(datetime.datetime.now().microsecond/10000)
            try:
                pygame.image.save(screenshot, outFileName+'.jpg')
            except:
                pass

        #Things after here are not seen by the remote users


        if self.currentDescriptionTarget and self.currentDescriptionTarget.description:
            tidyDescription= self.currentDescriptionTarget.description.replace('\n','__').replace('\t',' ')
            fontsize=14
            font = pygame.font.Font(None, fontsize)
            chunk_size=180
            spacing = fontsize+3
            chunks = len(tidyDescription)
            chunkedDescription = [ tidyDescription[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
            topOfText=self.resy  -((len(chunkedDescription)+1)*spacing)
            pygame.draw.rect(cached.screen(self), (0,0,0), (0,topOfText,  self.resx, self.resy), 0)
            for i, descChunk in enumerate(chunkedDescription):
                text = font.render(descChunk , 1, (200, 200, 200))
                cached.screen(self).blit(text, (10, i*spacing + topOfText))

        model.world.currentArea.soundManager.draw(cached.screen(camera), self, cached ,model)
        model.world.currentArea.drawLines(cached.screen(camera), self, cached ,model)

        if self.target:
            self.drawHighlight(self.target.rect, (10, 10, 100), 128,cached)


        model.world.currentArea.forceDrawSprites(cached.screen(self),self,cached, model)

