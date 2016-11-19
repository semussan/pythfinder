import pygame
from Area import Area
from Entity import Entity

class World():
    def __init__(self, model, camera,cached, campaignName):
        self.campaignName = campaignName
        self.joystickBindings = {}
        self.players = []
        pygame.joystick.init()
        pygame.init()
        self._areas = {}
        self.currentArea = None
        with open(campaignName + "/starting_area", 'rb') as f:
            startingArea = campaignName + "/" + f.readline()
            self.setArea(startingArea,camera,model,cached)

    def setArea(self, fileName,camera,cached, x=0, y=0):
        cached.clear()
        if self.currentArea:
            self.currentArea.soundManager.unload(cached)
        if fileName not in self._areas:
            self._areas[fileName] = Area(self.campaignName)
        self.currentArea = self._areas[fileName]
        self.currentArea.soundManager.spinUpAgain(cached)
        #self.currentArea.blood=[]

        # set players to desired positions
        def spiral(X, Y):
            x = y = 0
            dx = 0
            dy = -1
            for i in range(max(X, Y)**2):
                if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):
                    yield (x,y)
                if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                    dx, dy = -dy, dx
                x, y = x+dx, y+dy
        for player in self.players:
            for offset in spiral(5,5):
                if not self.getTarget(x + offset[0], y + offset[1], camera, False):
                    player.rect= (x + offset[0],y + offset[1],player.rect[2],player.rect[3])
                    self.reveal(x + offset[0],y + offset[1],camera,cached)
                    break
        camera.recenter(x,y)

    def initPlayers(self,camera,cached):
        # if self.joystickBindings:
        #    [x.quit() for x in self.joystickBindings]
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        with open(self.campaignName + "/" + 'players', 'rb') as playersFile:
            for player in playersFile:
                parsed = player.strip().split(' ')
                linetype, args = (parsed[0], parsed[1:])
                if linetype == 'npc':
                    x, y, width, height, maxHealth, movable, cycleTime, filename = args
                    newChar = Entity(self.campaignName + "/" + filename.strip(),
                                     (int(x), int(y), int(width), int(height),), int(maxHealth), movable == 'True',
                                     int(cycleTime))
                    self.players.append(newChar)
                    self.reveal(newChar.rect[0],newChar.rect[1],camera,cached)
                    newChar.isPlayer = True
                    if joysticks:
                        newJoystick = joysticks.pop()
                        newJoystick.init()
                        self.joystickBindings[newJoystick] = newChar

    def reconnectJoysticks(self):
        # if self.joystickBindings:
        #    [x.quit() for x in self.joystickBindings]
        if not self.joystickBindings:
            self.entities = [x for x in self.entities if not x.isPlayer]
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            with open(self.subdir + 'players', 'rb') as playersFile:
                for player in playersFile:
                    parsed = player.strip().split(' ')
                    linetype, args = (parsed[0], parsed[1:])
                    if linetype == 'npc':
                        x, y, width, height, maxHealth, movable, cycleTime, filename = args
                        newChar = Entity(self.model, self.camera, self.subdir + filename.strip(),
                                         (int(x), int(y), int(width), int(height),), int(maxHealth), movable == 'True',
                                         int(cycleTime))
                        self.entities.append(newChar)
                        newChar.isPlayer = True
                        if joysticks:
                            newJoystick = joysticks.pop()
                            newJoystick.init()
                            self.joystickBindings[newJoystick] = newChar
        else:
            players = [x for x in self.entities if x.isPlayer]
            for num, oldJoystick in enumerate(self.joystickBindings):
                playerName = self.joystickBindings[oldJoystick].imgName
                self.joystickBindings[oldJoystick] = [x for x in players if x.imgName == playerName][-1]

    def draw(self, screen, camera,cached,model):
        self.currentArea.draw(screen, camera,cached,model)
        for player in self.players:
            player.draw(screen, camera,cached,model)

    def update(self,camera,cached,model):
        self.players = [x for x in self.players if not x.markedForDeletion]
        self.currentArea.update(camera,cached,model)
        for sprite in self.allEntities():
            numUpdates = 4 if camera.battleManager else 1
            for x in range(numUpdates):
                sprite.update()

    def allEntities(self):
        return sorted(self.currentArea.entities + self.players, key=lambda x: x.rect[1])

    def click(self, x, y, clicktype, camera, newClick,targetBackground,targetShadow):
        if newClick:
            for player in self.players[::-1]:
                ret = player.click(x , y , clicktype, camera)
                if ret:
                    return ret
        return self.currentArea.click(x, y, clicktype, camera, newClick,targetBackground,targetShadow)

    def getTarget(self, x, y,camera,targetBackground):
        for player in self.players[::-1]:
                ret = player.isClicked(x , y , camera)
                if ret:
                    return ret
        return self.currentArea.getTarget(x, y, camera,targetBackground)

    def reveal(self, x, y, camera, cached):
        self.currentArea.reveal(x, y, camera,cached)

    def interact(self, player,model,camera,cached):
        if player.lastMove:
            px, py = player.rect[0], player.rect[1]
            x, y = (player.lastMove[0] + px, player.lastMove[1] + py)  # get where the player was 'facing'
            for sprite in self.allEntities():
                if camera.inBounds(sprite.rect, x, y):
                    if sprite.interactionString:
                        sprite.interaction(model,camera,cached)
                    else:
                        portrait=cached.portrait(sprite.imgName)
                        if not portrait:
                            portrait=cached.getImgs(player.imgName)[0]
                        camera.show(sprite)
                        camera.addDialog(player, 'left')
                    return
