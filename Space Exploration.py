import pygame
import math
import random
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
width, height = 1200, 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Advanced Space Exploration")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Load images and sounds
background_img = pygame.image.load("space_background.png").convert()
ship_img = pygame.image.load("spaceship.png").convert_alpha()
ship_img = pygame.transform.scale(ship_img, (40, 40))
asteroid_img = pygame.image.load("asteroid.png").convert_alpha()
asteroid_img = pygame.transform.scale(asteroid_img, (30, 30))
powerup_img = pygame.image.load("powerup.png").convert_alpha()
powerup_img = pygame.transform.scale(powerup_img, (20, 20))
collect_sound = pygame.mixer.Sound("collect.wav")
crash_sound = pygame.mixer.Sound("crash.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")
pygame.mixer.music.load("space_theme.mp3")
pygame.mixer.music.play(-1)

# Planet class
class Planet:
    def __init__(self, x, y, radius, color, name, resource_type):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.name = name
        self.resource_type = resource_type
        self.resources = random.randint(50, 200)
        self.angle = 0
        self.orbit_speed = random.uniform(0.001, 0.005)
        self.orbit_radius = random.randint(100, 300)
        self.center_x = x
        self.center_y = y

    def update(self):
        self.angle += self.orbit_speed
        self.x = self.center_x + math.cos(self.angle) * self.orbit_radius
        self.y = self.center_y + math.sin(self.angle) * self.orbit_radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.name}: {self.resources}", True, WHITE)
        screen.blit(text, (self.x - text.get_width() // 2, self.y + self.radius + 5))

# Spaceship class
class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.fuel = 1000
        self.resources = {"Metal": 0, "Water": 0, "Food": 0}
        self.angle = 0
        self.shield = 100
        self.powerup_timer = 0

    def move(self, dx, dy):
        if self.fuel > 0:
            speed_multiplier = 2 if self.powerup_timer > 0 else 1
            self.x += dx * self.speed * speed_multiplier
            self.y += dy * self.speed * speed_multiplier
            self.fuel -= 1
            self.angle = math.atan2(dy, dx)

    def draw(self, screen):
        rotated_ship = pygame.transform.rotate(ship_img, -math.degrees(self.angle) - 90)
        screen.blit(rotated_ship, (self.x - rotated_ship.get_width() // 2, self.y - rotated_ship.get_height() // 2))

        # Draw shield bar
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - 30, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 30, self.shield * 0.4, 5))

        # Draw powerup indicator
        if self.powerup_timer > 0:
            pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y - 40)), 5)

    def update(self):
        if self.powerup_timer > 0:
            self.powerup_timer -= 1

# Star class for background
class Star:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(0.1, 0.5)
        self.size = random.randint(1, 3)

    def move(self):
        self.y += self.speed
        if self.y > height:
            self.y = 0
            self.x = random.randint(0, width)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

# Asteroid class
class Asteroid:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = -50
        self.speed = random.uniform(1, 3)
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)

    def move(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        if self.y > height + 50:
            self.y = -50
            self.x = random.randint(0, width)

    def draw(self, screen):
        rotated_asteroid = pygame.transform.rotate(asteroid_img, self.rotation)
        screen.blit(rotated_asteroid, (self.x - rotated_asteroid.get_width() // 2, self.y - rotated_asteroid.get_height() // 2))

# Power-up class
class PowerUp:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = -50
        self.speed = random.uniform(1, 2)
        self.type = random.choice(["speed", "shield"])

    def move(self):
        self.y += self.speed
        if self.y > height + 50:
            self.y = -50
            self.x = random.randint(0, width)

    def draw(self, screen):
        screen.blit(powerup_img, (self.x - 10, self.y - 10))

# Game state
class GameState:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.high_score = self.load_high_score()
        self.mission_objective = self.generate_mission()
        self.game_over = False

    def generate_mission(self):
        resource = random.choice(["Metal", "Water", "Food"])
        amount = random.randint(10, 50)
        return f"Collect {amount} {resource}"

    def load_high_score(self):
        try:
            with open("high_score.json", "r") as f:
                return json.load(f)["high_score"]
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        with open("high_score.json", "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def check_mission_complete(self, ship):






        parts = self.mission_objective.split()
        if len(parts) >= 3:
            amount, resource = parts[1], parts[2]
            if resource in ship.resources and ship.resources[resource] >= int(amount):
                self.score += 1000
                self.mission_objective = self.generate_mission()
                return True
        return False
    def next_level(self):
        self.level += 1
        self.mission_objective = self.generate_mission()

# Trading system
class TradingSystem:
    def __init__(self):
        self.prices = {"Metal": 10, "Water": 15, "Food": 20}

    def trade(self, ship, resource_type, amount):
        if ship.resources[resource_type] >= amount:
            ship.resources[resource_type] -= amount
            credits = amount * self.prices[resource_type]
            ship.fuel += credits
            return credits
        return 0

# Create game objects
game_state = GameState()
planets = [
    Planet(600, 450, 50, YELLOW, "Sun", "Metal"),
    Planet(200, 200, 15, GRAY, "Mercury", "Metal"),
    Planet(1000, 700, 25, BLUE, "Earth", "Water"),
    Planet(400, 600, 20, RED, "Mars", "Food")
]

ship = Spaceship(width // 2, height // 2)
stars = [Star() for _ in range(100)]
asteroids = [Asteroid() for _ in range(5)]
powerups = [PowerUp() for _ in range(2)]
trading_system = TradingSystem()

# Main game loop
running = True
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state.game_over and event.key == pygame.K_SPACE:
                # Reset game
                ship = Spaceship(width // 2, height // 2)
                game_state = GameState()
            elif event.key == pygame.K_t:
                # Trading
                for resource in ship.resources:
                    credits = trading_system.trade(ship, resource, ship.resources[resource])
                    game_state.score += credits

    if not game_state.game_over:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        if dx != 0 or dy != 0:
            ship.move(dx, dy)

        # Update game objects
        ship.update()
        for planet in planets:
            planet.update()
        for asteroid in asteroids:
            asteroid.move()
        for powerup in powerups:
            powerup.move()

        # Check collisions
        for planet in planets:
            distance = math.hypot(ship.x - planet.x, ship.y - planet.y)
            if distance < planet.radius + 20:
                if planet.resources > 0:
                    ship.resources[planet.resource_type] += 1
                    planet.resources -= 1
                    game_state.score += 10
                    collect_sound.play()

        for asteroid in asteroids:
            distance = math.hypot(ship.x - asteroid.x, ship.y - asteroid.y)
            if distance < 30:
                ship.shield -= 10
                crash_sound.play()
                if ship.shield <= 0:
                    game_state.game_over = True

        for powerup in powerups:
            distance = math.hypot(ship.x - powerup.x, ship.y - powerup.y)
            if distance < 30:
                if powerup.type == "speed":
                    ship.powerup_timer = 300  # 5 seconds
                elif powerup.type == "shield":
                    ship.shield = min(ship.shield + 50, 100)
                powerup_sound.play()
                powerup.y = -50
                powerup.x = random.randint(0, width)

        # Check mission completion
        if game_state.check_mission_complete(ship):
            game_state.next_level()

        # Increase difficulty
        if game_state.score > game_state.level * 1000:
            game_state.next_level()
            asteroids.append(Asteroid())

    # Draw everything
    screen.blit(background_img, (0, 0))
    for star in stars:
        star.move()
        star.draw(screen)

    for planet in planets:
        planet.draw(screen)

    for asteroid in asteroids:
        asteroid.draw(screen)

    for powerup in powerups:
        powerup.draw(screen)

    if not game_state.game_over:
        ship.draw(screen)

    # Display info
    fuel_text = font.render(f"Fuel: {ship.fuel}", True, WHITE)
    metal_text = font.render(f"Metal: {ship.resources['Metal']}", True, WHITE)
    water_text = font.render(f"Water: {ship.resources['Water']}", True, WHITE)
    food_text = font.render(f"Food: {ship.resources['Food']}", True, WHITE)
    score_text = font.render(f"Score: {game_state.score}", True, WHITE)
    level_text = font.render(f"Level: {game_state.level}", True, WHITE)
    mission_text = font.render(f"Mission: {game_state.mission_objective}", True, WHITE)
    high_score_text = font.render(f"High Score: {game_state.high_score}", True, WHITE)
    
    screen.blit(fuel_text, (10, 10))
    screen.blit(metal_text, (10, 50))
    screen.blit(water_text, (10, 90))
    screen.blit(food_text, (10, 130))
    screen.blit(score_text, (width - 150, 10))
    screen.blit(level_text, (width - 150, 50))
    screen.blit(mission_text, (width // 2 - mission_text.get_width() // 2, 10))
    screen.blit(high_score_text, (width - 250, 90))

    if game_state.game_over:
        game_over_text = font.render("Game Over! Press SPACE to restart", True, WHITE)
        screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2))
        if game_state.score > game_state.high_score:
            game_state.high_score = game_state.score
            game_state.save_high_score()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()