__author__ = 'tyoung'
import pygame

shadowDist = 12
lightDist = 10


def getNeighbors(widthx, widthy, x, y, camera):
    posibleNeighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                        (x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2),
                        (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)]
    posibleNeighbors.extend([(x - 3, y), (x + 3, y), (x, y - 3), (x, y + 3),
                             (x - 2, y + 1), (x - 2, y - 1), (x + 2, y + 1), (x + 2, y - 1),
                             (x - 1, y - 2), (x - 1, y + 2), (x + 1, y - 2), (x + 1, y + 2)])
    neighbors = []
    for neighbor in posibleNeighbors:
        if camera.inBounds((0, 0, widthx, widthy), neighbor[0], neighbor[1]):
            neighbors.append(neighbor)
    return neighbors


class FoWMap():
    def __init__(self, rect, hasShadows):
        level = 0
        if hasShadows:
            level = 2

        self.foglevels = [[level for x in range(rect[3])] for x in range(rect[2])]
        self.rect = rect

    def redark(self):
        self.foglevels = [[2 for x in range(self.rect[3])] for x in range(self.rect[2])]

    def fogUnattended(self,model,parentBackground):
        for x in range(self.rect[2]):
            for y in range(self.rect[3]):
                if self.foglevels[x][y] is 0:
                    seen=False
                    for player in model.world.players:
                        adjustedx,adjustedy= x+parentBackground.rect[0],y+parentBackground.rect[1]
                        if ((player.rect[0] - adjustedx) ** 2 + (player.rect[1] - adjustedy) ** 2) ** .5 < lightDist:
                            seen=True;
                            break
                    if not seen:
                        self.foglevels[x][y]=1
    def drawSingleFoW(self, screen, camera, x, y, level,cached,prerect):
        screen.blit(cached.fogImgs(camera)[level], (prerect[0]+ camera.gridSize*x, prerect[1]+ camera.gridSize*y))
        # pygame.draw.rect(screen,(level*30,0,0),rect,0)

    def draw(self, screen, camera,cached):
        prerect = camera.getRectForXY(self.rect[0], self.rect[1])
        clippedx=camera.clippedXRange(self.rect[0],self.rect[0]+self.rect[2],self.rect[0])
        clippedy=camera.clippedYRange(self.rect[1],self.rect[1]+self.rect[3],self.rect[1])
        for x in clippedx:
            for y in clippedy:
                if self.foglevels[x][y] > 0:
                    self.drawSingleFoW(screen, camera, x, y, self.foglevels[x][y],cached,prerect)

    def revealOld(self, x, y, camera):
        self.foglevels[x][y] = 0
        for neighbor in getNeighbors(self.rect[2], self.rect[3], x, y, camera):
            if self.foglevels[neighbor[0]][neighbor[1]] > 0:
                if abs(neighbor[0] - x) + abs(neighbor[1] - y) <= 2:
                    self.foglevels[neighbor[0]][neighbor[1]] = 0
                else:
                    self.foglevels[neighbor[0]][neighbor[1]] = 1

    def click(self, x, y, clicktype, camera):
        camera.target = None
        try:
            if clicktype == 1:
                self.foglevels[x][y] = 0
                for neighbor in getNeighbors(self.rect[2], self.rect[3], x, y, camera):
                    if self.foglevels[neighbor[0]][neighbor[1]] > 0:
                        if abs(neighbor[0] - x) + abs(neighbor[1] - y) <= 2:
                            self.foglevels[neighbor[0]][neighbor[1]] = 0
                        else:
                            self.foglevels[neighbor[0]][neighbor[1]] = 1
            #if clicktype == 2:
            #    if self.foglevels[x][y] is not 2:
            #        self.foglevels[x][y] = 1  # was 2
            #    for neighbor in getNeighbors(self.rect[2], self.rect[3], x, y, camera):
            #        if self.foglevels[neighbor[0]][neighbor[1]] < 2:
            #            if abs(neighbor[0] - x) + abs(neighbor[1] - y) <= 2:
            #                self.foglevels[neighbor[0]][neighbor[1]] = 1  # was 2
            #            else:
            #                self.foglevels[neighbor[0]][neighbor[1]] = 1
            if clicktype == 2:
                self.foglevels[x][y] = 2  # was 2
                for neighbor in getNeighbors(self.rect[2], self.rect[3], x, y, camera):
                    if self.foglevels[neighbor[0]][neighbor[1]] < 2:
                        if abs(neighbor[0] - x) + abs(neighbor[1] - y) <= 2:
                            self.foglevels[neighbor[0]][neighbor[1]] = 2  # was 2
                        else:
                            self.foglevels[neighbor[0]][neighbor[1]] = 2
                            # print self.foglevels[x][y]
        except:
            pass

    ########http://www.roguebasin.com/index.php?title=PythonShadowcastingImplementation
    # Python shadowcasting implementation stuff starts here
    mult = [
        [1, 0, 0, -1, -1, 0, 0, 1],
        [0, 1, -1, 0, 0, -1, 1, 0],
        [0, 1, 1, 0, 0, -1, -1, 0],
        [1, 0, 0, 1, -1, 0, 0, -1]
    ]

    def square(self, x, y):
        return self.foglevels[x][y]
    def blocked(self, x, y, sourcex,sourcey,parentArea,parentBackground,camera,cached):
        return parentArea.doLinesBlock(sourcex+parentBackground.rect[0],sourcey+parentBackground.rect[1],x+parentBackground.rect[0], y+parentBackground.rect[1]) or parentArea.isSquareOpaque(x, y, parentBackground.rect[0], parentBackground.rect[1],camera,cached)
        # return (x < 0 or y < 0
        #        or x >= self.rect[2] or y >= self.rect[3]
        #        or self.data[y][x] == "#")
    def lit(self, x, y):
        return self.foglevels[x][y] == self.flag

    def set_lit(self, x, y, origx, origy):
        if 0 <= x < self.rect[2] and 0 <= y < self.rect[3]:
            if ((x - origx) ** 2 + (y - origy) ** 2) ** .5 <= lightDist:
                self.foglevels[x][y] = 0
            elif self.foglevels[x][y] > 0:
                self.foglevels[x][y] = 1

    def _cast_light(self, cx, cy, row, start, end, radius, xx, xy, yx, yy, id, origx, origy,parentArea,parentBackground,camera,cached):
        "Recursive lightcasting function"
        if start < end:
            return
        radius_squared = radius * radius
        for j in range(row, radius + 1):
            dx, dy = -j - 1, -j
            blocked = False
            while dx <= 0:
                dx += 1
                # Translate the dx, dy coordinates into map coordinates:
                X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
                # l_slope and r_slope store the slopes of the left and right
                # extremities of the square we're considering:
                l_slope, r_slope = (dx - 0.5) / (dy + 0.5), (dx + 0.5) / (dy - 0.5)
                if start < r_slope:
                    continue
                elif end > l_slope:
                    break
                else:
                    # Our light beam is touching this square; light it:
                    if dx * dx + dy * dy < radius_squared:
                        self.set_lit(X, Y, origx, origy)
                    if blocked:
                        # we're scanning a row of blocked squares:
                        if self.blocked(X, Y, origx,origy,parentArea,parentBackground,camera,cached):
                            new_start = r_slope
                            continue
                        else:
                            blocked = False
                            start = new_start
                    else:
                        if self.blocked(X, Y,origx,origy,parentArea,parentBackground,camera,cached) and j < radius:
                            # This is a blocking square, start a child scan:
                            blocked = True
                            self._cast_light(cx, cy, j + 1, start, l_slope,
                                             radius, xx, xy, yx, yy, id + 1, origx, origy,parentArea,parentBackground,camera,cached)
                            new_start = r_slope
            # Row is scanned; do next row unless last square was blocked:
            if blocked:
                break

    def reveal(self, x, y, camera, cached, parentArea,parentBackground, radius=shadowDist):
        if x < -shadowDist or x >= parentBackground.rect[2] + shadowDist or y < -shadowDist or y >= parentBackground.rect[3] + shadowDist:
            return  # we're too far away to care
        "Calculate lit squares from the given location and radius"
        # self.flag += 1
        for oct in range(8):
            self._cast_light(x, y, 1, 1.0, 0.0, radius,
                             self.mult[0][oct], self.mult[1][oct],
                             self.mult[2][oct], self.mult[3][oct], 0, x, y,parentArea,parentBackground,camera,cached)
