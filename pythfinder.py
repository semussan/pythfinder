
import pygame
from pygame.locals import *
screen = None
BLACK= (0,0,0)
running = True

class world():
        tiles=[]
        imgs=[]
        tileCache={}
        imgCache={}
        def load_submap(self, mapFileName):
                f = open('maps/'+mapFileName, 'rb')
                subdir='/'.join(('maps/'+mapFileName).split('/')[:-1]) + '/' 
                for mapLine in f:
                        parsed=mapLine.strip().split(' ')
                        linetype, args = (parsed[0],parsed[1:])
                        if linetype is 'i':#img
                                x,y,wid,hig,filename = args
                                if filename not in self.imgCache:
                                        self.imgCache[filename]=pygame.image.load(subdir+filename)
                                self.imgs.append((int(x),int(y),int(wid),int(hig),self.imgCache[filename]))
                        if linetype is 't':#tile
                                x,y,filename = args
                                if filename not in self.tileCache:
                                        self.tileCache[filename]=pygame.image.load(subdir+filename)
                                self.tiles.append((int(x),int(y),self.tileCache[filename]))
                        print x, y
class char():
        x=50
        y=50
class model():
        char=char()
        world=world()
def drawAt(imgName, x,y):
        img = pygame.image.load(imgName)
        screen.blit(img, (x,y))
        pygame.display.flip()
class feyAdventure():
        model=None
        def __init__(self):
                self.model=model()
                self.model.world.load_submap('fey/bridge.map')
        

def handle_user_input(model,camera):
        gridSize=camera.subwid/camera.horzTilesPerScreen
        for event in pygame.event.get():
                if not hasattr(event, 'key'): continue
                down = event.type == KEYDOWN
                if down:
                        if event.key==K_RIGHT:
                                camera.x-=gridSize
                        elif event.key==K_LEFT:
                                camera.x+=gridSize
                        elif event.key==K_UP:
                                camera.y+=gridSize
                        elif event.key==K_DOWN:
                                camera.y-=gridSize
                        elif event.type==KEYDOWN and event.key == pygame.K_ESCAPE:
                                print 'Quitting'
                                running = False  # Be interpreter friendly           
                                pygame.quit()


class camera():
        x=0
        y=0
        horzTilesPerScreen=20
        resx=1024
        resy=768
        subx=100
        suby=100
        subwid=800
        subhig=600
def drawWorld(model, camera):
        gridSize=camera.subwid/camera.horzTilesPerScreen
        
        screen.fill(BLACK)
        pygame.draw.rect(screen,(20,20,20),(camera.subx,camera.suby,camera.subwid,camera.subhig),0) #projector sub-screen outline
        for x, y, image in model.world.tiles:
                screen.blit(image, (camera.x+x*gridSize +camera.subx,camera.y+y*gridSize+camera.suby))
                
        for x, y, wid, hig, image in model.world.imgs:
                picture = pygame.transform.scale(image, (wid*gridSize, hig*gridSize))
                rect = picture.get_rect()
                rect = rect.move((camera.x+x*gridSize +camera.subx ,camera.y+y*gridSize +camera.suby))
                screen.blit(picture, rect)

        #gridlines
        for x in range(0 - (camera.subx%gridSize), camera.resx, gridSize):
                pygame.draw.line(screen, (60,0,0), (x,0),(x,camera.resy))
        for y in range(0 - (camera.suby%gridSize), camera.resy, gridSize):
                pygame.draw.line(screen, (60,0,0), (0,y),(camera.resx,y))

        #black-out borders
        pygame.draw.rect(screen,(0,0,0),(0,0,camera.resx,camera.suby),0)
        pygame.draw.rect(screen,(0,0,0),(camera.subx+camera.subwid,0,camera.resx,camera.resy),0)
        pygame.draw.rect(screen,(0,0,0),(0,camera.suby+camera.subhig,camera.resx,camera.resy),0)
        pygame.draw.rect(screen,(0,0,0),(0,0,camera.subx,camera.resy),0)
                

        


if __name__ == '__main__':
        camera=camera()
        screen = pygame.display.set_mode((camera.resx,camera.resy), DOUBLEBUF)
        adv=feyAdventure()
        model=adv.model
        clock = pygame.time.Clock()
        FRAMES_PER_SECOND = 30
        while running:
                handle_user_input(model,camera)
                drawWorld(model, camera)
                drawAt('chars/c1.png', model.char.x,model.char.y)
                pygame.display.update()
                deltat = clock.tick(FRAMES_PER_SECOND)     
                
        
