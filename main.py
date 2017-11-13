# -*- coding: utf-8 -*-

import threading
import sqlite3
import random
import math
import imageio
from PIL import Image
from PIL import ImageDraw


UniverseG = 10000
UniverseX = 100
UniverseY = 100
UniversePopulation = 30
UniverseTimeshift = 50


def generatedb(X, Y, number):
    ScaleX = X
    ScaleY = Y
    con = sqlite3.connect('stat.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS particles (id INTEGER PRIMARY KEY, x REAL, y REAL, Vx REAL, Vy REAL, Fx REAL, Fy REAL, m REAL)')
    cur.execute('DELETE FROM particles')
    for number in range(number):
        sql = 'INSERT INTO particles VALUES (NULL, %f, %f, %f, %f, %f, %f, %f)' % (random.random() * ScaleX, random.random() * ScaleY, 0, 0, 0, 0, 1)
        print sql
        cur.execute(sql)
    con.commit()
    con.close()

def getlistfromdb():
    con = sqlite3.connect('stat.db')
    cur = con.cursor()
    sql = 'SELECT x, y, Vx, Vy, Fx, Fy, m FROM particles'
    cur.execute(sql)
    lines = []
    for row in cur:
        lines.append(row)
    con.close()
    return lines

def CalcForceX(particle1 , particle2 ):
    # F = G * m1 *m2 / r^2 (rr = dx^2 + dy^2)
    G = UniverseG
    m1 = particle1[6]
    x1 = particle1[0]
    y1 = particle1[1]
    m2 = particle2[6]
    x2 = particle2[0]
    y2 = particle2[1]
    rr = (math.pow(x2-x1, 2) + math.pow(y2-y1, 2))
    Force = G * m1 * m2 / rr
    a = math.atan((y2-y1)/(x2-x1))
    ForceX = Force * math.cos(a)
    if x1 > x2:
        ForceX *= -1
    return ForceX


def CalcForceY(particle1 , particle2 ):
    # F = G * m1 *m2 / r^2 (rr = dx^2 + dy^2)
    G = UniverseG
    m1 = particle1[6]
    x1 = particle1[0]
    y1 = particle1[1]
    m2 = particle2[6]
    x2 = particle2[0]
    y2 = particle2[1]
    rr = (math.pow(x2-x1, 2) + math.pow(y2-y1, 2))
    Force = G * m1 * m2 / rr
    a = math.atan((y2-y1)/(x2-x1))

    ForceY = Force * math.sin(a)
    if y1 > x2:
        ForceY *= -1

    return ForceY

def CalcVelocityX(particle, timeshift=1):
    # Vx = v0х + ax * t
    v0x = particle[2]
    ax = particle[4]/particle[6]
    t = timeshift
    VeloX = v0x + ax * t
    return VeloX

def CalcVelocityY(particle, timeshift=1):
    # Vy = v0y + ay * t
    v0y = particle[3]
    ay = particle[5]/particle[6]
    t = timeshift
    VeloY = v0y + ay * t
    return VeloY

def CalcX(particle, timeshift=1):
    # dx = dt * vx
    dt = timeshift
    Vx = particle[2]
    X = particle[0]+Vx*dt
    return X

def CalcY(particle, timeshift=1):
    # dx = dt * vx
    dt = timeshift
    Vy = particle[3]
    Y = particle[1]+Vy*dt
    return Y

def iterateForce(particles):
    newparticles = []
    for particle in particles:
        Fx = 0
        Fy = 0
        for addictive in particles:
            if particle is not addictive:
                #print "Ч 1: ", particle, " Ч 2: ", addictive
                Fx += CalcForceX(particle, addictive)
                Fy += CalcForceY(particle, addictive)
        #print particle
        tmpparticle = [particle[0], particle[1], particle[2], particle[3], Fx, Fy, particle[6]]
        #print tmpparticle
        newparticles.append(tmpparticle)
    return newparticles

def iterateVelocity(particles):
    newparticles = []
    for particle in particles:
        Vx = 0
        Vy = 0
        for addictive in particles:
            if particle is not addictive:
                Vx += CalcVelocityX(particle, UniverseTimeshift)
                Vy += CalcVelocityY(particle, UniverseTimeshift)
        tmpparticle = [particle[0], particle[1], Vx, Vy, particle[4], particle[5], particle[6]]

        newparticles.append(tmpparticle)
    return newparticles

def iterateMovement(particles):
    newparticles = []
    for particle in particles:
        X = CalcX(particle, UniverseTimeshift)
        Y = CalcY(particle, UniverseTimeshift)
        tmpparticle = [X, Y, particle[2], particle[3], particle[4], particle[5], particle[6]]
        newparticles.append(tmpparticle)
    return newparticles

if __name__ == '__main__':
    #generatedb(UniverseX, UniverseY, UniversePopulation)
    images = []
    print getlistfromdb()
    for count in range(1):
        world = iterateForce(getlistfromdb())
        world = iterateVelocity(world)
        world = iterateMovement(world)
        print world

        img = Image.new('RGB', (UniverseX, UniverseY), (50,50,50))
        imgDrawer = ImageDraw.Draw(img)
        for particle in world:
            imgDrawer.point((particle[0],particle[1]))
        imgDrawer.text((10, 20), "Pic %s" % count)
        img.save("export\%sworld.png" % count)
        images.append(imageio.imread("export\%sworld.png" % count))
        img.close()
    imageio.mimsave('movie.gif', images)

