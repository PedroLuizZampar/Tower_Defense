import pygame
import math

class Projectile:
    def __init__(self, x, y, target_enemy, color=(255, 255, 0)):  # Cor padrão amarela
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 7
        self.damage = 20
        self.target = target_enemy
        self.color = color
        
    def move(self):
        if self.target is None or not hasattr(self.target, 'x'):
            return True
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        # Se atingiu o alvo
        if distance < self.radius + self.target.radius:
            return True
            
        # Move em direção ao alvo
        dx = dx / distance * self.speed
        dy = dy / distance * self.speed
        self.x += dx
        self.y += dy
        return False
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius) 