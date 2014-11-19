import pygame
import os

class bgtrack():
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
    bgtracks=[]
    def __init__(self,camera):
        self.camera=camera
        self.manager=pygame.mixer.pre_init(44100, -16, 2, 2048)
        
    def addBG(self,x,y,vol,filename):
        self.bgtracks.append(bgtrack(x,y,vol,filename))
              
    def update(self):
        for bgtrack in self.bgtracks:
            camx, camy=self.camera.getCameraCenter()
            dist=((bgtrack.x-camx)**2 + (bgtrack.y-camy)**2)**.5
            saturationRange=12
            falloffPower=2.6
            if dist<saturationRange : dist=saturationRange
            bgtrack.setDistVolume((saturationRange**falloffPower)/(dist**falloffPower))
        
