
import pygame
from sprite import Sprite
from pygame.locals import *
from sound import SoundManager
tileCache={}
imgCache={}



def getNeighbors(widthx,widthy,x,y,camera):
    posibleNeighbors=[(x-1,y),(x+1,y) ,(x,y-1) ,(x,y+1),
                       (x-2,y),(x+2,y) ,(x,y-2) ,(x,y+2),
                       (x-1,y-1),(x-1,y+1) ,(x+1,y-1) ,(x+1,y+1)]
    neighbors=[]
    for neighbor in posibleNeighbors:
        if camera.inBounds((0,0,widthx,widthy),neighbor[0],neighbor[1]):
            neighbors.append(neighbor)
    return neighbors

class FoWMap():
    fogImg=[None for x in range(3)]
    def __init__(self,rect,hasShadows):
        level=0
        if hasShadows:
            level=2
            
        self.foglevels=[[level for x in range(rect[3])] for x in range(rect[2])]
        self.rect=rect


    def drawSingleFoW(self, screen, camera, x,y,level):
        rect=camera.getRectForXY(self.rect[0]+x,self.rect[1]+y)
        if self.fogImg[level] is None:
            trans=pygame.Surface((rect[2],rect[3],))
            trans.set_alpha(level*128)
            trans.fill((10,10,10))
            self.fogImg[level]=trans
        screen.blit(self.fogImg[level], (rect[0],rect[1]))
        #pygame.draw.rect(screen,(level*30,0,0),rect,0)
        
    def draw(self, screen, camera):
        for x in range(self.rect[2]):
            for y in range(self.rect[3]):
                if self.foglevels[x][y]>0:
                    self.drawSingleFoW(screen, camera, x,y,self.foglevels[x][y])
                    
    def click(self, x,y,clicktype,camera):
        camera.target=None
        if clicktype==1:
            self.foglevels[x][y]=0
            for neighbor in getNeighbors(self.rect[2],self.rect[3],x,y,camera):
                if self.foglevels[neighbor[0]][neighbor[1]]>0:
                    if abs(neighbor[0]-x)+abs(neighbor[1]-y)<=1:
                        self.foglevels[neighbor[0]][neighbor[1]]=0
                    else:
                        self.foglevels[neighbor[0]][neighbor[1]]=1
        if clicktype==2:
            if self.foglevels[x][y] is not 2:
                self.foglevels[x][y]=1#was 2
            for neighbor in getNeighbors(self.rect[2],self.rect[3],x,y,camera):
                if self.foglevels[neighbor[0]][neighbor[1]]<2:
                    if abs(neighbor[0]-x)+abs(neighbor[1]-y)<=1:
                        self.foglevels[neighbor[0]][neighbor[1]]=1 #was 2
                    else:
                        self.foglevels[neighbor[0]][neighbor[1]]=1
        if clicktype==3:
            self.foglevels[x][y]=2#was 2
            for neighbor in getNeighbors(self.rect[2],self.rect[3],x,y,camera):
                if self.foglevels[neighbor[0]][neighbor[1]]<2:
                    if abs(neighbor[0]-x)+abs(neighbor[1]-y)<=1:
                        self.foglevels[neighbor[0]][neighbor[1]]=2 #was 2
                    else:
                        self.foglevels[neighbor[0]][neighbor[1]]=2
        #print self.foglevels[x][y]

class Background():
    def __init__(self,imgName,rect,entryPoint, hasShadows):
        self.imgName=imgName
        self.rect=rect
        self.hasShadows=hasShadows
        self.FoW=FoWMap(rect,hasShadows)
        if imgName not in imgCache:
            imgCache[imgName]=pygame.image.load(imgName)
            
    def draw(self, screen, camera):
        picture = pygame.transform.scale(imgCache[self.imgName], (self.rect[2]*camera.gridSize(),
                                                                  self.rect[3]*camera.gridSize()))
        newrect = picture.get_rect()
        newrect = newrect.move(self.rect[0],self.rect[1])
        screen.blit(picture, camera.getRectForRect(newrect))
            
    def drawFoW(self, screen, camera):
        if self.FoW and camera.drawShadows:
            self.FoW.draw(screen, camera)

    def click(self, x,y,clicktype,camera):
        camera.target=None
        if self.FoW and camera.drawShadows:
            self.FoW.click(x,y,clicktype,camera)

    def getBounds(self):
        return self.rect

class world():
    backgrounds=[]
    imgs=[]
    soundManager=None
    sprites=[]
    def __init__(self, screen, camera):
        self.screen=screen
        self.camera=camera
        self.soundManager=SoundManager(camera)
        pygame.init() 
    def load(self, mapFileName):
        self.backgrounds=[]
        self.imgs=[]
        self.sprites=[]
        self.soundManager.reset()
        f = open(mapFileName, 'rb')
        subdir='/'.join(('maps/'+mapFileName).split('/')[1:-1]) + '/' 
        for mapLine in f:
            parsed=mapLine.strip().split(' ')
            linetype, args = (parsed[0],parsed[1:])
            if linetype == 'background':#img
                x,y,wid,hig,filename, hasShadows = args
                self.backgrounds.append(Background(subdir+filename.strip(),(int(x),int(y),int(wid),int(hig), ), None,hasShadows == 'True' ))
            if linetype == 'sound':#sound
                x,y,vol,filename = args
                self.soundManager.addBG(int(x),int(y),float(vol),subdir+filename.strip())
            if linetype == 'npc':
                x,y,width, height , movable, filename = args
                self.sprites.append(Sprite(subdir+filename.strip(),(int(x),int(y),int(width),int(height), ),movable == 'True' ,))
            
            #if linetype is 't':#tile
            #    x,y,filename = args
            #    if filename not in tileCache:
            #        tileCache[filename]=pygame.image.load(subdir+filename)
            #    self.tiles.append((int(x),int(y),tileCache[filename]))
            #print x, y
            
    def drawHighlight(self, screen, camera, rect):
        rect=camera.getRectForRect(rect)
        trans=pygame.Surface((rect[2],rect[3],))
        trans.set_alpha(128)
        trans.fill((10,10,100))
        screen.blit(trans, (rect[0],rect[1]))
        
    def draw(self,screen,camera):
        for background in self.backgrounds:
            background.draw(screen, camera)
        if camera.target:
            camera.drawHighlight(camera.target.rect,(10,10,100),128)
        if camera.battleManager and camera.battleManager.started and camera.battleManager.getCurPlayer():
            camera.drawHighlight(camera.battleManager.getCurPlayer().rect,(100,10,10),128)
        for sprite in self.sprites:
            sprite.draw(screen, camera)
        for background in self.backgrounds:
            background.drawFoW(screen, camera)
            
    def update(self):
          self.soundManager.update()
          for sprite in self.sprites:
              numUpdates=4 if self.camera.battleManager else 1
              for x in range(numUpdates):
                  sprite.update()
    def click(self, x,y,clicktype,camera):
        for sprite in self.sprites:
            ret= sprite.click(x-sprite.rect[0],y-sprite.rect[1],clicktype,camera)
            if ret: return ret
        for background in self.backgrounds:
            if camera.inBounds(background.getBounds(),x,y):
                background.click(x-background.rect[0],y-background.rect[1],clicktype,camera)
