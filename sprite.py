
import pygame
from pygame.locals import *
from sound import SoundManager
tileCache={}
imgCache={}

        
def inBounds(rect,x,y):
    if x>=rect[0] and x<rect[0]+rect[2] and y>=rect[1] and y<rect[1]+rect[3]:
        return True
    else:
        return False

class Sprite():
    img=None
    picture=None
    soundManager=None
    onClick = lambda self, x,y,clicktype,camera :False
    def onClick(self,x,y,clicktype,camera):
        print 'Click for', self.imgName
    def __init__(self,imgName,rect,movable=True):


        self.imgName=imgName
        self.rect=rect
        self.img=pygame.image.load(self.imgName)

        #self.draw=draw

        #self.onClick=onClick

    def draw(self, screen, camera):
        if not self.picture:
            self.picture= pygame.transform.scale(self.img, (self.rect[2]*camera.gridSize(),
                                                        self.rect[3]*camera.gridSize()))
        newrect = self.picture.get_rect()
        newrect[0], newrect[1] = (self.rect[0],self.rect[1])
        screen.blit(self.picture, camera.getRectForRect(newrect))        
    def update(self):
          pass                       
    def click(self, x,y,clicktype,camera):
        if camera.inBounds((0,0,self.rect[0],self.rect[1]),x,y):
            self.onClick(x,y,clicktype,camera)
            return True
            
