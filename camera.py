
import pyconsole
import pygame
from pygame.locals import *
import Tkinter, tkFileDialog, tkSimpleDialog

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
        defResx=1224
        defResy=868
        x=-10
        y=-10
        horzTilesPerScreen=42
        subx=130
        suby=140
        subwid=882
        subhig=670
        isFull=False
        drawGrid=True
        drawShadows=True
        vert={}
        horz={}
        resx=defResx
        resy=defResy
        def inBounds(self,rect,x,y):
            if x>=rect[0] and x<rect[0]+rect[2] and y>=rect[1] and y<rect[1]+rect[3]:
                return True
            else:
                return False

        def __init__(self, screen):
                self.screen=screen

        def toggleFull(self):
                if self.isFull:
                        self.resx, self.resy =(self.defResx,self.defResy)
                        pygame.display.set_mode((self.resx, self.resy))
                        self.isFull=False
                else:
                        self.resx, self.resy =(1920,1080)
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
                    
                #gridlines
                if self.drawGrid:
                        if (self.resx,self.resy) not in self.vert:
                                self.vert[(self.resx,self.resy)]=pygame.image.load('coreImgs/vert.png')
                        picture = pygame.transform.scale(self.vert[(self.resx,self.resy)], (3, self.resy))
                        newrect = picture.get_rect()
                        oldpos=0
                        for x in range(0 + (self.subx%self.gridSize()), self.resx, self.gridSize()):
                                newrect = newrect.move(x-oldpos,0)
                                self.screen.blit(picture, newrect)
                                oldpos=x

                        if (self.resx,self.resy) not in self.horz:
                                self.horz[(self.resx,self.resy)]=pygame.image.load('coreImgs/horz.png')
                        picture = pygame.transform.scale(self.horz[(self.resx,self.resy)], (self.resx, 3))
                        newrect = picture.get_rect()
                        oldpos=0
                        for y in range(0 + (self.suby%self.gridSize()), self.resy, self.gridSize()):
                                newrect = newrect.move(0,y-oldpos)
                                self.screen.blit(picture, newrect)
                                oldpos=y

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

