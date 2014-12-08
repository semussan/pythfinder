
import pygame
import copy
import datetime
import dill
from sprite import Sprite
from World import World
from camera import camera
from pygame.locals import *
from collections import defaultdict
import pyconsole
from BattleManager import BattleManager
import os,sys

import glob


screen = None
BLACK= (0,0,0)
running = True
keyStatus=defaultdict(lambda :False)
keyStatusLast=defaultdict(lambda :False)
joyStatus=defaultdict(lambda :False)
joyStatusLast=defaultdict(lambda :False)
joyHatStatus=defaultdict(lambda :(0,0))
joyHatStatusLast=defaultdict(lambda :(0,0))
joyHatStatusLastLast=defaultdict(lambda :(0,0))
mousex, mousey,button=0,0,0


def getLatestSaveFile():
        return max(glob.iglob(os.path.join('saves', '*.save')), key=os.path.getctime)


def writeState(filename,model,camera):
        for sprite in model.world.sprites:
                sprite.imgs=None
                sprite.portrait=None
                sprite.deadImg=None
        for background in model.world.backgrounds:
                background.img=None
                background.FoW.fogImg=None
        model.world.bloodImgs=None
        camera.vert={}
        camera.horz={}
        camera.soundManager.clearRunning()
##        print 'saving in ',camera.soundManager.bgtracksSaves
        camera.battleManager=None
        screensave=camera.screen
        camera.screen=None
        with open(filename+'.save','wb') as saveFile:
                saveFile.write(dill.dumps([model,camera]))
        camera.screen=screensave
        model.writeState=writeState
##        print 'left',camera.soundManager.bgtracksSaves
        
def loadState(filename):
        global transferModel, transferCamera,camera
        camera.soundManager.clearRunningAndStored()
        screensave=camera.screen
        with open(filename,'rb') as saveFile:
                transferModel, transferCamera=dill.load(saveFile)
        transferCamera.screen=screensave
        model.loadState=loadState
##        print 'After save load',camera.soundManager.bgtracksSaves
        #transferCamera.screen = pygame.display.set_mode((camera.resx,camera.resy),  DOUBLEBUF)
class Model():
        def __init__(self, camera):
                self.world=World(self, camera)
class Adventure():
        model=None
        def __init__(self, camera,mapFile,):
                self.model=Model(camera)
                self.model.world.load(mapFile)
        
def isCtrl():
        return bool(pygame.key.get_mods()& KMOD_LCTRL)

def newPress(key):
        global keyStatus,keyStatusLast
        return not keyStatusLast[key] and keyStatus[key]
def newJoyPress(joy_ID, button):
        global joyStatus,joyStatusLast
        return not joyStatusLast[joy_ID, button] and joyStatus[joy_ID, button]
def newJoyHatPress(joy_ID):
        global joyHatStatus,joyHatStatusLast,joyHatStatusLastLast
        return joyHatStatusLastLast[joy_ID] == (0,0) and joyHatStatusLast[joy_ID] == (0,0)  and joyHatStatus[joy_ID] != (0,0)
        
        
def handle_user_input(model,camera,console):
        global keyStatus,keyStatusLast,joyStatus,joyStatusLast,joyStatusLastLast,joyHatStatusLastLast
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
                    sys.exit()
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
        #Handle player controller input
        for joystick, player in model.world.joystickBindings.iteritems():
                numButtons = joystick.get_numbuttons()
                for i in range(numButtons):
                        joyStatus[joystick.get_id(),i]=joystick.get_button( i )
                joyHatStatus[joystick.get_id()]=joystick.get_hat(0)

                #Dpad movement
                if newJoyHatPress(joystick.get_id()):
                        moveX,moveY=joystick.get_hat(0)
                        player.move(moveX,-moveY)
                        if player.maxHealth/2>player.hp:
                                model.world.addBlood(player.rect[0],player.rect[1])

                #Interact
                if newJoyPress(joystick.get_id(),0):
                        print "Interact!", joystick.get_id()
                        model.world.interact(player)

                #Talk
                if newJoyPress(joystick.get_id(),1):
                        print "Talk!", joystick.get_id()
                        camera.addDialog(player,'Left')

                #HealthDown
                if newJoyPress(joystick.get_id(),2):
                        print "HealthDown!", joystick.get_id()
                        player.damage(+1)
                        
                #HealthUp
                if newJoyPress(joystick.get_id(),3):
                        print "HealthUp!", joystick.get_id()
                        player.damage(-1)
                        

                        
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
                
        if newPress(K_BACKSPACE):
                model.world.repair()                     

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

        #Quicksave
        if newPress(K_F5):
                writeState('saves/'+datetime.datetime.now().strftime("%I.%M%p on %B %d, %Y"),model,camera)
                #camera.quickSaveFile())
        #Quickload
        if newPress(K_F9):
                loadState(getLatestSaveFile())
                #camera.quickSaveFile())

        #ManualSave
        if newPress(K_F11):
                writeState(camera.quickSaveFile(),model,camera)
        #Manual Load
        if newPress(K_F12):
                loadState(camera.quickFile())



        if newPress(K_e) and camera.target:
                if camera.target.interaction:
                        camera.target.interaction()
                elif camera.target.portrait:
                        camera.target.show()
        if newPress(K_i) and camera.target:
                if camera.target.portrait:
                        camera.target.show()
                

        if newPress(K_MINUS) and camera.target:
                camera.target.damage(1)
        if newPress(K_EQUALS) and camera.target:
                camera.target.damage(-1)
                
        if newPress(K_DELETE) and camera.target:
                if not camera.target.dead:
                        camera.target.dead=True
                        camera.target.movable=False
                        if camera.battleManager:
                                camera.battleManager.removePlayer(camera.target)
                                camera.target=camera.battleManager.getCurPlayer()
                        else:
                                camera.target=None
                else:
                        camera.target.rect=(-99,-99,0,0)
                        camera.target=None
                
        pos = pygame.mouse.get_pos()
        if keyStatus[MOUSEBUTTONDOWN]:
            trans=camera.xyToModel(mousex,mousey)
            target = model.world.click(trans[0],trans[1],button,camera, not keyStatusLast[MOUSEBUTTONUP])
            if newPress(MOUSEBUTTONDOWN):
                    camera.target=target
                    
        if newPress(K_LALT):
                if not camera.battleManager:
                        camera.battleManager=BattleManager(camera)
                if camera.target and not camera.battleManager.has(camera.target):
                        if camera.target.isPlayer and not camera.battleManager.started:
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
        joyStatusLast=copy.deepcopy(joyStatus)
        joyHatStatusLast=copy.deepcopy(joyHatStatus)
        joyStatusLastLast=copy.deepcopy(joyStatusLast)
        joyHatStatusLastLast=copy.deepcopy(joyHatStatusLast)
        
def getAllFiles(self, fileName):
        folder, filePart=os.path.split(fileName)
        namePart=filePart.split('.')[0]
        files = [folder+'/'+f for f in os.listdir(folder) if os.path.isfile(folder+'/'+f) and namePart in f]

transferModel=None
transferCamera=None
if __name__ == '__main__':
        global transferModel, transferCamera
        screen = pygame.display.set_mode((camera.resx,camera.resy),  DOUBLEBUF)
        camera=camera(screen)        
        console=pyconsole.Console(screen,(0,0,camera.resx,camera.resy/6))
        console.active=False
        adv=Adventure( camera,'maps/fey/hub.map')
        model=adv.model
        model.writeState=writeState
        model.loadState=loadState
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
                model.world.sprites.append(Sprite(model,camera,imgFile,(x,y,width,height ), True ,))
        while running:
                try:
                        if transferModel and transferCamera:
                                model=transferModel
                                camera=transferCamera
                                transferModel,transferCamera=None,None
                        camera.drawWorld(model,console)
                        handle_user_input(model,camera,console)
                        model.world.update()
                        camera.update()
                        pygame.display.update()
                        deltat = clock.tick(FRAMES_PER_SECOND)
                        model.world.repair()
                        #loadState(camera.quickFile())
                        #writeState(camera.quickSaveFile())
                except Exception, e:
                        #running = False
                        print e
                        
                
        
