
import pygame
from sprite import Sprite
from pygame.locals import *
import os
import random
import types
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
        if self.fogImg is None:
            self.fogImg=[None for x in range(3)]
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
        self.img=pygame.image.load(imgName)
        #if imgName not in imgCache:
        #    imgCache[imgName]=pygame.image.load(imgName)
            
    def drawGridlines(self,camera):
        #gridlines
        if camera.drawGrid:
                if (self.rect) not in camera.vert:
                        camera.vert[self.rect]=pygame.image.load('coreImgs/vert.png')
                picture = pygame.transform.scale(camera.vert[self.rect], (3, self.rect[3]*camera.gridSize()))
                newrect = picture.get_rect()
                
                xs,ys,ws,hs= camera.getRectForRect(self.rect)
                newrect = newrect.move(0,ys)
                oldpos=0
                for x in range(xs, xs+ws, camera.gridSize()):
                        newrect = newrect.move(x-oldpos,0)
                        camera.screen.blit(picture, newrect)
                        oldpos=x

                if (self.rect) not in camera.horz:
                        camera.horz[self.rect]=pygame.image.load('coreImgs/horz.png')
                picture = pygame.transform.scale(camera.horz[self.rect], (self.rect[2]*camera.gridSize(), 3))
                newrect = picture.get_rect()
                newrect = newrect.move(xs,0)
                oldpos=0
                for y in range(ys, ys+hs, camera.gridSize()):
                        newrect = newrect.move(0,y-oldpos)
                        camera.screen.blit(picture, newrect)
                        oldpos=y            
    def draw(self, screen, camera):
        if self.img is None:
            self.img=pygame.image.load(self.imgName)
            
        picture = pygame.transform.scale(self.img, (self.rect[2]*camera.gridSize(),
                                                                  self.rect[3]*camera.gridSize()))
        newrect = picture.get_rect()
        newrect = newrect.move(self.rect[0],self.rect[1])
        screen.blit(picture, camera.getRectForRect(newrect))
    
        self.drawGridlines(camera)
            
    def drawFoW(self, screen, camera):
        if self.FoW and camera.drawShadows:
            self.FoW.draw(screen, camera)

    def click(self, x,y,clicktype,camera):
        camera.target=None
        if self.FoW and camera.drawShadows:
            self.FoW.click(x,y,clicktype,camera)

    def getBounds(self):
        return self.rect

class World():
    backgrounds=[]
    imgs=[]
    sprites=[]
    blood=[]
    joystickBindings={}
    bloodImgs=None
    def __init__(self,  camera):
        self.camera=camera
        pygame.joystick.init()
        pygame.init() 
    def load(self, mapFileName):
        self.backgrounds=[]
        self.imgs=[]
        self.sprites=[]
        self.blood=[]
        self.camera.soundManager.reset()
        f = open(mapFileName, 'rb')
        subdir='/'.join(('maps/'+mapFileName).split('/')[1:-1]) + '/'
        lastNPC=None
        #LoadWorld
        for mapLine in f:
            parsed=mapLine.strip().split(' ')
            linetype, args = (parsed[0],parsed[1:])
            if linetype == 'background':#img
                x,y,wid,hig,filename, hasShadows = args
                self.backgrounds.append(Background(subdir+filename.strip(),(int(x),int(y),int(wid),int(hig), ), None,hasShadows == 'True' ))
            if linetype == 'sound':#sound
                x,y,vol,filename = args
                self.camera.soundManager.addBG(int(x),int(y),float(vol),subdir+filename.strip())
            if linetype == 'npc':
                x,y,width, height , maxHealth, movable, cycleTime, filename = args
                lastNPC=Sprite(self.camera,subdir+filename.strip(),(int(x),int(y),int(width),int(height), ), int(maxHealth),movable == 'True' , int(cycleTime))
                self.sprites.append(lastNPC)
            if linetype =='interaction' and lastNPC:
                command="def interactionFunc(self): " + " ".join(args)
                exec command
                print interactionFunc
                lastNPC.interaction = types.MethodType( interactionFunc, lastNPC )
        #LoadPlayers
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        playersFile=open(subdir+'players','rb')
        for player in playersFile:
            parsed=player.strip().split(' ')
            linetype, args = (parsed[0],parsed[1:])
            if linetype == 'npc':
                x,y,width, height , maxHealth, movable, cycleTime, filename = args
                newChar=Sprite(self.camera, subdir+filename.strip(),(int(x),int(y),int(width),int(height), ), int(maxHealth),movable == 'True' , int(cycleTime))
                self.sprites.append(newChar)
                if joysticks:
                    newJoystick=joysticks.pop()
                    newJoystick.init()
                    self.joystickBindings[newJoystick]=newChar
        print "Joysticks!", self.joystickBindings
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
        for bloodDrop in self.blood:
            screen.blit(bloodDrop[2],camera.getRectForRect((bloodDrop[0],bloodDrop[1],1,1)))
        if camera.target:
            camera.drawHighlight(camera.target.rect,(10,10,100),128)
        if camera.battleManager and camera.battleManager.started and camera.battleManager.getCurPlayer():
            camera.drawHighlight(camera.battleManager.getCurPlayer().rect,(100,10,10),128)
        for sprite in self.sprites:
            sprite.draw(screen, camera)
        for background in self.backgrounds:
            background.drawFoW(screen, camera)
    def addBlood(self,x,y):
        if not self.bloodImgs:
            bloodDir='./coreImgs/blood/'
            filelist = [bloodDir+f for f in os.listdir(bloodDir)]
            self.bloodImgs=[]
            for filename in filelist:
                self.bloodImgs.append(pygame.image.load(filename))
        self.blood.append((x,y,random.choice(self.bloodImgs)))
        print self.blood
    def update(self):
          self.sprites=sorted(self.sprites, key=lambda x: x.rect[1])#sort by height
          for sprite in self.sprites:
              numUpdates=4 if self.camera.battleManager else 1
              for x in range(numUpdates):
                  sprite.update()
    def interact(self, player):
        if player.lastMove:
            px,py=player.rect[0],player.rect[1]
            x,y=(player.lastMove[0]+px,player.lastMove[1]+py)#get where the player was 'facing'
            for sprite in self.sprites:
                if self.camera.inBounds(sprite.rect, x,y):
                    if sprite.interaction:
                        sprite.interaction()
                    return
            
    def click(self, x,y,clicktype,camera, newClick):
        if newClick:
            for sprite in self.sprites:
                ret= sprite.click(x-sprite.rect[0],y-sprite.rect[1],clicktype,camera)
                if ret: return ret
        for background in self.backgrounds:
            if camera.inBounds(background.getBounds(),x,y):
                background.click(x-background.rect[0],y-background.rect[1],clicktype,camera)
