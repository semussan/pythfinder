
import pygame
from pygame.locals import *
from sound import SoundManager
tileCache={}
imgCache={}
import os
import pdb
def getAllFiles(fileName):
    folder, filePart=os.path.split(fileName)
    namePart=filePart.split('.')[0]
    files = [folder+'/'+f for f in os.listdir(folder) if os.path.isfile(folder+'/'+f) and namePart in f]
    return files

files = [f for f in os.listdir('.') if os.path.isfile(f)]

class Sprite():
    img=None
    picture=None
    soundManager=None
    onClick = lambda self, x,y,clicktype,camera :False
    def onClick(self,x,y,clicktype,camera):
        pass
        #print 'Click for', self.imgName
    def __init__(self,imgName,rect, maxHealth,movable=True, cycleTime=100):


        self.imgName=imgName
        self.maxHealth=maxHealth
        self.hp=self.maxHealth
        self.rect=rect
        self.imgs=[]
        for f in getAllFiles(imgName):
            if 'P.png' in f:
                self.portrait=pygame.image.load(f)
            else:
                self.imgs.append(pygame.image.load(f))
        self.movable=movable
        self.facingRight=True
        getAllFiles(imgName)
        self.timer=0
        self.switchTime=cycleTime
        self.dead=False
        self.deadImg=None

        #self.draw=draw

        #self.onClick=onClick
        
    def damage(self, damage):
        self.hp-=damage
        if self.hp<=0:
            self.dead=True
            self.movable=False
        if self.hp>0:
            self.dead=False
            self.movable=True
            
    def move(self, xoff,yoff):
        if self.movable:
            self.rect=(self.rect[0] + xoff,
                       self.rect[1] + yoff,
                       self.rect[2],
                       self.rect[3],)
            if xoff>0:
                self.facingRight=True
            elif xoff<0:
                self.facingRight=False

    def draw(self, screen, camera):
        #if not self.picture:
        #    self.picture= pygame.transform.scale(self.img, (self.rect[2]*camera.gridSize(),
        #                                                self.rect[3]*camera.gridSize()))
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
            if not self.deadImg:
                self.deadImg= pygame.transform.scale(pygame.image.load('coreImgs/bones.png'), (self.rect[2]*camera.gridSize(),
                                                           self.rect[3]*camera.gridSize()))
            newrect = self.deadImg.get_rect()
            newrect = newrect.move(self.rect[0],self.rect[1])
            screen.blit(self.deadImg,camera.getRectForRect(newrect))   
            
               
    def update(self):
        self.timer+=1
    def click(self, x,y,clicktype,camera):
        if camera.inBounds((0,0,self.rect[2],self.rect[3]),x,y):
            self.onClick(x,y,clicktype,camera)
            return self
            
