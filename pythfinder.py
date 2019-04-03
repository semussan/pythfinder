import pygame
from Entity import Entity
from World import World
import camera
import pyconsole
import threading
import runthis_webhost
import os, sys
from Input import handle_user_input
import objgraph
from Cached import Cached
import time
from SaveStates import loadState
screen = None
BLACK = (0, 0, 0)
running = True
from flask import Flask, render_template, Response

# emulated camera
from webcamera import WebCamera


app = Flask(__name__)
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(WebCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def webVideoFunc():
    app.run(host='0.0.0.0', debug=True, use_reloader=False)		
def setupWebVideo():
    t = threading.Thread(target=webVideoFunc,name="WebVideo",args=())
    t.daemon = True
    t.start()

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
    setupWebVideo()
    model, camera = loadState()
    #camera = camera.Camera()
    cached = Cached()
    console = pyconsole.Console(cached.screen(camera), (0, 0, camera.resx, camera.resy / 6))
    console.active = False
    #adv = Adventure(camera, 'maps/fey',cached)
    #model = adv.model
    clock = pygame.time.Clock()
    DESIRED_FPS = 24
    LIMIT_FPS = True
    UPDATE_STEP = (1.0/float(DESIRED_FPS))
    SLEEP_SEC = .001
    pygame.init()
    pygame.display.set_mode((camera.resx, camera.resy), pygame.RESIZABLE)
    #def loadMap():
    #    model.world.load(camera.quickFile())


    def loadSprite(width=1, height=1):
        imgFile = camera.quickFile()
        x, y = 0, 0
        if camera.target:
            x, y = camera.target.rect[0], camera.target.rect[1]
        model.world.sprites.append(Entity(model, camera, imgFile, (x, y, width, height), True, ))

    next_update = time.time() + UPDATE_STEP
    OBSERVED_FPS = 0
    while running:
        #try:
            #if transferModel and transferCamera:
            #    model = transferModel
            #    camera = transferCamera
            #    transferModel, transferCamera = None, None
        cycle_start_time = time.time()

        controler_start = time.time()
        model, camera = handle_user_input(model, camera, cached, console)
        controler_end = time.time()

        model_start = time.time()
        model.world.update(camera,cached,model)
        model_end = time.time()

        view_start = time.time()
        camera.drawWorld(model, console,cached)
        camera.update(model)
        view_end = time.time()

        camera.showFPS(OBSERVED_FPS, model_end-model_start, view_end - view_start, controler_end - controler_start, cached)
        pygame.display.update()

        #deltat = clock.tick(FRAMES_PER_SECOND)
        #last_update_time = time.time()
        #while time.time() < next_update:
            #model, camera = handle_user_input(model, camera, cached, console)
        #    time.sleep(SLEEP_SEC)
        now = time.time()
        if LIMIT_FPS and now < next_update:
            pygame.time.delay( int((next_update - now)*1000))
        cycle_end_time = time.time()
        OBSERVED_FPS = 1.0/(cycle_end_time - cycle_start_time)
            
        #print next_update, cycle_end_time, cycle_start_time, UPDATE_STEP

        next_update = next_update + UPDATE_STEP

        #print next_update

        #model.world.reconnectJoysticks()
        # loadState(camera.quickFile())
        # writeState(camera.quickSaveFile())
        #except Exception, e:
        #    print e
        #    running = False
