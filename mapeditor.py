import pygame as pg
import json


class edit:

    editing = False
    start = None
    makeblock = False
    black = (0, 0, 0)
    screenstart = [0, 0]

    def __init__(self, width, height):
        self.hw = width/2
        self.hh = height/2

    def keyhandle(self, event, campos):

        if event:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.start:
                        self.start = (event.pos[0] + campos[0] - self.hw,
                                      event.pos[1] + campos[1] - self.hh)
                        self.screenstart[0] = event.pos[0]
                        self.screenstart[1] = event.pos[1]
                    else:
                        self.makeblock = True
                        self.start = None

    def draw(self, surface, camdeltapos):

        if self.start:
            self.screenstart[0] += camdeltapos[0]
            self.screenstart[1] += camdeltapos[1]
            current = pg.mouse.get_pos()
            nwidth = current[0] - self.screenstart[0]
            nheight = current[1] - self.screenstart[1]
            rectangle = (self.screenstart[0], self.screenstart[1], nwidth, nheight)
            pg.draw.rect(surface, self.black, rectangle, 3)

    def makeblock(self):
        g
