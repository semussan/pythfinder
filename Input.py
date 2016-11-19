__author__ = 'tyoung'
from RightClickMenu import rightClickMenu
import pygame
import copy
from pygame.locals import *
import sys
from BattleManager import BattleManager
from collections import defaultdict
from SaveStates import loadState, writeState
import datetime

keyStatus = defaultdict(lambda: False)
keyStatusLast = defaultdict(lambda: False)
mouseStatus = defaultdict(lambda: False)
mouseStatusLast = defaultdict(lambda: False)
joyStatus = defaultdict(lambda: False)
joyStatusLast = defaultdict(lambda: False)
joyHatStatus = defaultdict(lambda: (0, 0))
joyHatStatusLast = defaultdict(lambda: (0, 0))
joyHatStatusLastLast = defaultdict(lambda: (0, 0))
mousex, mousey, button = 0, 0, 0

def handle_user_input(model, camera, cached, console):
    global keyStatus, keyStatusLast, mouseStatus,mouseStatusLast, joyStatus, joyStatusLast, joyStatusLastLast, joyHatStatusLastLast


    now = pygame.time.get_ticks()

    def shiftMod():
        return 5 if keyStatus[K_LSHIFT] else 1

    #------------console and helper functions--------------
    def stopsound(): model.world.currentArea.soundManager.clearRunningAndStored(cached)
    def stopSound(): model.world.currentArea.soundManager.clearRunningAndStored(cached)
    if console.active:
        console.process_input(locals())

    mousex, mousey = pygame.mouse.get_pos()
    for event in pygame.event.get():
        # Handle exiting prog
        if event.type == QUIT:
            print 'Quitting'
            running = False  # Be interpreter friendly
            pygame.quit()
            sys.exit()
        # record key status
        if hasattr(event, 'key'):
            down = event.type == KEYDOWN
            keyStatus[event.key] = down

        # record mouse input
        if event.type is pygame.MOUSEBUTTONUP or event.type is pygame.MOUSEBUTTONDOWN:
            global button
            mouseStatus[event.button] = True if event.type is pygame.MOUSEBUTTONDOWN else False

    # Handle player controller input
    if newKeyPress(K_PAUSE):
        camera.pausingPlayers=not camera.pausingPlayers

    if camera.lookingForJoystickTarget:
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            if not joystick.get_init():
                joystick.init()
            numButtons = joystick.get_numbuttons()
            found=False
            for i in range(numButtons):
                if  joystick.get_button(i):
                    found=True
            if joystick.get_hat(0)[0] or 54.get_hat(0)[1]:
                    found=True
            if found:
                cached._playerToJoystick[camera.lookingForJoystickTarget.imgName]=joystick
                camera.lookingForJoystickTarget= None


    ## Handle Inputs
    pos = pygame.mouse.get_pos()
    gridCoords = camera.xyToModel(mousex, mousey)

    for playerName, joystick in cached._playerToJoystick.iteritems():
        if [x for x in model.world.players if x.imgName == playerName]:
            player = [x for x in model.world.players if x.imgName == playerName][0]
            if not joystick.get_init():
                joystick.init()
            numButtons = joystick.get_numbuttons()
            for i in range(numButtons):
                joyStatus[joystick.get_id(), i] = joystick.get_button(i)
            joyHatStatus[joystick.get_id()] = joystick.get_hat(0)

            if not camera.pausingPlayers:
                # Dpad movement
                if playerName not in cached._playerLastPress:
                    cached._playerLastPress[playerName]=now
                if now - cached._playerLastPress[playerName] >= 150 and (joyHatStatus[joystick.get_id()][0] or joyHatStatus[joystick.get_id()][1]) :
                    moveX, moveY = joystick.get_hat(0)
                    player.move(moveX, -moveY, camera,model,cached)
                    cached._playerLastPress[playerName]= now
                    if player.maxHealth / 2 > player.hp:
                        model.world.currentArea.addBlood(player.rect[0], player.rect[1],cached)

                # Interact
                if newJoyPress(joystick.get_id(), 0):
                    print "Interact!", joystick.get_id()
                    model.world.interact(player,model,camera,cached)

                # Talk
                if joyStatus[joystick.get_id(), 1]:
                    print "Talk!", joystick.get_id()
                    camera.addDialog(player, 'Left',1)

                # HealthDown
                if newJoyPress(joystick.get_id(), 2):
                    print "HealthDown!", joystick.get_id()
                    player.damage(+1)

                # HealthUp
                if newJoyPress(joystick.get_id(), 3):
                    print "HealthUp!", joystick.get_id()
                    player.damage(-1)

    # camera and target movement
    if camera.target:
        if newKeyPress(K_d) or newKeyPress(K_RIGHT):
            camera.target.move(1, 0,camera,model,cached)
        if newKeyPress(K_a) or newKeyPress(K_LEFT):
            camera.target.move(-1, 0,camera,model,cached)
        if newKeyPress(K_w) or newKeyPress(K_UP):
            camera.target.move(0, -1,camera,model,cached)
        if newKeyPress(K_s) or newKeyPress(K_DOWN):
            camera.target.move(0, 1,camera,model,cached)
    else:
        if keyStatus[K_d] or keyStatus[K_RIGHT]:
            camera.x += 1 * shiftMod()
        if keyStatus[K_a] or keyStatus[K_LEFT]:
            camera.x -= 1 * shiftMod()
        if keyStatus[K_w] or keyStatus[K_UP]:
            camera.y -= 1 * shiftMod()
        if keyStatus[K_s] or keyStatus[K_DOWN]:
            camera.y += 1 * shiftMod()

    ###########resizing##############
    if camera.target:
        if newKeyPress(K_KP8):
            camera.target.resize(0, -1,camera,model,cached)
        if newKeyPress(K_KP2):
            camera.target.resize(0, 1,camera,model,cached)
        if newKeyPress(K_KP4):
            camera.target.resize(-1, 0,camera,model,cached)
        if newKeyPress(K_KP6):
            camera.target.resize(1, 0,camera,model,cached)
    #########rotating
    if camera.target:
        if newKeyPress(K_KP9):
            camera.target.rotateBy(1)
        if newKeyPress(K_KP7):
            camera.target.rotateBy(-1)
    if newKeyPress(K_RETURN):
        camera.toggleFull()

    if newKeyPress(K_PERIOD):
        camera.doStreaming = not camera.doStreaming

    if newKeyPress(K_BACKSPACE):
        model.world.reconnectJoysticks()

    if newKeyPress(K_PAGEUP):
        camera.drawGrid = False
    if newKeyPress(K_PAGEDOWN):
        camera.drawGrid = True

    if newKeyPress(K_HOME):
        camera.drawShadows = False
    if newKeyPress(K_END):
        camera.drawShadows = True

    if newKeyPress(K_BACKQUOTE):
        console.active = True
    if newKeyPress(K_KP_PLUS):
        camera.cameraChase = not camera.cameraChase

    ########Saving##########
    #  Quicksave
    if newKeyPress(K_F5):
        writeState('saves/' + datetime.datetime.now().strftime("%I.%M%p on %B %d, %Y"), model, camera,cached)
        # camera.quickSaveFile())
    # Quickload
    if newKeyPress(K_F9):
        model, camera = loadState()
        # camera.quickSaveFile())

    # ManualSave
    if newKeyPress(K_F11):
        writeState(camera.quickSaveFile(), model, camera)
    # Manual Load
    if newKeyPress(K_F12):
        loadState(camera.quickFile())

    if newKeyPress(K_e) and camera.target:
        if camera.target.interactionString:
            camera.target.interaction(model,camera, cached)
        elif camera.target.imgName:
            camera.show(camera.target)
    if newKeyPress(K_i) and camera.target:
        if camera.target.portrait:
            camera.target.show()

    if newKeyPress(K_MINUS) and camera.target:
        camera.target.damage(1)
    if newKeyPress(K_EQUALS) and camera.target:
        camera.target.damage(-1)

    if newKeyPress(K_SLASH):
        if camera.target:
            camera.currentDescriptionTarget=camera.target
        else:
            camera.currentDescriptionTarget=None
    if newKeyPress(K_ESCAPE):
        camera.target = None
        camera.dialogs={}
        camera.currentDescriptionTarget = None

    if newKeyPress(K_DELETE) and camera.target:
        camera.target.onDeletePress(camera,cached,model)

    if newKeyPress(K_F10):
        camera.battleManager=None


    ######## Mouse presses##########
    if newMouseRelease(3):# right click
        camera.target = model.world.getTarget(gridCoords[0], gridCoords[1],camera,keyStatus[K_LCTRL])
        rightClickMenu(gridCoords[0],gridCoords[1],camera.target,model,camera,cached)
    if newMouseRelease(1):
        target = model.world.click(gridCoords[0], gridCoords[1], 1 , camera,True,keyStatus[K_LCTRL],keyStatus[K_LSHIFT])
        camera.target = target
    elif mouseStatus[1] or mouseStatus[2]:
        model.world.click(gridCoords[0], gridCoords[1], 1 if mouseStatus[1] else 2, camera,False,keyStatus[K_LCTRL],keyStatus[K_LSHIFT])

    ########Battle buttons##############
    if newKeyPress(K_LALT):
        if not camera.battleManager:
            camera.battleManager = BattleManager(camera)
        if camera.target and not camera.battleManager.has(camera.target):
            if camera.target.isPlayer and not camera.battleManager.started:
                init = int(camera.quickInit("Enter initiative"))
                camera.battleManager.addPlayer(camera.target, init)
            else:
                camera.battleManager.addPlayer(camera.target)

    if newKeyPress(K_RALT)  and camera.battleManager:
        if len(camera.battleManager.list) <= 1:
            camera.battleManager = None
        elif camera.target and camera.battleManager.has(camera.target):
                camera.battleManager.removePlayer(camera.target)
                camera.target = camera.battleManager.getCurPlayer()
        else:
            camera.battleManager.removePlayer(camera.battleManager.getCurPlayer())
            camera.target = camera.battleManager.getCurPlayer()
    if newKeyPress(K_SPACE):
        if camera.battleManager:
            if not camera.battleManager.started:
                camera.battleManager.startBattle()
                camera.target = camera.battleManager.getCurPlayer()
            else:
                if camera.target is camera.battleManager.getCurPlayer():
                    camera.target = camera.battleManager.cycleNextPlayer()
                    camera.target = camera.battleManager.getCurPlayer()
                else:
                    camera.target = camera.battleManager.getCurPlayer()
    ####DM Copy-Past##
    if keyStatus[K_LCTRL] and newKeyPress(K_c) and camera.target:
        camera.copyTarget=camera.target
    if keyStatus[K_LCTRL] and newKeyPress(K_v) and camera.copyTarget:
        camera.copyTarget.duplicateTo(gridCoords[0],gridCoords[1],camera,model)

    keyStatusLast = copy.deepcopy(keyStatus)
    mouseStatusLast = copy.deepcopy(mouseStatus)
    joyStatusLast = copy.deepcopy(joyStatus)
    joyHatStatusLast = copy.deepcopy(joyHatStatus)
    joyStatusLastLast = copy.deepcopy(joyStatusLast)
    joyHatStatusLastLast = copy.deepcopy(joyHatStatusLast)
    return model, camera
def isCtrl():
    return bool(pygame.key.get_mods() & KMOD_LCTRL)


def newKeyPress(key):
    global keyStatus, keyStatusLast
    return not keyStatusLast[key] and keyStatus[key]

def newKeyRelease(key):
    global keyStatus, keyStatusLast
    return keyStatusLast[key] and not keyStatus[key]

def newMousePress(key):
    global mouseStatus, mouseStatusLast
    return not mouseStatusLast[key] and mouseStatus[key]

def newMouseRelease(key):
    global mouseStatus, mouseStatusLast
    return mouseStatusLast[key] and not mouseStatus[key]

def newJoyPress(joy_ID, button):
    global joyStatus, joyStatusLast
    return not joyStatusLast[joy_ID, button] and joyStatus[joy_ID, button]


def newJoyHatPress(joy_ID):
    global joyHatStatus, joyHatStatusLast, joyHatStatusLastLast
    return joyHatStatusLastLast[joy_ID] == (0, 0) and joyHatStatusLast[joy_ID] == (0, 0) and joyHatStatus[joy_ID] != (
    0, 0)
