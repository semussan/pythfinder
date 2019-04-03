__author__ = 'tyoung'
import pygame
from Entity import Entity
import random
import types
from Background import Background
from sound import SoundManager
from BlockLine import BlockLine
from Shadows import lightDist

def ccw(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
def intersect(A,B,C,D):
        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Area():
    backgrounds = []
    blocklines = []
    entities = []
    blood = []
    soundManager = None

    def __init__(self, campaignName):
        self.campaignName = campaignName
        self.soundManager = SoundManager()
        self.blocklines=[]
        pygame.joystick.init()
        pygame.init()


    def drawHighlight(self, screen, camera, rect):
        rect = camera.gridRectToCameraRect(rect)
        trans = pygame.Surface((rect[2], rect[3],))
        trans.set_alpha(128)
        trans.fill((10, 10, 100))
        screen.blit(trans, (rect[0], rect[1]))

    def draw(self, screen, camera,cached,model):
        for background in self.backgrounds:
            background.update()
            background.draw(screen, camera, cached, model)
        for bloodDrop in self.blood:
            self.drawBlood(bloodDrop, screen, camera, cached)
        if camera.battleManager and camera.battleManager.started and camera.battleManager.getCurPlayer():
            camera.drawHighlight(camera.battleManager.getCurPlayer().rect, (100, 10, 10), 128, cached)
        for sprite in self.entities:
            sprite.draw(screen, camera,cached,model)

    def drawFogOfWar(self, screen, camera,cached):
        for background in self.backgrounds:
            background.drawFoW(screen, camera,cached)

    def drawLines (self, screen, camera,cached,model):
        for blockLine in self.blocklines:
            blockLine.draw(screen, camera,cached,model)


    def drawBlood(self, bloodDrop, screen, camera,cached):
        screen.blit(cached.bloodImgs()[bloodDrop[2]], camera.gridRectToCameraRect((bloodDrop[0], bloodDrop[1], 1, 1)))

    def addBlood(self, x, y,cached):
        self.blood.append((x, y, random.randint(0, len(cached.bloodImgs()) - 1)))

    def reveal(self, x, y, camera,cached, ):
        for background in self.backgrounds:
            #    if camera.inBounds(background.getBounds(), x, y):
            background.reveal(x - background.rect[0], y - background.rect[1], camera,cached,self)

    click_count = 0
    def click(self, x, y, clicktype, camera, newClick,targetBackground,targetShadow):
        Area.click_count+=1
        if newClick:
            targeted = [entity for entity in self.entities if entity.in_click(x,y,camera)]
            if targeted: #TODO have these and similiar functions return a list of targeted things, implementing clickable, and isClicked and click seperately 
                click_mod = Area.click_count % len(targeted)
                target = targeted[click_mod]
                target.click(x , y , clicktype, camera)
                return target

            for blockline in self.blocklines:
                ret = blockline.isClicked (x , y ,  camera)
                if ret: return ret

        for background in self.backgrounds:
            ret = self.soundManager.click( x, y, clicktype, camera, newClick,targetBackground)
            if ret: return ret
            if camera.inBounds(background.getBounds(), x, y):
                ret = background.click(x - background.rect[0], y - background.rect[1], clicktype, camera,targetShadow)
                if ret and targetBackground: return ret

    def getTarget(self,x, y, camera,targetBackground):
        for sprite in self.entities:
            ret = sprite.isClicked(x, y, camera)
            if ret:
                return ret
        if targetBackground:
            ret = self.soundManager.click( x, y, clicktype, camera, newClick,targetBackground)
            if ret: return ret
            for background in self.backgrounds:
                if camera.inBounds(background.getBounds(), x, y):
                    return background
        ret = self.soundManager.getTarget( x, y,camera,targetBackground)
        if ret: return ret


    def isSquareOpaque(self, x, y, xoffset, yoffset,camera,cached):
        globx = xoffset + x
        globy = yoffset + y

        for blocker in [x for x in self.entities if x.blocking]:
            if camera.inBounds(blocker.rect, globx, globy):
                return True
        backgroundFound=False
        for background in self.backgrounds:
            if camera.inBounds(background.getBounds(), globx, globy):
                img = cached.getImg(background.imgName, idx = 0)
                xpixel = img.get_width() * (float(globx - background.rect[0] + .5) / background.rect[2])
                ypixel = img.get_height() * (float(globy - background.rect[1] + .5) / background.rect[3])
                pix = img.get_at((int(xpixel), int(ypixel)))
                backgroundFound = backgroundFound or pix.a > 127

        return True and not backgroundFound

    def isShrouded(self,rect,camera):
        if camera.drawShadows:
            for background in self.backgrounds:
                if camera.inBounds(background.rect, rect[0], rect[1]):
                    for sx in range(rect[0],rect[0]+rect[2]):
                        for sy in range(rect[1],rect[1]+rect[3]):
                            try: #TODO make this error reproducable and fix
                                if  background.FoW.foglevels[sx-background.rect[0]][sy-background.rect[1]] is 0:
                                    return False
                            except:
                                pass
            return True
        else:
            return False

    def update(self,camera,cached,model):
        self.entities = [x for x in self.entities if not x.markedForDeletion]
        self.blocklines = [x for x in self.blocklines if not x.markedForDeletion]
        self.backgrounds = [x for x in self.backgrounds if not x.markedForDeletion]
        self.soundManager.bgtracks = [x for x in self.soundManager.bgtracks if not x.markedForDeletion]
        self.soundManager.update(camera,cached)
        for background in self.backgrounds:
            background.FoW.fogUnattended(model,background)
    def distBetweenBoxes(self, rect1, rect2):
        shortest = min(hypotenuse(p1, p2) for p1, p2 in itertools.product(lst_a, lst_b))

    def addVerticalBlockLine(self,rect):
        self.blocklines.append(BlockLine(rect,True))
    def addHorizontalBlockLine(self,rect):
        self.blocklines.append(BlockLine(rect,False))

    def doLinesBlock(self,x, y, sourcex,sourcey):
        for blockLine in [i for i in  self.blocklines if abs(sourcex - i.rect[0])<lightDist+i.rect[2] and abs(sourcey - i.rect[1])<lightDist+i.rect[3] ]:
            if blockLine.isVert:
                if intersect((x+.5,y+.5),(sourcex+.5,sourcey+.5), (blockLine.rect[0],blockLine.rect[1]),(blockLine.rect[0],blockLine.rect[1]+blockLine.rect[3])):
                    return True
            else:
                if intersect((x+.5,y+.5),(sourcex+.5,sourcey+.5), (blockLine.rect[0],blockLine.rect[1]),(blockLine.rect[0]+blockLine.rect[2],blockLine.rect[1])):
                    return True

        return False


