__author__ = 'tyoung'

import glob
import os
import dill


def getLatestSaveFile():
    return max(glob.iglob(os.path.join('saves', '*.save')), key=os.path.getctime)


def writeState(filename, model,camera,cached):
    #camera.soundManager.clearRunning()
    ##        print 'saving in ',camera.soundManager.bgtracksSaves
    #screensave = camera.screen
    #camera.screen = None
    with open(filename + '.save', 'wb') as saveFile:
        saveFile.write(dill.dumps([model, camera]))
    #camera.screen = screensave
    #model.writeState = writeState


##        print 'left',camera.soundManager.bgtracksSaves

def loadState(filename=None):
    if not filename:
        filename=getLatestSaveFile()
    #global transferModel, transferCamera, camera
    #model.world.currentArea.soundManager.clearRunningAndStored(cached)
    #screensave = camera.screen
    modelIn = None
    cameraIn= None
    with open(filename, 'rb') as saveFile:
        modelIn, cameraIn = dill.load(saveFile)
#    modelIn.world.currentArea.soundManager.spinUpAgain(cached)
    return modelIn, cameraIn
    #transferCamera.screen = screensave
    #model.loadState = loadState