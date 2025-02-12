import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Solar System Simulation")

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (169, 169, 169)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BROWN = (165, 42, 42)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)

# Planet class
class Planet:
    def __init__(self, x, y, radius, color, orbit_radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.orbit_radius = orbit_radius
        self.speed = speed
        self.angle = 0

    def update(self):
        self.angle += self.speed
        self.x = width // 2 + int(math.cos(self.angle) * self.orbit_radius)
        self.y = height // 2 + int(math.sin(self.angle) * self.orbit_radius)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

# Create planets
sun = Planet(width // 2, height // 2, 30, YELLOW, 0, 0)
mercury = Planet(0, 0, 4, GRAY, 60, 0.02)
venus = Planet(0, 0, 8, ORANGE, 100, 0.015)
earth = Planet(0, 0, 9, BLUE, 150, 0.01)
mars = Planet(0, 0, 5, RED, 210, 0.008)
jupiter = Planet(0, 0, 20, BROWN, 300, 0.004)
saturn = Planet(0, 0, 17, LIGHT_BLUE, 380, 0.003)
uranus = Planet(0, 0, 12, BLUE, 450, 0.002)
neptune = Planet(0, 0, 11, DARK_BLUE, 520, 0.001)

planets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # Draw orbit paths
    for planet in planets:
        pygame.draw.circle(screen, (50, 50, 50), (width // 2, height // 2), planet.orbit_radius, 1)

    # Update and draw planets
    sun.draw(screen)
    
    for planet in planets:
        planet.update()
        planet.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
