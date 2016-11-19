import pygame
from Entity import Entity
from World import World
from camera import camera
import pyconsole
import os, sys
from Input import handle_user_input
from Cached import Cached
from SaveStates import loadState
screen = None
BLACK = (0, 0, 0)
running = True




##        print 'After save load',camera.soundManager.bgtracksSaves
# transferCamera.screen = pygame.display.set_mode((camera.resx,camera.resy),  DOUBLEBUF)
class Model():
    def __init__(self, camera, campaignName,cached):
        self.world = World(self, camera,cached, campaignName)
        self.world.initPlayers(camera,cached)


class Adventure():
    model = None

    def __init__(self, camera, campaignName,cached ):
        self.model = Model(camera, campaignName,cached)



def getAllFiles(self, fileName):
    folder, filePart = os.path.split(fileName)
    namePart = filePart.split('.')[0]
    files = [folder + '/' + f for f in os.listdir(folder) if os.path.isfile(folder + '/' + f) and namePart in f]


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = "128,128"
    #camera = camera()
    model, camera = loadState()
    cached= Cached()
    console = pyconsole.Console(cached.screen(camera), (0, 0, camera.resx, camera.resy / 6))
    console.active = False
    #adv = Adventure(camera, 'maps/fey',cached)
    #model = adv.model
    clock = pygame.time.Clock()
    FRAMES_PER_SECOND = 24
    pygame.init()


    #def loadMap():
    #    model.world.load(camera.quickFile())


    def loadSprite(width=1, height=1):
        imgFile = camera.quickFile()
        x, y = 0, 0
        if camera.target:
            x, y = camera.target.rect[0], camera.target.rect[1]
        model.world.sprites.append(Entity(model, camera, imgFile, (x, y, width, height), True, ))

    while running:
        #try:
            #if transferModel and transferCamera:
            #    model = transferModel
            #    camera = transferCamera
            #    transferModel, transferCamera = None, None
        model, camera = handle_user_input(model, camera, cached, console)
        model.world.update(camera,cached,model)
        camera.drawWorld(model, console,cached)
        camera.update(model)
        pygame.display.update()
        deltat = clock.tick(FRAMES_PER_SECOND)

        #model.world.reconnectJoysticks()
        # loadState(camera.quickFile())
        # writeState(camera.quickSaveFile())
        #except Exception, e:
        #    print e
        #    running = False
