
import pygame
from pygame.locals import *
from sound import SoundManager
import os
import pdb


pygame.font.init()
font = pygame.font.Font(None, 10)
class Sprite():
    picture=None
    interaction=None
    onClick = lambda self, x,y,clicktype,camera :False
    def onClick(self,x,y,clicktype,camera):
        pass
        #print 'Click for', self.imgName
    def getAllFiles(self, fileName):
        folder, filePart=os.path.split(fileName)
        namePart=filePart.split('.')[0]
        files = [folder+'/'+f for f in os.listdir(folder) if os.path.isfile(folder+'/'+f) and namePart in f]
        return files
    def clearImgs(self):
        self.imgName=''
        self.imgs=[]
    def show(self):
        self.camera.addDialog(self,'right')
    def loadImgs(self,imgName):
        self.imgName=imgName
        self.imgs=[]
        self.portrait=None
        for f in self.getAllFiles(imgName):
            if 'P.png' in f:
                self.portrait=pygame.image.load(f)
            else:
                self.imgs.append(pygame.image.load(f))
    def __init__(self,model,camera,imgName,rect, maxHealth=50,movable=True, cycleTime=100):
        self.model=model
        self.camera=camera
        self.isPlayer=False
        self.imgName=imgName
        self.maxHealth=maxHealth
        self.hp=self.maxHealth
        self.rect=rect
        self.loadImgs(imgName)
        self.movable=movable
        self.facingRight=True
        self.timer=0
        self.switchTime=cycleTime
        self.dead=False
        self.deadImg=None
        self.lastMove=None
        self.targetable=True

        #self.draw=draw

        #self.onClick=onClick
        
    def damage(self, damage):
        if self.hp-damage<=self.maxHealth:
            self.hp-=damage
        if self.hp<=0:
            self.dead=True
            self.movable=False
        if self.hp>0:
            self.dead=False
            self.movable=True
            
    def move(self, xoff,yoff):
        if self.movable:
            if self.maxHealth/2>self.hp:
                self.model.world.addBlood(self.rect[0],self.rect[1])
            self.rect=(self.rect[0] + xoff,
                       self.rect[1] + yoff,
                       self.rect[2],
                       self.rect[3],)
            self.model.world.reveal(self.rect[0],self.rect[1],self.camera)
            if xoff>0:
                self.facingRight=True
            elif xoff<0:
                self.facingRight=False
            self.lastMove=(xoff,yoff)
    def drawHP(self, screen, camera):
        if self.isPlayer and self.hp<self.maxHealth:
            text = font.render(str(self.hp)+"/"+str(self.maxHealth) , 1, (255, 255, 255))
            center=camera.getXYForXY(self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3])
            textpos = text.get_rect(centerx=center[0],centery=center[1])
            screen.blit(text, textpos)
            
    def draw(self, screen, camera):
        #if not self.picture:
        #    self.picture= pygame.transform.scale(self.img, (self.rect[2]*camera.gridSize(),
        #                                                self.rect[3]*camera.gridSize()))
        if self.imgs is None:
            self.loadImgs(self.imgName)
        if self.imgs:
            if not self.dead:
                curImg=self.imgs[(self.timer/self.switchTime)%len(self.imgs)]
                drawimg=curImg
                if not self.facingRight:
                    drawimg=pygame.transform.flip(curImg,True,False)
                    
                newrect = curImg.get_rect()
                newrect[0], newrect[1] = (self.rect[0],self.rect[1])
                newrect=camera.getRectForRect(newrect)
                newrect=(newrect[0],newrect[1]-(curImg.get_height()-(self.rect[3]*camera.gridSize())),
                         newrect[2],newrect[3])
                screen.blit(drawimg,newrect)       
            else:
                if not self.portrait:
                    if not self.deadImg:
                        self.deadImg= pygame.transform.scale(pygame.image.load('coreImgs/bones.png'), (self.rect[2]*camera.gridSize(),
                                                                   self.rect[3]*camera.gridSize()))
                    newrect = self.deadImg.get_rect()
                    newrect = newrect.move(self.rect[0],self.rect[1])
                    screen.blit(self.deadImg,camera.getRectForRect(newrect))
                else:
                    if not self.deadImg:
                        self.deadImg= pygame.transform.rotate(self.imgs[0] ,-90)
                    newrect = self.deadImg.get_rect()
                    newrect = newrect.move(self.rect[0],self.rect[1])
                    screen.blit(self.deadImg,camera.getRectForRect(newrect))
        self.drawHP(screen,camera)
            
               
    def update(self):
        self.timer+=1
    def click(self, x,y,clicktype,camera):
        if self.targetable:
            if camera.inBounds((0,0,self.rect[2],self.rect[3]),x,y):
                self.onClick(x,y,clicktype,camera)
                return self
            
