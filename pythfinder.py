
import pygame
import copy
from world import world
from camera import camera
from pygame.locals import *
from collections import defaultdict
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
                self.model.world.load_submap('fey/bridge.map')
        


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
                        camera.toggleFull()
        if keyStatus[K_PAGEDOWN]:
                camera.drawGrid=False
        if keyStatus[K_PAGEUP]:
                camera.drawGrid=True
        if keyStatus[K_HOME]:
                camera.drawShadows=False
        if keyStatus[K_END]:
                camera.drawShadows=True
                
        pos = pygame.mouse.get_pos()
        if keyStatus[MOUSEBUTTONDOWN]:
            trans=camera.xyToModel(mousex,mousey)
            clickeditem = model.world.click(trans[0],trans[1],button,camera)

        keyStatusLast=copy.deepcopy(keyStatus)
        
                

        


if __name__ == '__main__':
        screen = pygame.display.set_mode((camera.resx,camera.resy),  DOUBLEBUF)
        camera=camera(screen)
        adv=feyAdventure(screen, camera)
        model=adv.model
        clock = pygame.time.Clock()
        FRAMES_PER_SECOND = 40
        pygame.init() 
        while running:
                camera.drawWorld(model)
                handle_user_input(model,camera)
                model.world.update()
                #drawAt('chars/c1.png', model.char.x,model.char.y)
                pygame.display.update()
                deltat = clock.tick(FRAMES_PER_SECOND)     
                
        
