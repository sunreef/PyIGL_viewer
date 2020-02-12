import numpy as np
import math

def magnitude(v):
    return math.sqrt(np.sum(v ** 2))

def normalize(v):
    m = magnitude(v)
    if m == 0:
        return v
    return v / m

def ortho(l, r, b, t, n, f):
    dx = r - l
    dy = t - b
    dz = f - n
    rx = -(r + l) / (r - l)
    ry = -(t + b) / (t - b)
    rz = -(f + n) / (f - n)
    return np.matrix([[2.0/dx,0,0,rx],
                      [0,2.0/dy,0,ry],
                      [0,0,-2.0/dz,rz],
                      [0,0,0,1]])


def perspective(fovy, aspect, n, f):
    s = 1.0/math.tan(math.radians(fovy)/2.0)
    sx, sy = s / aspect, s
    zz = -(f+n)/(f-n)
    zw = -2*f*n/(f-n)
    return np.matrix(
            [[sx,0,0,0],
                [0,sy,0,0],
                [0,0,zz,zw],
                [0,0,-1.0,0]], dtype='f')


def translate(xyz):
    x, y, z = xyz
    return np.matrix([[1,0,0,x],
                      [0,1,0,y],
                      [0,0,1,z],
                      [0,0,0,1]])

def scale(xyz):
    x, y, z = xyz
    return np.matrix([[x,0,0,0],
                      [0,y,0,0],
                      [0,0,z,0],
                      [0,0,0,1]])

def sincos(a):
    a = math.radians(a)
    return math.sin(a), math.cos(a)

def rotate(a, xyz):
    x, y, z = normalize(xyz)
    s, c = sincos(a)
    nc = 1 - c
    return np.matrix([[x*x*nc +   c, x*y*nc - z*s, x*z*nc + y*s],
                      [y*x*nc + z*s, y*y*nc +   c, y*z*nc - x*s],
                      [x*z*nc - y*s, y*z*nc + x*s, z*z*nc +   c]])

def rotx(a):
    s, c = sincos(a)
    return np.matrix([[1,0,0],
                      [0,c,-s],
                      [0,s,c]])

def roty(a):
    s, c = sincos(a)
    return np.matrix([[c,0,s],
                      [0,1,0],
                      [-s,0,c]]
                      )

def rotz(a):
    s, c = sincos(a)
    return np.matrix([[c,-s,0,0],
                      [s,c,0,0],
                      [0,0,1,0],
                      [0,0,0,1]])

def lookat(eye, target, up):
    F = target[:3] - eye[:3]
    f = normalize(F)
    U = normalize(up[:3])
    s = np.cross(f, U)
    u = np.cross(s, f)
    M = np.matrix(np.identity(4))
    M[:3,:3] = np.vstack([s,u,-f])
    T = translate(-eye)
    return M * T
