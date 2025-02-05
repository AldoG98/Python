import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time

def draw_field():
    glBegin(GL_QUADS)
    glColor3fv((0.1, 0.6, 0.1))  # Darker green for the field
    glVertex3fv((-3, -2, 0))
    glVertex3fv((3, -2, 0))
    glVertex3fv((3, 2, 0))
    glVertex3fv((-3, 2, 0))
    glEnd()

    # Draw field lines
    glColor3fv((1, 1, 1))  # White lines
    glBegin(GL_LINES)
    glVertex3fv((-3, 0, 0.01))
    glVertex3fv((3, 0, 0.01))
    glVertex3fv((0, -2, 0.01))
    glVertex3fv((0, 2, 0.01))
    glEnd()

def draw_seating_section(color):
    glBegin(GL_QUADS)
    glColor3fv(color)
    glVertex3fv((-1, -0.5, 0))
    glVertex3fv((1, -0.5, 0))
    glVertex3fv((1, 0.5, 0))
    glVertex3fv((-1, 0.5, 0))
    glEnd()

def draw_roof():
    glBegin(GL_TRIANGLES)
    glColor3fv((0.7, 0.7, 0.7))  # Light gray for the roof
    glVertex3fv((-4, 3, 1))
    glVertex3fv((0, 5, 1))
    glVertex3fv((4, 3, 1))
    glEnd()

def render_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()

    glTranslatef(0, 0, -10)  # Move the scene back
    glRotatef(15, 1, 0, 0)  # Tilt the view

    draw_field()
    
    # Draw seating sections
    colors = [
        (1, 0, 0),    # Red
        (0, 0, 1),    # Blue
        (1, 1, 0),    # Yellow
        (1, 0.5, 0),  # Orange
    ]
    
    for i, color in enumerate(colors):
        glPushMatrix()
        glTranslatef(0, i * 1.2 + 2, i * 0.5)
        glScalef(3, 1, 1)
        draw_seating_section(color)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -(i * 1.2 + 2), i * 0.5)
        glScalef(3, 1, 1)
        draw_seating_section(color)
        glPopMatrix()
        
        pygame.display.flip()
        time.sleep(0.5)  # Slower render effect

    draw_roof()
    
    glPopMatrix()
    pygame.display.flip()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        render_scene()

main()
