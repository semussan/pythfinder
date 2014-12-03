import pygame
import os
from itertools import cycle
import random

class BattleManager():
    def __init__(self, camera):
        self.list=[]
        self.cycle=cycle(self.list)
        self.camera=camera
        self.timeCursor=0
        self.curTarget=None
        self.started=False
    def cycleNextPlayer(self):
        if len(self.list):
            self.curTarget=self.cycle.next()
            return self.curTarget[0]
        else:
            return None
    def getCurPlayer(self):
        if len(self.list):
            return self.curTarget[0]
        else:
            return None
    def addPlayer(self, target, init=None):
        init2=init
        if not init2:
            if self.started:
                init2=self.curTarget[1]
            else:
                init2=random.randint(1, 20)
        print '1', self.list
        new=(target,init2)
        self.list.insert(0,new)
        self.list=sorted(self.list,key=lambda x:x[1])
        if self.curTarget:
            curInd=self.list.index(self.curTarget)
        else:
            curInd=None
        self.cycle=cycle(self.list)
        #reposition new cycle
        cycleTarget=self.cycle.next()
        if self.curTarget and curInd:
            while cycleTarget is not self.curTarget:
                cycleTarget=self.cycle.next()
        else:
            self.curTarget= new
        print '2', self.list
    def has(self, target):
        return len([x for x in self.list if x[0] is target])  >0
        
    def removePlayer(self, target):
        targetEntries=[x for x in self.list if x[0] is target]
        if not targetEntries:
            return False
        targetEntry=targetEntries[0]
        print '1', self.list, targetEntry
        if self.curTarget[0] is target:
            if len(self.list)>1:
                self.curTarget=self.cycle.next()
            else:
                self.curTarget=None
                
        print '1.2', self.curTarget
            
        self.list.remove(targetEntry)
        self.list=sorted(self.list,key=lambda x:x[1])
        self.cycle=cycle(self.list)
        #reposition new cycle
        cycleCursor=self.cycle.next()
        if self.curTarget and cycleCursor:
            while cycleCursor is not self.curTarget:
                cycleCursor=self.cycle.next()
        print '2', self.list, self.curTarget, cycleCursor

    def startBattle(self):
        self.list=sorted(self.list,key=lambda x:x[1])
        self.cycle=cycle(self.list)
        self.started=True

        
            

if __name__ == '__main__':
    bm=BattleManager(None)
    bm.addPlayer('tod',4)
    bm.addPlayer('and',2)
    bm.addPlayer('wat',20)
    bm.addPlayer('may',7)
    assert bm.cycleNextPlayer()=='may'
    assert bm.cycleNextPlayer()=='wat'
    assert bm.cycleNextPlayer()=='and'
    assert bm.cycleNextPlayer()=='tod'
    assert bm.cycleNextPlayer()=='may'
    assert bm.cycleNextPlayer()=='wat'
