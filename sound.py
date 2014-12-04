import pygame
import os

class Bgtrack():
    def __init__(self, x, y, vol, filename):
        self.x=x
        self.y=y
        self.filename=filename
        self.volumeoffset=vol
        print filename
        self.soundobj=pygame.mixer.Sound(filename)#load music
        self.channel=self.soundobj.play(-1)
        self.soundobj.set_volume(self.volumeoffset)
    def setDistVolume(self, vol):
        self.soundobj.set_volume(self.volumeoffset*vol)
        

class SoundManager():
    bgtracksSaves=[]
    bgtracks=[]
    def __init__(self,camera):
        self.camera=camera
        self.manager=pygame.mixer.pre_init(44100, -16, 2, 2048)
    def reset(self):
        for bg in self.bgtracks:
            bg.soundobj.stop()
        self.bgtracks=[]
        bgtracksSaves=[]
        
    def update(self):
        if self.bgtracksSaves and not self.bgtracks:
            for bgsave in self.bgtracksSaves:
                self.bgtracks.append(Bgtrack(*bgsave))
        for bgtrack in self.bgtracks:
            camx, camy=self.camera.getCameraCenter()
            dist=((bgtrack.x-camx)**2 + (bgtrack.y-camy)**2)**.5
            saturationRange=12
            falloffPower=2.6
            if dist<saturationRange : dist=saturationRange
            bgtrack.setDistVolume((saturationRange**falloffPower)/(dist**falloffPower))
                
        
    def addBG(self,x,y,vol,filename):
        self.bgtracks.append(Bgtrack(x,y,vol,filename))
        self.bgtracksSaves.append((x,y,vol,filename))
        
    def playOnce(self,filename,vol):
        sound = pygame.mixer.Sound(filename)
        sound.set_volume(vol)
        sound.play(0)
              

