import pygame
import math
import random

class Enemy:
    COLOR = (225, 148, 255)  # Cor padrão roxa
    BASE_HEALTH = 100
    BASE_SPEED = 2
    SPAWN_CHANCE = 60  # Chance base de spawn (%)
    NAME = "Básico"  # Nome do inimigo padrão
    
    def __init__(self, path):
        self.radius = 12
        self.path_index = 0
        self.path = path
        self.x, self.y = path[0]
        self.base_speed = self.BASE_SPEED
        self.speed = self.base_speed
        self.max_health = self.BASE_HEALTH
        self.health = self.max_health
        self.slow_timer = 0
        self.is_slowed = False
        self.dot_timer = 0
        self.dot_tick_timer = 0
        self.dot_damage = 0
        self.is_burning = False
        
    @classmethod
    def should_spawn(cls):
        return random.randint(1, 100) <= cls.SPAWN_CHANCE
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
        
    def apply_slow(self, duration_frames=120):
        self.slow_timer = duration_frames
        self.speed = self.base_speed * 0.5
        self.is_slowed = True
        
    def apply_dot(self, damage, duration_frames=120):
        self.dot_timer = duration_frames
        self.dot_tick_timer = 30
        self.dot_damage = damage
        self.is_burning = True
        
    def update(self):
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.speed = self.base_speed
                self.is_slowed = False
                
        if self.dot_timer > 0:
            self.dot_timer -= 1
            if self.dot_timer <= 0:
                self.is_burning = False
            else:
                self.dot_tick_timer -= 1
                if self.dot_tick_timer <= 0:
                    if self.take_damage(self.dot_damage):
                        return True
                    self.dot_tick_timer = 30
        return False
        
    def move(self):
        if self.update():
            return True
        
        if self.path_index >= len(self.path) - 1:
            return True
            
        target_x, target_y = self.path[self.path_index + 1]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance < self.speed:
            self.path_index += 1
            if self.path_index < len(self.path) - 1:
                self.x, self.y = self.path[self.path_index]
        else:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed
            self.x += dx
            self.y += dy
            
        return False
        
    def draw(self, screen):
        # Desenha o inimigo com sua cor base
        pygame.draw.circle(screen, self.COLOR, (int(self.x), int(self.y)), self.radius)
        
        # Efeito de lentidão
        if self.is_slowed:
            slow_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(slow_surface, (43, 181, 255, 200), (self.radius, self.radius), self.radius)
            screen.blit(slow_surface, (int(self.x - self.radius), int(self.y - self.radius)))
            
        # Efeito de queimadura
        if self.is_burning:
            burn_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(burn_surface, (255, 140, 0, 200), (self.radius, self.radius), self.radius)
            screen.blit(burn_surface, (int(self.x - self.radius), int(self.y - self.radius)))
        
        # Barra de vida
        bar_width = 30
        bar_height = 5
        health_percentage = self.health / self.max_health
        
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.x - bar_width/2,
                         self.y - self.radius - 10,
                         bar_width,
                         bar_height))
        
        pygame.draw.rect(screen, (0, 255, 0),
                        (self.x - bar_width/2,
                         self.y - self.radius - 10,
                         bar_width * health_percentage,
                         bar_height))

class TankEnemy(Enemy):
    COLOR = (150, 75, 0)  # Marrom
    BASE_HEALTH = 200  # Dobro de vida
    BASE_SPEED = 1.2  # 40% mais lento
    SPAWN_CHANCE = 20  # 20% de chance de spawn
    NAME = "Tanque"  # Nome do inimigo tanque
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 15  # Maior tamanho
        
    def apply_slow(self, duration_frames=120):
        # Imune a slow
        pass

class SpeedEnemy(Enemy):
    COLOR = (50, 255, 50)  # Verde
    BASE_HEALTH = 60  # 40% menos vida
    BASE_SPEED = 3  # 50% mais rápido
    SPAWN_CHANCE = 30  # 30% de chance de spawn
    NAME = "Célere"  # Nome do inimigo veloz
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 8  # Menor tamanho
        
    def apply_dot(self, damage, duration_frames=120):
        # Imune a DoT
        pass

class ArmoredEnemy(Enemy):
    COLOR = (128, 128, 128)  # Cinza
    BASE_HEALTH = 150  # 50% mais vida
    BASE_SPEED = 1.5  # 25% mais lento
    SPAWN_CHANCE = 25  # 25% de chance de spawn
    NAME = "Defensor"  # Nome do inimigo blindado
    
    def __init__(self, path):
        super().__init__(path)
        self.damage_reduction = 0.3  # 30% de redução de dano
        
    def take_damage(self, damage):
        # Reduz o dano recebido
        reduced_damage = damage * (1 - self.damage_reduction)
        self.health -= reduced_damage
        return self.health <= 0

def spawn_random_enemy(path, wave_manager=None):
    """Função para gerar um inimigo aleatório baseado nas chances de spawn"""
    if not wave_manager:
        return Enemy(path), False
        
    # Pega as chances de spawn para a onda atual
    chances = wave_manager.get_spawn_chances()
    roll = random.uniform(0, 100)
    
    # Determina qual inimigo será spawnado baseado no roll
    if roll > chances['normal']:  # Se não for normal, será especial
        remaining = roll - chances['normal']
        if wave_manager.current_wave % 5 == 0:  # Ondas múltiplas de 5
            if remaining <= chances['tank']:
                enemy = TankEnemy(path)
            elif remaining <= chances['tank'] + chances['armored']:
                enemy = ArmoredEnemy(path)
            else:
                enemy = SpeedEnemy(path)
        elif wave_manager.current_wave % 2 == 0:  # Ondas pares
            if remaining <= chances['speed']:
                enemy = SpeedEnemy(path)
            elif remaining <= chances['speed'] + chances['tank']:
                enemy = TankEnemy(path)
            else:
                enemy = ArmoredEnemy(path)
        else:  # Ondas normais
            if remaining <= chances['tank']:
                enemy = TankEnemy(path)
            elif remaining <= chances['tank'] + chances['speed']:
                enemy = SpeedEnemy(path)
            else:
                enemy = ArmoredEnemy(path)
                
        # Aplica o aumento de vida
        health_increase = wave_manager.get_health_increase()
        enemy.max_health += health_increase
        enemy.health = enemy.max_health
        return enemy, True
    
    # Inimigo normal
    enemy = Enemy(path)
    health_increase = wave_manager.get_health_increase()
    enemy.max_health += health_increase
    enemy.health = enemy.max_health
    return enemy, False 