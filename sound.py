import pygame
import os
from Editable import Editable

class Bgtrack(Editable):
    def __init__(self, x, y, vol, isLocalized,filename,uuid,cached):
        self.rect=(x,y,1,1)
        self.uuid=uuid
        self.filename=filename
        self.imgName=filename
        self.volumeoffset=vol
        self.isLocalized=isLocalized
        self.startSound(cached)
    def setDistVolume(self, vol,cached):
        self.runIfNeed(cached)
        cached.bgsounds()[self.uuid].set_volume(self.volumeoffset*vol)
    def startSound(self,cached):
        cached.bgsounds()[self.uuid] = pygame.mixer.Sound(self.filename)
        #soundChannelObj=cached.bgsoundChannels()[self.uuid] = pygame.mixer.Sound(self.filename)
        cached.bgsounds()[self.uuid].set_volume(self.volumeoffset)
        cached.bgsounds()[self.uuid].play(-1)
    def runIfNeed(self,cached):
         if self.uuid not in cached.bgsounds() or cached.bgsounds()[self.uuid] is None:
            self.startSound(cached)

    def draw(self, screen, camera,cached ,model):
        x,y = (self.rect[0],self.rect[1])
        img=None
        if self.isLocalized:
            if not cached._lSoundImg:
                cached._lSoundImg = pygame.image.load('coreImgs/localSound.png')
            img = cached._lSoundImg
        else:
            if not cached._gSoundImg:
                cached._gSoundImg = pygame.image.load('coreImgs/globalSound.png')
            img = cached._gSoundImg
        newrect = camera.getRectForRect((x,y,1,1))
        cached.screen(camera).blit(img, newrect)

    def isNonlocalizedClicked(self, x, y,camera):
        if camera.inBounds((0, 0, 1, 1), x, y):
            return self
    def onDeletePress(self,camera,cached,model):
        self.markedForDeletion = True
        camera.target = None
        cached.bgsounds()[self.uuid].stop()
        cached.bgsounds()[self.uuid]= None
        model.world.currentArea.soundManager.bgtracks.remove(self)


class SoundManager():
    bgtracks=[]
    uuid=0

    def __init__(self):
        print 'Initing sound '
        self.manager=pygame.mixer.pre_init(44100, -16, 2, 2048)
    def unload(self,cached):
        for bg in self.bgtracks:
            cached.bgsounds()[bg.uuid].stop()
            cached.bgsounds()[bg.uuid]=None
        pygame.mixer.stop()
    def clearRunningAndStored(self,cached ):
        for bg in self.bgtracks:
            cached.bgsounds()[bg.uuid].stop()
        pygame.mixer.stop()
        self.bgtracks=[]
    def spinUpAgain(self,cached):
         for bgtrack in self.bgtracks:
             bgtrack.runIfNeed(cached)
    def update(self,camera,cached):
        for bgtrack in self.bgtracks:
            if bgtrack.isLocalized:
                camx, camy=camera.getCameraCenter()
                dist=((bgtrack.rect[0]-camx)**2 + (bgtrack.rect[1]-camy)**2)**.5
                saturationRange=12
                falloffPower=2.6
                if dist<saturationRange : dist=saturationRange
                bgtrack.setDistVolume((saturationRange**falloffPower)/(dist**falloffPower),cached)
            else:
                bgtrack.setDistVolume(1,cached)
    def draw(self, screen, camera,cached ,model):
        for sound in self.bgtracks:
            sound.draw(screen,camera,cached,model)

    def addBG(self,x,y,vol,isLocalized,filename,cached):
        self.bgtracks.append(Bgtrack(x,y,vol,isLocalized,filename,self.uuid,cached))
        self.uuid+=1
        
    def playOnce(self,filename,vol):
        sound = pygame.mixer.Sound(filename)
        sound.set_volume(vol)
        sound.play(0)

    def click(self, x, y, clicktype, camera, newClick,targetBackground):
        if newClick:
            for sound in self.bgtracks:
                return sound.isClicked( x, y,camera)
    def getTarget(self, x, y,camera,targetBackground):
        for sound in self.bgtracks:
            return  sound.isClicked( x, y,camera)
              

