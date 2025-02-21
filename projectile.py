import pygame
import math
from base import GameSpeed  # Adicione no topo do arquivo

class Projectile:
    def __init__(self, x, y, target_enemy, color=(255, 255, 0)):  # Cor padrão amarela
        self.x = x
        self.y = y
        self.radius = 5
        self.base_speed = 7
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
            
        # Move em direção ao alvo usando a velocidade ajustada
        current_speed = self.base_speed * GameSpeed.get_instance().current_multiplier
        dx = dx / distance * current_speed
        dy = dy / distance * current_speed
        self.x += dx
        self.y += dy
        return False
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius) 