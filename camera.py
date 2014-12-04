
import pyconsole
import pygame
from pygame.locals import *
import Tkinter, tkFileDialog, tkSimpleDialog
from sound import SoundManager

root = Tkinter.Tk()
root.withdraw()
def isInt(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class camera():
        target=None
        battleManager=None
        defSubx=908
        defSuby=140
        defPadding=20
        x=-10
        y=-10
        horzTilesPerScreen=42
        subx, suby =(defPadding,defPadding)
        subwid=882
        subhig=670
        dialogTime=6*40 #6sec * 40fps
        isFull=False
        drawGrid=True
        drawShadows=True
        vert={}
        horz={}
        resx, resy =(defPadding*2+subwid,defPadding*2+subhig)
        dialogs={}
        soundManager=None

        
        def inBounds(self,rect,x,y):
            if x>=rect[0] and x<rect[0]+rect[2] and y>=rect[1] and y<rect[1]+rect[3]:
                return True
            else:
                return False

        def __init__(self, screen):
                self.screen=screen
                self.soundManager=SoundManager(self)

        def toggleFull(self):
                if self.isFull:
                        self.subx, self.suby =(self.defPadding,self.defPadding)
                        self.resx, self.resy =(self.defPadding*2+self.subwid,self.defPadding*2+self.subhig)
                        pygame.display.set_mode((self.resx, self.resy))
                        self.isFull=False
                else:
                        self.resx, self.resy =(1920,1080)
                        self.subx, self.suby =(self.defSubx,self.defSuby)
                        pygame.display.set_mode((self.resx,self.resy),  FULLSCREEN)
                        self.isFull=True

        def getCameraCenter(self):
            return (self.x+ (self.subx+(self.subwid/2))/self.gridSize(),
                    self.y+ (self.suby+(self.subhig/2))/self.gridSize())      
        def xyToModel(self,x,y):
            return ((x-self.subx)/self.gridSize()+self.x,
                    (y-self.suby)/self.gridSize()+self.y,)
                                  
        def gridSize(self):
            return self.subwid/self.horzTilesPerScreen
        
        def getXYForXY(self,x,y):
            return (self.subx+(x-self.x)*self.gridSize(),
                    self.suby+(y-self.y)*self.gridSize(),)
                    
        def getRectForXY(self,x,y):
            return (self.subx+(x-self.x)*self.gridSize(),
                    self.suby+(y-self.y)*self.gridSize(),
                    self.gridSize(),
                    self.gridSize())
        def getRectForRect(self,rect):
            return (self.subx+(rect[0]-self.x)*self.gridSize(),
                    self.suby+(rect[1]-self.y)*self.gridSize(),
                    rect[2]*self.gridSize(),
                    rect[3]*self.gridSize())
        def quickFile(self):
                return tkFileDialog.askopenfilename()
        def quickSaveFile(self):
                return tkFileDialog.asksaveasfilename()
        def quickDialog(self,prompt):
                return tkSimpleDialog.askstring("",prompt)
        def quickInt(self,prompt):
                ret=False
                while not ret:
                        str=tkSimpleDialog.askstring("",prompt)
                        ret=isInt(str)
                return int(str)
        def drawHighlight(self, rect, color, alpha):
                rect=self.getRectForRect(rect)
                trans=pygame.Surface((rect[2],rect[3],))
                trans.set_alpha(alpha)
                trans.fill(color)
                self.screen.blit(trans, (rect[0],rect[1]))
        def addDialog(self,player,side):
            self.dialogs[player]={'timeRemaining':self.dialogTime,'Side':side}
                
##        def drawGridlines(self):
##            #gridlines
##            if self.drawGrid:
##                    if (self.resx,self.resy) not in self.vert:
##                            self.vert[(self.resx,self.resy)]=pygame.image.load('coreImgs/vert.png')
##                    picture = pygame.transform.scale(self.vert[(self.resx,self.resy)], (3, self.resy))
##                    newrect = picture.get_rect()
##                    oldpos=0
##                    for x in range(0 + (self.subx%self.gridSize()), self.resx, self.gridSize()):
##                            newrect = newrect.move(x-oldpos,0)
##                            self.screen.blit(picture, newrect)
##                            oldpos=x
##
##                    if (self.resx,self.resy) not in self.horz:
##                            self.horz[(self.resx,self.resy)]=pygame.image.load('coreImgs/horz.png')
##                    picture = pygame.transform.scale(self.horz[(self.resx,self.resy)], (self.resx, 3))
##                    newrect = picture.get_rect()
##                    oldpos=0
##                    for y in range(0 + (self.suby%self.gridSize()), self.resy, self.gridSize()):
##                            newrect = newrect.move(0,y-oldpos)
##                            self.screen.blit(picture, newrect)
##                            oldpos=y
        def update(self):
            self.soundManager.update()
            for player in self.dialogs:
                self.dialogs[player]['timeRemaining']-=1
            self.dialogs={key:value for key,value in self.dialogs.iteritems() if value['timeRemaining']>=0}
        def drawWorld(self,model,console):
                gridSize=self.gridSize
                
                self.screen.fill((0,0,0))
                pygame.draw.rect(self.screen,(10,10,10),(self.subx,self.suby,self.subwid,self.subhig),0) #projector sub-screen outline
                #for x, y, image in model.world.tiles:
                #        screen.blit(image, (self.x+x*gridSize +self.subx,self.y+y*gridSize+self.suby))
                        
                #for x, y, wid, hig, image in model.world.imgs:
                #        picture = pygame.transform.scale(image, (wid*gridSize, hig*gridSize))
                #        rect = picture.get_rect()
                #        rect = rect.move((self.x+x*gridSize +self.subx ,self.y+y*gridSize +self.suby))
                #        screen.blit(picture, rect)
                model.world.draw(self.screen, self)
                    


                #black-out borders
                if not self.battleManager:
                        color=(0,0,0)
                else:
                        color=(60,0,0)
                pygame.draw.rect(self.screen,color,(0,0,self.resx,self.suby),0)
                pygame.draw.rect(self.screen,color,(self.subx+self.subwid,0,self.resx,self.resy),0)
                pygame.draw.rect(self.screen,color,(0,self.suby+self.subhig,self.resx,self.resy),0)
                pygame.draw.rect(self.screen,color,(0,0,self.subx,self.resy),0)
                if console.active:
                        console.draw()

                #Organize Dialogs
                leftDialogs=[]
                rightDialogs=[]
                for player in self.dialogs:
                    if self.dialogs[player]['Side'].lower()=='left':
                        leftDialogs.append(player)
                    else:
                        rightDialogs.append(player)
                leftDialogs = sorted(leftDialogs, key=lambda x:-self.dialogs[x]['timeRemaining'])
                rightDialogs = sorted(rightDialogs, key=lambda x:-self.dialogs[x]['timeRemaining'])
                #Draw dialogs
                space=10
                runningOffset=0
                borderOffsets=(40,120)
                for player in leftDialogs:
                    if player.portrait:
                        #ar=float(player.rect[2])/player.rect[3]
                        newRect=player.portrait.get_rect()
                        newRect=newRect.move(self.subx+runningOffset+borderOffsets[0],
                                             self.suby+self.subhig-newRect[3]-borderOffsets[1])
                        self.screen.blit(player.portrait, newRect)
                        runningOffset+=space+newRect[2]
                        
                    
                    

