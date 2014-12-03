
import pygame
import copy
from sprite import Sprite
from world import world
from camera import camera
from pygame.locals import *
from collections import defaultdict
import pyconsole
from BattleManager import BattleManager
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
                self.model.world.load('maps/fey/bridge.map')
        
def isCtrl():
        return bool(pygame.key.get_mods()& KMOD_LCTRL)

def newPress(key):
        global keyStatus,keyStatusLast
        return not keyStatusLast[key] and keyStatus[key]
        
def handle_user_input(model,camera,console):
        global keyStatus,keyStatusLast
        def shiftMod():
            return 5 if keyStatus[K_LSHIFT] else 1

        
        if console.active:
                console.process_input(globals())
        
        mousex,mousey=pygame.mouse.get_pos()
        for event in pygame.event.get():
                #Handle exiting prog
                if (event.type==KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == QUIT:
                    print 'Quitting'
                    running = False  # Be interpreter friendly           
                    pygame.quit()
                #record key status
                if hasattr(event, 'key'):

                    down = event.type == KEYDOWN
                    keyStatus[event.key]=down

                #record mouse input
                if event.type == pygame.MOUSEBUTTONUP:
                    keyStatus[MOUSEBUTTONDOWN]=False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    keyStatus[MOUSEBUTTONDOWN]=True
                    global button
                    button=event.button
                        
        #camera and target movement
        if camera.target:
                if newPress(K_d) or newPress(K_RIGHT):
                        camera.target.move(1,0)
                if newPress(K_a) or newPress(K_LEFT):
                        camera.target.move(-1,0)
                if newPress(K_w) or newPress(K_UP):
                        camera.target.move(0,-1)
                if newPress(K_s) or newPress(K_DOWN):
                        camera.target.move(0,1)
        else:
                if keyStatus[K_d] or keyStatus[K_RIGHT]:
                        camera.x+=1*shiftMod()
                if keyStatus[K_a] or keyStatus[K_LEFT]: 
                        camera.x-=1*shiftMod()
                if keyStatus[K_w] or keyStatus[K_UP]:
                        camera.y-=1*shiftMod()
                if keyStatus[K_s] or keyStatus[K_DOWN]: 
                        camera.y+=1*shiftMod()                
                
        if newPress(K_RETURN):
                camera.toggleFull()
                        

        if newPress(K_PAGEUP):
                camera.drawGrid=False
        if newPress(K_PAGEDOWN):
                camera.drawGrid=True   
                
        if newPress(K_HOME):
                camera.drawShadows=False
        if newPress(K_END):
                camera.drawShadows=True

        if newPress(K_BACKQUOTE):
                console.active=True
                
        pos = pygame.mouse.get_pos()
        if keyStatus[MOUSEBUTTONDOWN]:
            trans=camera.xyToModel(mousex,mousey)
            target = model.world.click(trans[0],trans[1],button,camera)
            if newPress(MOUSEBUTTONDOWN):
                    camera.target=target
                    
        if newPress(K_LALT):
                if not camera.battleManager:
                        camera.battleManager=BattleManager(camera)
                if camera.target and not camera.battleManager.has(camera.target):
                        if not isinstance(camera.target,Sprite) and not camera.battleManager.started:
                                init=int(camera.quickInt("Enter initiative"))
                                camera.battleManager.addPlayer(camera.target,init)
                        else:
                                camera.battleManager.addPlayer(camera.target)   
                        
                        
        if newPress(K_RALT) and camera.target and camera.battleManager and camera.battleManager.has(camera.target):
                if len(camera.battleManager.list)<=1:
                        camera.battleManager=None
                else:
                        camera.battleManager.removePlayer(camera.target)
                        camera.target=camera.battleManager.getCurPlayer()
        if newPress(K_SPACE):
                if camera.battleManager:
                        if not camera.battleManager.started:
                                camera.battleManager.startBattle()
                                camera.target=camera.battleManager.getCurPlayer()
                        else:
                                if camera.target is camera.battleManager.getCurPlayer():
                                        camera.target=camera.battleManager.cycleNextPlayer()
                                        camera.target=camera.battleManager.getCurPlayer()
                                else:
                                        camera.target=camera.battleManager.getCurPlayer()

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
        def loadMap():
                model.world.load(camera.quickFile())
        def loadSprite(width=1,height=1):
                imgFile=camera.quickFile()
                x,y=0,0
                if camera.target:
                        x,y=camera.target.rect[0],camera.target.rect[1]
                model.world.sprites.append(Sprite(imgFile,(x,y,width,height ), True ,))
        while running:
                #try:
                        camera.drawWorld(model,console)
                        handle_user_input(model,camera,console)
                        model.world.update()
                        pygame.display.update()
                        deltat = clock.tick(FRAMES_PER_SECOND)
                #except Exception, e:
                #        running = False
                #        print e
                        
                
        
