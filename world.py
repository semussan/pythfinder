
import pygame

tileCache={}
imgCache={}



from pygame.locals import *

class FoWMap():
    def __init__(self,rect):
        self.foglevels=[[2 for x in range(rect[3])] for x in range(rect[2])]


    def drawSingleFoW(self, screen, camera, x,y,level):
        rect=camera.getRectForXY(x,y)
        pygame.draw.rect(screen,(60,0,0),rect,0)
    def draw(self, screen, camera):
        for x in range(len(self.foglevels)):
            for y in range(len(self.foglevels[0])):
                if self.foglevels[x][y]>0:
                    self.drawSingleFoW(screen, camera, x,y,self.foglevels[x][y])
                    
    def click(self, x,y,clicktype):
        if self.foglevels[x][y] >0:
            print x,y
            self.foglevels[x][y]-=1      

class Background():
    def __init__(self,imgName,rect,entryPoint):
        self.FoW=FoWMap(rect)
        self.imgName=imgName
        self.wid=rect[2]-rect[0]
        self.hig=rect[3]-rect[1]
        self.rect=rect
        if imgName not in imgCache:
            imgCache[imgName]=pygame.image.load(imgName)
            
    def draw(self, screen, camera):
        picture = pygame.transform.scale(imgCache[self.imgName], (self.wid*camera.gridSize(), self.hig*camera.gridSize()))
        newrect = picture.get_rect()
        newrect = newrect.move(camera.getXYForXY(newrect[0],newrect[1]))
        screen.blit(picture, camera.getRectForRect(self.rect))
        self.FoW.draw(screen, camera)

    def click(self, x,y,clicktype):
        self.FoW.click(x,y,clicktype)

    def getBounds(self):
        return self.rect
            
        
def inBounds(rect,x,y):
    if x>=rect[0] and x<rect[2] and y>=rect[1] and y<rect[3]:
        return True
    else:
        return False

class world():
    backgrounds=[]
    imgs=[]
    def load_submap(self, mapFileName):
        f = open('maps/'+mapFileName, 'rb')
        subdir='/'.join(('maps/'+mapFileName).split('/')[:-1]) + '/' 
        for mapLine in f:
            parsed=mapLine.strip().split(' ')
            linetype, args = (parsed[0],parsed[1:])
            if linetype is 'i':#img
                x,y,x2,y2,filename = args
                self.backgrounds.append(Background(subdir+filename,(int(x),int(y),int(x2),int(y2)), None))
            #if linetype is 't':#tile
            #    x,y,filename = args
            #    if filename not in tileCache:
            #        tileCache[filename]=pygame.image.load(subdir+filename)
            #    self.tiles.append((int(x),int(y),tileCache[filename]))
            #print x, y
    def click(self, x,y,clicktype):
        for background in self.backgrounds:
            if inBounds(background.getBounds(),x,y):
                background.click(x,y,clicktype)
