
import pygame
class camera():
        x=0
        y=0
        horzTilesPerScreen=30
        resx=1024
        resy=768
        subx=100
        suby=100
        subwid=800
        subhig=600
        def gridSize(self):
            return camera.subwid/camera.horzTilesPerScreen
        def getXYForXY(self,x,y):
            return (self.subx+(x-self.x)*self.gridSize(),
                    self.suby+(y-self.y)*self.gridSize(),)
                    
        def getRectForXY(self,x,y):
            return (self.subx+(x-self.x)*self.gridSize(),
                    self.suby+(y-self.y)*self.gridSize(),
                    self.subx+((x-self.x)+1)*self.gridSize(),
                    self.suby+((y-self.y)+1)*self.gridSize())
        def getRectForRect(self,rect):
            return (self.subx+(rect[0]-self.x)*self.gridSize(),
                    self.suby+(rect[1]-self.y)*self.gridSize(),
                    self.subx+(rect[2]-self.x)*self.gridSize(),
                    self.suby+(rect[3]-self.y)*self.gridSize())
        
