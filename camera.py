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

pygame.font.init()


def isInt(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class Camera():
    def_x = 982
    def_y = 982
    FPS_FONT = pygame.font.Font(None, 18)

    def __init__(self):
        self.currentDescriptionTarget = None
        self.target = None
        self.battleManager = None
        self.x = -10
        self.y = -10
        self.tileSize = 32
        self.dialogTime = 30  # 6sec * 24    fps
        self.isFull = False
        self.drawGrid = True
        self.drawShadows = True
        self.dialogs = {}
        self.doStreaming=True
        self.copyTarget=False
        self.pausingPlayers=False
        self.lookingForJoystickTarget = None
        self.cameraChase = False
        self.set_size(Camera.def_x , Camera.def_y)
        self.recenter(0, 0)

    def set_size(self, w, h):
        pygame.display.set_mode((w, h), pygame.RESIZABLE)
        (self.resx, self.resy) = (w, h)
        #self.tileSize = self.resx / horzTilesPerScreen
        self.calc_derivs()

    def calc_derivs(self):
        self.vertTilesPerScreen =  int(math.ceil(float(self.resy) / self.tileSize))
        self.horzTilesPerScreen =  int(math.ceil(float(self.resx) / self.tileSize))

    def show(self,target):
        self.addDialog(target, 'right')

    def inBounds(self, rect, x, y):
        return x >= rect[0] and x < rect[0] + rect[2] and y >= rect[1] and y < rect[1] + rect[3]

    def recenter(self, x, y):
        self.x = x - (self.resx / 2) / self.tileSize
        self.y = y - (self.resy / 2) / self.tileSize


    def toggleFull(self):
        if self.isFull:
            self.resx, self.resy = (Camera.def_x, Camera.def_y)
            pygame.display.set_mode((self.resx, self.resy), RESIZABLE)
            self.isFull = False
        else:
            self.resx, self.resy = (1920, 1080)
            pygame.display.set_mode((self.resx, self.resy), FULLSCREEN)
            self.isFull = True

    def getCameraCenter(self):
        return (self.x + (self.resx / 2) / self.tileSize,
                self.y + (self.resy / 2) / self.tileSize)

    def xyToModel(self, x, y):
        return (x / self.tileSize + self.x,
                y / self.tileSize + self.y,)

    def getXYForXY(self, x, y):
        return ( (x - self.x) * self.tileSize,
                 (y - self.y) * self.tileSize,)

    def getRectForXY(self, x, y):
        return ((x - self.x) * self.tileSize,
                (y - self.y) * self.tileSize,
                self.tileSize,
                self.tileSize)

    def gridRectToCameraRect(self, rect):
        return ((rect[0] - self.x) * self.tileSize,
                (rect[1] - self.y) * self.tileSize,
                rect[2] * self.tileSize,
                rect[3] * self.tileSize)

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
        rect = self.gridRectToCameraRect(rect)
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
        
    def update(self,model):
        if self.cameraChase:
            x = sum([i.rect[0] for i in model.world.players])/len(model.world.players)
            y = sum([i.rect[1] for i in model.world.players])/len(model.world.players)
            self.recenter(x,y)
        for player in self.dialogs:
            self.dialogs[player]['timeRemaining'] -= 1
        self.dialogs = {key: value for key, value in self.dialogs.iteritems() if value['timeRemaining'] >= 0}


    def drawGridlines(self, cached):
        if self.drawGrid:
            color = (0,0,0)
            width = 1
            for x in range (0, self.resx, self.tileSize):
                pygame.draw.line(cached.screen(self), color, (x,0), (x, self.resy), width)
            for y in range (0, self.resy, self.tileSize):
                pygame.draw.line(cached.screen(self), color, (0,y), (self.resx, y), width)

    def drawWorld(self, model, console,cached):
        tileSize = self.tileSize
        
        if self.battleManager:
            color = (60, 0, 0)
        elif self.doStreaming:
            color = (0, 0, 60)
        else:
            color = (0, 0, 0)

        cached.screen(self).fill(color)
        model.world.draw_world(cached.screen(self), self,cached,model)
        self.drawGridlines(cached)
        model.world.currentArea.drawFogOfWar(cached.screen(self),self,cached)
        self.drawSprites(cached.screen(self),self,cached, model, dm_view = False)
        
        screenshot=None

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
                portrait = cached.getImg(player.imgName, idx=0)
            if portrait:
                newRect = portrait.get_rect()
                newimg = pygame.transform.scale(portrait,(Camera.tileSize*8, int((float(newRect[3])/newRect[2])*Camera.tileSize*8)))
                newRect = newimg.get_rect()
                newRect = newRect.move(runningOffset + borderOffsets[0],
                                       self.resy - newRect[3] - borderOffsets[1])
                cached.screen(self).blit(newimg, newRect)
                #if self.doStreaming:
                #    screenshot.blit(newimg, newRect)
                runningOffset += space + newRect[2]

        space = 10
        runningOffset = 0
        for player in rightDialogs:
            portrait=cached.portrait(player.imgName)
            if not portrait:
                portrait=cached.getImg(player.imgName, idx=0)
            if portrait:
                newRect = portrait.get_rect()
                newimg= pygame.transform.scale(portrait,(self.tileSize*8, int((float(newRect[3])/newRect[2])*self.tileSize*8)))
                newRect = newimg.get_rect()
                newRect = newRect.move(self.resx - runningOffset - borderOffsets[0] - newRect[2],
                                       self.resy - newRect[3] - borderOffsets[1])
                cached.screen(self).blit(newimg, newRect)
                #if self.doStreaming:
                #    screenshot.blit(newimg, newRect)
                runningOffset += space + newRect[2]


        #Things after here are not seen by the remote users
        if self.doStreaming:
            #rect = pygame.Rect(int(0), int(0), int(self.resx), int(self.resy))
            #screenshot = pygame.Surface((int(self.resx), int(self.resy)))
            #screenshot.blit(cached.screen(self), rect, area=rect)
            outFileName=r"screenshots/" + str(datetime.datetime.now().microsecond/10000)
            try:
                pygame.image.save(cached.screen(self), outFileName+'.BMP')
            except:
                pass

        self.drawSprites(cached.screen(self),self,cached, model, dm_view = True)



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

        model.world.currentArea.soundManager.draw(cached.screen(Camera), self, cached ,model)
        model.world.currentArea.drawLines(cached.screen(Camera), self, cached ,model)

        if self.target:
            self.drawHighlight(self.target.rect, (10, 10, 100), 128,cached)



        if console.active:
            console.draw()
            
        #self.showFPS(FPS, cached)

    def drawSprites(self, screen, camera,cached,model, dm_view = False):
        #painters alg
        all_sprites = model.world.currentArea.entities + model.world.players
        all_sprites.sort(key = lambda x : x.rect[3]) #by height
        all_sprites.sort(key = lambda x : x.rect[1]+x.rect[3]) #then by y pos
        for sprite in all_sprites:
            sprite.draw(screen, camera,cached,model, dm_view=dm_view)

    def showFPS(self, fps, model_time, view_time, controler_time, cached):
        start_pos = (5,5)
        v_space = 20
        sum_time = model_time + view_time+ controler_time
        for count, i in enumerate([('FPS: ', fps), ('model_time ', model_time/sum_time) , ('view_time: ', view_time/sum_time) , ('controler_time: ', controler_time/sum_time)]):
            text = Camera.FPS_FONT.render(i[0] + str(i[1]), 1, (220, 0, 0))
            #center = camera.getXYForXY(self.rect[0] + self.rect[2] / 2.0, self.rect[1] + self.rect[3])
            cached.screen(self).blit(text, (start_pos[0], start_pos[1] + count * v_space))

