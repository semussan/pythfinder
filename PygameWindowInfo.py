"""
http://www.akeric.com/python/pygameWindowInfo/pygameWindowInfo_0_1.py
Eric Pavey - warpcat@sbcglobal.net - 2009-10-25
http://www.akeric.com/blog
Permission to use and modify given by author, as long as author is given credit.

Python module containing class allowing the user to query Pygame window and
display screen extent values.  Comes with unit test to show example usage.

Tested in WinXP, Python 2.6.2, Pygame 1.9.1
"""
__version__ = "0.1"

import os
from ctypes import POINTER, WINFUNCTYPE, windll
from ctypes.wintypes import BOOL, HWND, RECT

import pygame

class PygameWindowInfo(object):
    """
    Create an object that will allow the user to query both the current position
    of the Pygame window, but the position of the main display screen inside,
    relative to the resolution of the current computer monitor\flatscreen.

    IMPORTANT:  PygameWindowInfo.updateObject() must be called to during every
    cycle of the Pygame main loop to keep the system updated, or unexpected
    results could occur
    """
    def __init__(self):
        """Initialize our object"""
        # Find the start x,y pos of the main pygame *screen* (the screen in the
        # window):
        sdlpos = os.getenv("SDL_VIDEO_WINDOW_POS")
        if sdlpos is None:
            raise Exception("Must have previously setup a Pygame window starting position via the 'SDL_VIDEO_WINDOW_POS' evn var.")
        self.initPygameScreenPos = [int(i) for i in sdlpos.split(",")]

        # Run our ctypes code to query window position:
        try:
            # It's said that not all systems support this dictionary key.  I'm
            # not sure what systmes those are, but might as well put a check in.
            self.hwnd = pygame.display.get_wm_info()["window"]
        except KeyError:
            raise Exception("Your system isn't accepting the code: 'pygame.display.get_wm_info()[\"window\"]', must not be supported :-(")
        self.prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
        self.paramflags = (1, "hwnd"), (2, "lprect")
        self.GetWindowRect = self.prototype(("GetWindowRect", windll.user32), self.paramflags)

        # Find the initial *window* position:
        rect = self.GetWindowRect(self.hwnd)
        # Calculate the thickness of the *window* border to the *screen* object inside:
        self.borderThickness = int(self.initPygameScreenPos[0]) - rect.left
        self.titleThickness = int(self.initPygameScreenPos[1]) - rect.top
        # borderThickness is the left, right, and bottom window edges.  titleThickness
        # is th thickness of the top title-bar of the window.

    def getWindowPosition(self):
        """
        Return a dict with the top, bottom, left, and right coordinates for the
        the Pygame *window*:  The frame around the Pygame screen.
        """
        rect = self.GetWindowRect(self.hwnd)
        return {"top":rect.top, "bottom":rect.bottom, "left":rect.left, "right":rect.right}

    def getScreenPosition(self):
        """
        Return a dict with the top, bottom, left, and right coordinates for the
        the Pygame *screen*:  The active area inside the Pygame window borders.
        """
        rect = self.GetWindowRect(self.hwnd)
        return {"top":rect.top+self.titleThickness, "bottom":rect.bottom-self.borderThickness,
                "left":rect.left+self.borderThickness, "right":rect.right-self.borderThickness}

    def update(self):
        """
        Should be called once during every cycle in the Pygame main loop, to
        keep the environment updated with the latest pygame screen position.
        Very important.  If you don't do this, unexpected results!
        """
        data = self.getScreenPosition()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%s,%s"%(data["left"], data["top"])


# Unit Testing:
if __name__ == "__main__":
    """Unit Test, will print window, screen and border thicknesses to the shell."""

    pygame.init()

    # Must set this env var for PygameWindowInfo to work!
    os.environ['SDL_VIDEO_WINDOW_POS'] = "128,128"

    screen = pygame.display.set_mode((256, 256), pygame.RESIZABLE)
    pygame.display.set_caption("PygameWindowInfo v%s"%__version__)

    # Creat our object:
    winInfo = PygameWindowInfo()

    # Main loop:
    looping = True
    while looping:
        # ***Must update our winInfo object during every loop*** to accurately
        #  track window and display screen position
        winInfo.update()

        screen.fill(pygame.Color("black"))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                looping = False
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        winPos = winInfo.getWindowPosition()
        screenPos = winInfo.getScreenPosition()

        # Print interesting data!
        print "Window -",
        for key in winPos.keys():
            print "%s: %s"%(key, winPos[key]),
        print " |  Screen -",
        for key in screenPos.keys():
            print "%s: %s"%(key, screenPos[key]),
        print " |  Title thickness: %s"%winInfo.titleThickness,
        print " |  Border thickness: %s"%winInfo.borderThickness,
        print "\n",

        pygame.display.flip()

    pygame.quit()

