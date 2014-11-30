
import pygame
import copy
from world import world
from camera import camera
from pygame.locals import *
from collections import defaultdict
import pyconsole
screen = None
BLACK= (0,0,0)
running = True
keyStatus=defaultdict(lambda :False)
keyStatusLast=defaultdict(lambda :False)
mousex, mousey,button=0,0,0


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
                self.model.world.load('fey/bridge.map')
        
def isCtrl():
        return bool(pygame.key.get_mods()& KMOD_LCTRL)

def handle_user_input(model,camera,console):
        global keyStatus,keyStatusLast
        def shiftMod():
            return 5 if keyStatus[K_LSHIFT] else 1

        
        if console.active:
                console.process_input(globals())
        
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
                        
        if keyStatus[K_RIGHT] or keyStatus[K_d]:
                camera.x+=1*shiftMod()
        if keyStatus[K_LEFT] or keyStatus[K_a]: 
                camera.x-=1*shiftMod()
        if keyStatus[K_UP] or keyStatus[K_w]:
                camera.y-=1*shiftMod()
        if keyStatus[K_DOWN] or keyStatus[K_s]: 
                camera.y+=1*shiftMod()
                
        if keyStatus[K_RETURN]:
                if not keyStatusLast[K_RETURN]:
                        camera.toggleFull()
                        

        if keyStatus[K_PAGEUP]:
                camera.drawGrid=False
        if keyStatus[K_PAGEDOWN]:
                camera.drawGrid=True   
                
        if keyStatus[K_HOME]:
                camera.drawShadows=False
        if keyStatus[K_END]:
                camera.drawShadows=True

        if keyStatus[K_BACKQUOTE]:
                console.active=True
                
        pos = pygame.mouse.get_pos()
        if keyStatus[MOUSEBUTTONDOWN]:
            trans=camera.xyToModel(mousex,mousey)
            clickeditem = model.world.click(trans[0],trans[1],button,camera)

        keyStatusLast=copy.deepcopy(keyStatus)
        
                

        


if __name__ == '__main__':
        
        
        screen = pygame.display.set_mode((camera.resx,camera.resy),  DOUBLEBUF)
        camera=camera(screen)
        console=pyconsole.Console(screen,(0,0,camera.resx,camera.resy/6))
        console.active=False

        adv=feyAdventure(screen, camera)
        model=adv.model
        clock = pygame.time.Clock()
        FRAMES_PER_SECOND = 40
        pygame.init() 
        while running:
                camera.drawWorld(model,console)
                handle_user_input(model,camera,console)
                model.world.update()
                #drawAt('chars/c1.png', model.char.x,model.char.y)
                pygame.display.update()
                deltat = clock.tick(FRAMES_PER_SECOND)     
                
        
