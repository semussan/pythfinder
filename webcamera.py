from time import time
import os
import glob
directory=r'screenshots'
class WebCamera(object):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""
    lastImg=""
    def __init__(self):
        pass
        #self.frames = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]

    def get_frame(self):

        try:
            fileName=sorted(glob.iglob(directory+'\*.jpg'), key=os.path.getmtime)[-2]
            self.lastImg = open(fileName, 'rb').read()
        except:
            pass
        return self.lastImg
