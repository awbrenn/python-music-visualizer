from recorder import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import os, sys, signal
import Image
import math
import ImageFilter
import numpy


ORIGINAL_IMAGE = None
WARPED_IMAGE = None
IMAGE_WIDTH = None
IMAGE_HEIGHT = None
PI = 3.1415926535897
original_pixels = None
warped_pixels = None
SR = None
frequency_sum_scaling_factor = 20400
strength = 0.0

def handleError(error_message):
    print error_message
    print '\nkilling process...'
    os.kill(os.getpid(), signal.SIGKILL)


def handleKey(key, x, y):
    global ORIGINAL_IMAGE
    global WARPED_IMAGE
    global original_pixels
    global warped_pixels

    if key == 'q' or key == 'Q':
        print 'Quit Program'
        print '\nkilling process'
        os.kill(os.getpid(), signal.SIGKILL)


def drawImage():
    global WARPED_IMAGE

    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDrawPixels(IMAGE_WIDTH, IMAGE_HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, numpy.fromstring(WARPED_IMAGE.tostring(), numpy.uint8))

    glFlush()


def animateWarp():
    getStrengthFromAudio()
    warpTheImage()
    glutPostRedisplay()


def openGlInit():
    global IMAGE_WIDTH
    global IMAGE_HEIGHT
    global m_texname

    glutInit()

    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowSize(IMAGE_WIDTH, IMAGE_HEIGHT)
    glutCreateWindow('Warp Result')

    glutIdleFunc(animateWarp)
    glutDisplayFunc(drawImage)
    glutKeyboardFunc(handleKey)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, IMAGE_WIDTH, 0, IMAGE_HEIGHT)

    glClearColor(1, 1, 1, 0)
    glutMainLoop()


def warpTheImage():
    global ORIGINAL_IMAGE
    global WARPED_IMAGE
    global original_pixels
    global warped_pixels
    global strength

    size = ((IMAGE_HEIGHT / 6) + (IMAGE_WIDTH / 6)) / 2

    x_center = IMAGE_WIDTH / 2
    y_center = IMAGE_HEIGHT / 2

    for col in range(IMAGE_WIDTH):    # for every pixel:
        for row in range(IMAGE_HEIGHT):
            x = col - x_center
            y = row - y_center

            angle = strength * math.exp(-1.0 * (float(x) * float(x) + float(y) * float(y)) / (size * size))
            u = math.cos(angle) * float(x) + math.sin(angle) * float(y) + x_center
            v = -1.0 * math.sin(angle) * float(x) + math.cos(angle) * float(y) + y_center

            u = int(u)
            v = int(v)

            if v > (IMAGE_HEIGHT - 1) or u > (IMAGE_WIDTH - 1) or v < 0 or u < 0:
                warped_pixels[col, row] = (0, 0, 0, 0)
            else:
                warped_pixels[col, row] = original_pixels[u, v]
    return WARPED_IMAGE


def getStrengthFromAudio():
    global SR
    global frequency_sum_scaling_factor
    global strength

    if SR.newAudio==False:
        strength = 0.0
        return
    xs, ys = SR.fft()
    strength = sum(ys) / frequency_sum_scaling_factor
    SR.newAudio = False


def swhInit():
    global SR

    SR = SwhRecorder()
    SR.setup()
    SR.continuousStart()


def main():
    global ORIGINAL_IMAGE
    global WARPED_IMAGE
    global IMAGE_WIDTH
    global IMAGE_HEIGHT
    global original_pixels
    global warped_pixels
    global SR

    swhInit()

    if len(sys.argv) != 2:
        handleError('Error: bad input\nUse Case: $> python imageMusicVisualizer.py input.img')

    ORIGINAL_IMAGE = Image.open(sys.argv[1]).transpose(Image.FLIP_TOP_BOTTOM)

    if ORIGINAL_IMAGE.mode == 'RGB':
        ORIGINAL_IMAGE = ORIGINAL_IMAGE.convert('RGBA')
    elif ORIGINAL_IMAGE.mode != 'RGBA':
        handleError('The image type is not RGB or RGBA')

    IMAGE_WIDTH = ORIGINAL_IMAGE.size[0]
    IMAGE_HEIGHT = ORIGINAL_IMAGE.size[1]

    WARPED_IMAGE = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), "black")

    original_pixels = ORIGINAL_IMAGE.load()
    warped_pixels = WARPED_IMAGE.load()

    WARPED_IMAGE = warpTheImage()
    openGlInit()


main()