import pygame as pg
import objects
import mapeditor
import time
pg.init()

# värit
black = (0, 0, 0)
white = (255, 255, 255)
grey = (119, 136, 153)
# peli-ikkunan aloitus
width = 800
height = 600
size = [width, height]
screen = pg.display.set_mode(size)

# kappaleet
editor = mapeditor.edit(width, height)
camera = objects.camera(size)
ball = objects.ball([width/2, height/2], [0, 0], 20, white)
obstacles = camera.openlevel("levels/level1.json")

# kello
clock = pg.time.Clock()
rate = 60
currenttime = time.time()
accumulator = 0
dt = 0.012

done = False
while not done:

    # clock.tick(rate)

    # fysiikan erotus fpssästä
    newtime = time.time()
    frametime = newtime - currenttime
    currenttime = newtime
    accumulator += frametime

    while accumulator > dt:

        # nappien painallus logiikka:
        for event in pg.event.get():

            done = camera.keyhandle(event, editor)
            if editor.editing:
                editor.keyhandle(event, camera.pos)
            if event.type == pg.QUIT:
                done = True

        if camera.goleft:
            ball.vel[0] -= 0.3
        if camera.goright:
            ball.vel[0] += 0.3
        if camera.godown:
            ball.vel[1] += 0.2

        # tarkistaa onko este ruudulla
        camera.checkobstacles(obstacles)
        # kappaleiden liikutus:
        ball.move(dt)
        camera.move(ball.pos)
        ball.update(camera.pos, camera.deltapos, size)
        for obstacle in obstacles:
            obstacle.update(camera.deltapos)
        ball.check(camera.nearobstacles)
        accumulator -= dt

    # peli-ikkunan piirto:
    screen.fill(grey)
    if editor.editing:
        editor.draw(screen, camera.deltapos)
    for obstacle in camera.nearobstacles:
        obstacle.draw(screen)
    ball.draw(screen)
    camera.getfps(frametime, screen)
    pg.display.flip()

pg.quit()
