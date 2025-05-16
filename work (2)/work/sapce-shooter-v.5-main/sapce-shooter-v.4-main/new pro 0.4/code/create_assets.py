import pygame
import os

# Initialize Pygame
pygame.init()

# Create directories if they don't exist
os.makedirs('images', exist_ok=True)
os.makedirs('sounds', exist_ok=True)

# Create player ship (triangle)
player_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.polygon(player_surf, (0, 255, 0), [(20, 0), (0, 40), (40, 40)])
pygame.image.save(player_surf, 'images/player.png')

# Create laser (rectangle)
laser_surf = pygame.Surface((4, 20), pygame.SRCALPHA)
pygame.draw.rect(laser_surf, (255, 0, 0), (0, 0, 4, 20))
pygame.image.save(laser_surf, 'images/laser.png')

# Create meteor (circle)
meteor_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(meteor_surf, (150, 150, 150), (15, 15), 15)
pygame.image.save(meteor_surf, 'images/meteor.png')

# Create star (small circle)
star_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
pygame.draw.circle(star_surf, (255, 255, 255), (2, 2), 2)
pygame.image.save(star_surf, 'images/star.png')

# Create explosion frames
for i in range(8):
    size = 30 + i * 5
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 165, 0), (size//2, size//2), size//2)
    pygame.image.save(surf, f'images/explosion_{i}.png')

# Create empty sound files
with open('sounds/laser.wav', 'wb') as f:
    f.write(b'')
with open('sounds/explosion.wav', 'wb') as f:
    f.write(b'')

print("Assets created successfully!") 