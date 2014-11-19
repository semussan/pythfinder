
import pygame
from pygame.locals import *
tileCache={}
imgCache={}

        
def inBounds(rect,x,y):
    if x>=rect[0] and x<rect[0]+rect[2] and y>=rect[1] and y<rect[1]+rect[3]:
        return True
    else:
        return False


def getNeighbors(widthx,widthy,x,y):
    posibleNeightbors=[(x-1,y),(x+1,y) ,(x,y-1) ,(x,y+1)]
    neighbors=[]
    for neighbor in posibleNeightbors:
        if inBounds((0,0,widthx,widthy),x,y):
            neighbors.append(neighbor)
    return neighbors

class FoWMap():
    fogImg=[None for x in range(3)]
    def __init__(self,rect):
        self.foglevels=[[2 for x in range(rect[3]+1)] for x in range(rect[2]+1)]
        self.rect=rect


    def drawSingleFoW(self, screen, camera, x,y,level):
        rect=camera.getRectForXY(self.rect[0]+x,self.rect[1]+y)
        if self.fogImg[level] is None:
            trans=pygame.Surface((rect[2],rect[3],))
            trans.set_alpha(level*128)
            trans.fill((0,0,0))
            self.fogImg[level]=trans
        screen.blit(self.fogImg[level], (rect[0],rect[1]))
        #pygame.draw.rect(screen,(level*30,0,0),rect,0)
        
    def draw(self, screen, camera):
        for x in range(self.rect[2]):
            for y in range(self.rect[3]):
                if self.foglevels[x][y]>0:
                    self.drawSingleFoW(screen, camera, x,y,self.foglevels[x][y])
                    
    def click(self, x,y,clicktype):
        if clicktype==1:
            self.foglevels[x][y]=0
            neighbors=[(x-1,y),(x+1,y) ,(x,y-1) ,(x,y+1)]
            for neighbor in getNeighbors(self.rect[2],self.rect[3],x,y):
                if self.foglevels[neighbor[0]][neighbor[1]]>0:
                    self.foglevels[neighbor[0]][neighbor[1]]=1
        if clicktype==2:
            self.foglevels[x][y]=2
            neighbors=[(x-1,y),(x+1,y) ,(x,y-1) ,(x,y+1)]
            for neighbor in getNeighbors(self.rect,x,y):
                if self.foglevels[neighbor[0]][neighbor[1]]<2:
                    self.foglevels[neighbor[0]][neighbor[1]]=1
        print self.foglevels[x][y]

class Background():
    def __init__(self,imgName,rect,entryPoint):
        self.imgName=imgName
        self.FoW=FoWMap(rect)
        self.rect=rect
        if imgName not in imgCache:
            imgCache[imgName]=pygame.image.load(imgName)
            
    def draw(self, screen, camera):
        picture = pygame.transform.scale(imgCache[self.imgName], (self.rect[2]*camera.gridSize(),
                                                                  self.rect[3]*camera.gridSize()))
        newrect = picture.get_rect()
        newrect = newrect.move(self.rect[0],self.rect[1])
        screen.blit(picture, camera.getRectForRect(newrect))
        self.FoW.draw(screen, camera)

    def click(self, x,y,clicktype):
        self.FoW.click(x,y,clicktype)

    def getBounds(self):
        return self.rect

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
                x,y,wid,hig,filename = args
                self.backgrounds.append(Background(subdir+filename,(int(x),int(y),int(wid),int(hig)), None))
            #if linetype is 't':#tile
            #    x,y,filename = args
            #    if filename not in tileCache:
            #        tileCache[filename]=pygame.image.load(subdir+filename)
            #    self.tiles.append((int(x),int(y),tileCache[filename]))
            #print x, y
    def click(self, x,y,clicktype):
        for background in self.backgrounds:
            if inBounds(background.getBounds(),x,y):
                background.click(x-background.rect[0],y-background.rect[1],clicktype)
