import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# Initialize Pygame and OpenGL
def init():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, 0.0, -5)

# Create a simple 3D triangle (pyramid shape)
def draw_triangle():
    glBegin(GL_TRIANGLES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 1, 0)  # Top vertex
    glColor3f(0, 1, 0)
    glVertex3f(-1, -1, 1)  # Bottom left
    glColor3f(0, 0, 1)
    glVertex3f(1, -1, 1)  # Bottom right
    glColor3f(1, 1, 0)
    glVertex3f(0, 1, 0)  # Top vertex again
    glColor3f(1, 0, 1)
    glVertex3f(1, -1, 1)  # Bottom right again
    glColor3f(0, 1, 1)
    glVertex3f(1, -1, -1)  # Back vertex
    glEnd()

# Draw the reflections for kaleidoscopic effect
def kaleidoscope_reflections():
    num_reflections = 8
    for i in range(num_reflections):
        glPushMatrix()
        glRotatef(i * (360 / num_reflections), 0, 1, 0)  # Rotate around Y axis
        draw_triangle()
        glPopMatrix()

def random_colors():
    return random.random(), random.random(), random.random()

# Main loop for rendering the kaleidoscope
def main():
    init()
    angle = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Apply rotation for dynamic kaleidoscope
        glPushMatrix()
        glRotatef(angle, 1, 1, 0)  # Rotate along X and Y axis
        kaleidoscope_reflections()  # Draw the reflections
        glPopMatrix()

        # Update rotation angle for animation
        angle += 0.5
        if angle > 360:
            angle = 0

        # Double buffering for smoother rendering
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
