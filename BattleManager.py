import pygame
import os
from itertools import cycle
import random


class BattleManager():
    def __init__(self, camera):
        self.list = []
        #self.cycle = cycle(self.list)
        self.camera = camera
        self.timeCursor = 0
        self.curTarget = None
        self.started = False

    def cycleNextPlayer(self):
        if len(self.list):
            item = self.list[0]
            self.list = self.list[1:]
            self.list.append(item)
            #self.curTarget = self.cycle.next()
            return self.list[0][0]
        else:
            return None

    def getCurPlayer(self):
        if len(self.list):
            return self.list[0][0]
        else:
            return None

    def addPlayer(self, target, init=None):
        if not init:
            if len(self.list):
                init = self.list[0][1] - .0001 #set to current target's init
            else:
                init = random.randint(1, 20)

        new = (target, init)
        self.list.insert(0, new)

    def has(self, target):
        return len([x for x in self.list if x[0] is target]) > 0

    def removePlayer(self, target):
        self.list = [x for x in self.list if x[0] is not target]

    def startBattle(self):
        self.list = sorted(self.list, key=lambda x: x[1])
        self.started = True


if __name__ == '__main__':
    bm = BattleManager(None)
    bm.addPlayer('tod', 4)
    bm.addPlayer('and', 2)
    bm.addPlayer('wat', 20)
    bm.addPlayer('may', 7)
    assert bm.cycleNextPlayer() == 'may'
    assert bm.cycleNextPlayer() == 'wat'
    assert bm.cycleNextPlayer() == 'and'
    assert bm.cycleNextPlayer() == 'tod'
    assert bm.cycleNextPlayer() == 'may'
    assert bm.cycleNextPlayer() == 'wat'
