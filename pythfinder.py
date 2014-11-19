
import pygame
import copy
from world import world
from camera import camera
from pygame.locals import *
from collections import defaultdict
screen = None
BLACK= (0,0,0)
running = True


class char():
        x=50
        y=50
class model():
        def __init__(self, screen,camera):
                self.char=char()
                self.world=world(screen, camera)
def drawAt(imgName, x,y):
        img = pygame.image.load(imgName)
        screen.blit(img, (x,y))
        pygame.display.flip()
class feyAdventure():
        model=None
        def __init__(self,screen, camera):
                self.model=model(screen, camera)
                self.model.world.load_submap('fey/bridge.map')
        
keyStatus=defaultdict(lambda :False)
keyStatusLast=defaultdict(lambda :False)
mousex, mousey,button=0,0,0
isFull=False
def toggleFull():
        global isFull
        if isFull:
                camera.resx, camera.resy =(1024,768)
                pygame.display.set_mode((camera.resx,camera.resy))
                isFull=False
        else:
                camera.resx, camera.resy =(1920,1080)
                pygame.display.set_mode((camera.resx,camera.resy),  FULLSCREEN)
                
                isFull=True
def handle_user_input(model,camera):
        global keyStatus,keyStatusLast
        def shiftMod():
            return 5 if keyStatus[K_LSHIFT] else 1
        
        mousex,mousey=pygame.mouse.get_pos()
        for event in pygame.event.get():
                #record key status
                if hasattr(event, 'key'):
                    down = event.type == KEYDOWN
                    keyStatus[event.key]=down
                    if event.type==KEYDOWN and event.key == pygame.K_ESCAPE:
                            print 'Quitting'
                            running = False  # Be interpreter friendly           
                            pygame.quit()
                #record mouse input
                if event.type == pygame.MOUSEBUTTONUP:
                    keyStatus[MOUSEBUTTONDOWN]=False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    keyStatus[MOUSEBUTTONDOWN]=True
                    global button
                    button=event.button
                        
        if keyStatus[K_RIGHT]:
                camera.x+=1*shiftMod()
        if keyStatus[K_LEFT]: 
                camera.x-=1*shiftMod()
        if keyStatus[K_UP]:
                camera.y-=1*shiftMod()
        if keyStatus[K_DOWN]: 
                camera.y+=1*shiftMod()
        if keyStatus[K_RETURN]:
                if not keyStatusLast[K_RETURN]:
                        toggleFull()

        pos = pygame.mouse.get_pos()
        if keyStatus[MOUSEBUTTONDOWN]:
            trans=camera.xyToModel(mousex,mousey)
            clickeditem = model.world.click(trans[0],trans[1],button)

            
        keyStatusLast=copy.deepcopy(keyStatus)
def drawWorld(model, camera):
        gridSize=camera.gridSize
        
        screen.fill(BLACK)
        pygame.draw.rect(screen,(10,10,10),(camera.subx,camera.suby,camera.subwid,camera.subhig),0) #projector sub-screen outline
        #for x, y, image in model.world.tiles:
        #        screen.blit(image, (camera.x+x*gridSize +camera.subx,camera.y+y*gridSize+camera.suby))
                
        #for x, y, wid, hig, image in model.world.imgs:
        #        picture = pygame.transform.scale(image, (wid*gridSize, hig*gridSize))
        #        rect = picture.get_rect()
        #        rect = rect.move((camera.x+x*gridSize +camera.subx ,camera.y+y*gridSize +camera.suby))
        #        screen.blit(picture, rect)
        for background in model.world.backgrounds:
            background.draw(screen, camera)

        #gridlines
        for x in range(0 + (camera.subx%camera.gridSize()), camera.resx, camera.gridSize()):
                pygame.draw.line(screen, (0,0,0), (x,0),(x,camera.resy))
        for y in range(0 + (camera.suby%camera.gridSize()), camera.resy, camera.gridSize()):
                pygame.draw.line(screen, (0,0,0), (0,y),(camera.resx,y))


        #black-out borders
        pygame.draw.rect(screen,(0,0,0),(0,0,camera.resx,camera.suby),0)
        pygame.draw.rect(screen,(0,0,0),(camera.subx+camera.subwid,0,camera.resx,camera.resy),0)
        pygame.draw.rect(screen,(0,0,0),(0,camera.suby+camera.subhig,camera.resx,camera.resy),0)
        pygame.draw.rect(screen,(0,0,0),(0,0,camera.subx,camera.resy),0)
                

        


if __name__ == '__main__':
        camera=camera()
        screen = pygame.display.set_mode((camera.resx,camera.resy),  DOUBLEBUF)
        adv=feyAdventure(screen, camera)
        model=adv.model
        clock = pygame.time.Clock()
        FRAMES_PER_SECOND = 40
        pygame.init() 
        while running:
                handle_user_input(model,camera)
                model.world.update()
                drawWorld(model, camera)
                #drawAt('chars/c1.png', model.char.x,model.char.y)
                pygame.display.update()
                deltat = clock.tick(FRAMES_PER_SECOND)     
                
        
