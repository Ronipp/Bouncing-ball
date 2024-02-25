import pygame as pg
import numpy as np
import json
pg.font.init()


class ball:

    tnum = 10
    omega = 0
    fii = 0
    img = pg.image.load('ball.png')

    def __init__(self, position, velocity, radius, color):

        self.color = color
        self.pos = position
        self.radius = radius
        self.vel = velocity
        self.screenpos = position
        self.past = [[int(position[0]), int(position[1])]]

    def move(self, dt):

        accel = 15 - 0.3 * self.vel[1]
        airrx = -0.3 * self.vel[0]
        self.vel[1] += accel * dt
        if abs(self.vel[1]) > 15:
            self.vel[1] = 15
        self.vel[0] += airrx * dt
        if self.vel[0] > 4.5:
            self.vel[0] = 4.5
        elif self.vel[0] < -4.5:
            self.vel[0] = -4.5
        self.pos = np.add(self.pos, self.vel)

        alpha = self.omega * dt
        self.omega -= alpha
        self.fii += self.omega
        self.fii %= 360

    def update(self, campos, deltapos, size):

        self.screenpos[0] = self.pos[0] - (campos[0] - size[0]/2)
        self.screenpos[1] = self.pos[1]

        self.past.insert(0, [int(self.screenpos[0]), int(self.screenpos[1])])
        if len(self.past) > self.tnum:
            self.past.pop()

        if deltapos != (0 or 0.):
            for pos in self.past:
                pos[0] += int(deltapos[0])

    def check(self, obstacles):

        def clamp(val, minval, maxval):
            return max(minval, min(val, maxval))

        for ob in obstacles:
            # löytää lähimmän pisteen ympyrään esteestä
            closex = clamp(self.pos[0], ob.pos[0], ob.pos[0] + ob.width)
            closey = clamp(self.pos[1], ob.pos[1], ob.pos[1] + ob.height)
            # ympyrän keskipisteen ja tämän pisteen etäisyyden neliö
            distx = self.pos[0] - closex
            disty = self.pos[1] - closey
            distsquare = (distx**2) + (disty**2)
            # onko etäisyyden neliö pienempi kuin ympyrän säteen neliö
            if distsquare < self.radius**2:
                if self.vel[1] >= 0 and self.pos[1] < ob.pos[1]:
                    self.pos[1] = ob.pos[1] - self.radius
                    self.vel[1] = -self.vel[1]
                    self.omega -= 2*self.vel[0]
                elif self.vel[1] < 0 and self.pos[1] > ob.pos[1] + ob.height:
                    self.pos[1] = (ob.pos[1] + ob.height) + self.radius
                    self.vel[1] = -self.vel[1]
                    self.omega += 2*self.vel[0]
                elif self.vel[0] > 0 and self.pos[0] < ob.pos[0]:
                    self.pos[0] = ob.pos[0] - self.radius
                    self.vel[0] = -self.vel[0]
                    self.omega += 2*self.vel[1]
                else:
                    self.pos[0] = ob.pos[0] + ob.width + self.radius
                    self.vel[0] = -self.vel[0]
                    self.omega -= 2*self.vel[1]

    def draw(self, surface):

        for pos in reversed(self.past):
            pg.draw.circle(surface, self.color, pos, int(self.radius - 2*self.past.index(pos)))

        rotimg = pg.transform.rotate(self.img, self.fii)
        imgrect = rotimg.get_rect()
        imgrect.center = self.screenpos
        surface.blit(rotimg, imgrect)


class obstacle:

    near = False

    def __init__(self, position, width, height, color, name):
        self.pos = position
        self.screenpos = position
        self.width = width
        self.height = height
        self.color = color
        self.name = name

    def update(self, camdeltapos):
        self.screenpos = [self.screenpos[0] + camdeltapos[0], self.screenpos[1] + camdeltapos[1]]

    def draw(self, surface):
        pos = [int(self.screenpos[0]), int(self.screenpos[1])]
        pg.draw.rect(surface, self.color, (pos[0], pos[1], self.width, self.height))


class camera:

    vel = [0, 0]
    deltapos = [0, 0]
    nearobstacles = []
    ftlist = []
    font = pg.font.SysFont('Comic Sans MS', 30)
    fps = 0
    goleft = False
    goright = False
    godown = False

    def __init__(self, size):
        self.size = size
        self.pos = [size[0]/2, size[1]/2]

    def move(self, ballposition):

        if ballposition[0] > self.pos[0] + self.size[0]/4:
            self.vel[0] += ballposition[0] - (self.pos[0] + self.size[0]/4)
        if ballposition[0] < self.pos[0] - self.size[0]/4:
            self.vel[0] += ballposition[0] - (self.pos[0] - self.size[0]/4)

        beforex = self.pos[0]
        accel = 0.9 * self.vel[0]
        if round(self.vel[0]) != 0:
            if self.vel[0] > 0:
                self.vel[0] -= accel
                self.pos[0] += self.vel[0]
            else:
                self.vel[0] -= accel
                self.pos[0] += self.vel[0]
        self.deltapos[0] = beforex - self.pos[0]

    def keyhandle(self, event, editor):

        done = False
        if event:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    done = True
                if event.key == pg.K_e:
                    if not editor.editing:
                        editor.editing = True
                    else:
                        editor.editing = False
                if event.key == pg.K_LEFT:
                    self.goleft = True
                if event.key == pg.K_RIGHT:
                    self.goright = True
                if event.key == pg.K_DOWN:
                    self.godown = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    self.goleft = False
                if event.key == pg.K_RIGHT:
                    self.goright = False
                if event.key == pg.K_DOWN:
                    self.godown = False
        return done

    def checkobstacles(self, obstacles):
        for ob in obstacles:
            if (ob.pos[0] > self.pos[0] + self.size[0]/2 or
               ob.pos[0] + ob.width < self.pos[0] - self.size[0]/2):
                ob.near = False
            else:
                ob.near = True
            if ob.near and ob not in self.nearobstacles:
                self.nearobstacles.append(ob)
            if not ob.near and ob in self.nearobstacles:
                self.nearobstacles.remove(ob)

    def getfps(self, frametime, surface):

        self.ftlist.append(frametime)
        if len(self.ftlist) > 100:
            sum = 0
            for time in self.ftlist:
                sum += time
            self.fps = int(100 / sum)
            self.ftlist = []
        fpstext = self.font.render(str(self.fps), True, (255, 255, 0))
        surface.blit(fpstext, (765, 0))

    def openlevel(self, filename):

        obstaclelist = []
        with open(filename) as file:
            lvldata = file.read()
            lvl = json.loads(lvldata)

            for object in lvl:
                if object["type"] == "obstacle":
                    object = obstacle(object["pos"], object["width"], object["height"],
                                      object["color"], object["name"])
                    obstaclelist.append(object)

            return obstaclelist
