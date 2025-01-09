import pygame
import numpy as np
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Chiller Plant Sim")

# Fonts and colors
font = pygame.font.SysFont(None, 36)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# Chiller data (interpolated)
chiller_data = {
    "leaving_evap_temp": [20, 30, 40, 50],
    "entering_cond_temp": [85, 75, 65, 55],
    "cooling_rate_tons": [
        [118.6, 127.4, 135.7, 143.5],
        [146.0, 156.3, 166.0, 175.1],
        [183.9, 196.4, 208.3, 219.5],
        [227.4, 242.2, 257.6, 270.9],
    ],
    "power_draw_kw": [
        [111.9, 98.3, 87.3, 78.9],
        [114.2, 100.5, 89.2, 80.3],
        [117.9, 103.5, 90.9, 80.2],
        [122.9, 107.3, 92.8, 81.8],
    ],
}


def interpolate_capacity(leaving_temp_index, entering_temp):
    return np.interp(
        [entering_temp],
        chiller_data["entering_cond_temp"],
        chiller_data["cooling_rate_tons"][leaving_temp_index],
    )[0]


def interpolate_power(leaving_temp_index, entering_temp):
    return np.interp(
        [entering_temp],
        chiller_data["entering_cond_temp"],
        chiller_data["power_draw_kw"][leaving_temp_index],
    )[0]


class Zone:
    def __init__(self, room_temp, target_temp):
        self.room_temp = room_temp
        self.target_temp = target_temp
        self.heat_loss_rate = random.uniform(0.03, 0.06)
        self.cooling_rate = 0
        self.cooling_on = False

    def update(self, outside_temp, cooling_rate):
        # Heat gain from outside
        self.room_temp += self.heat_loss_rate * (outside_temp - self.room_temp)
        if self.cooling_on:
            self.room_temp -= cooling_rate


class ChillerPlantSim:
    def __init__(self, num_zones):
        self.zones = [Zone(random.uniform(60, 75), 70) for _ in range(num_zones)]
        self.outside_temp = random.uniform(85, 95)
        self.time = 0
        self.chiller_on = False
        self.score = 0

    def step(self, action):
        # Toggle chiller state based on action
        if action == 1:
            self.chiller_on = not self.chiller_on

        cooling_rate = 0
        power_draw = 0

        if self.chiller_on:
            cooling_rate = interpolate_capacity(2, self.outside_temp) / len(self.zones)
            power_draw = interpolate_power(2, self.outside_temp)

        for zone in self.zones:
            zone.cooling_on = self.chiller_on
            zone.update(self.outside_temp, cooling_rate)

        # Calculate score (reward)
        self.score += sum(
            max(0, 1 - abs(zone.room_temp - zone.target_temp) / 5)
            for zone in self.zones
        )
        self.score -= power_draw / 10  # Penalize high power usage
        self.time += 1

        # Check for game over
        game_over = any(
            zone.room_temp > 85 or zone.room_temp < 55 for zone in self.zones
        )
        return game_over

    def render(self):
        screen.fill(WHITE)
        for i, zone in enumerate(self.zones):
            x = 100 + i * 120
            y = SCREEN_HEIGHT // 2
            color = GREEN if 65 <= zone.room_temp <= 75 else RED
            pygame.draw.rect(screen, color, (x, y, 100, -zone.room_temp))
            temp_text = font.render(f"{zone.room_temp:.1f}F", True, BLUE)
            screen.blit(temp_text, (x, y - 20))

        score_text = font.render(f"Score: {int(self.score)}", True, ORANGE)
        screen.blit(score_text, (20, 20))
        pygame.display.flip()


# Main game loop
sim = ChillerPlantSim(num_zones=5)
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sim.step(1)  # Toggle chiller state

    game_over = sim.step(0)  # Keep running the simulation
    sim.render()

    if game_over:
        print("Game Over!")
        running = False

    clock.tick(30)

pygame.quit()
