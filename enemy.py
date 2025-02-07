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
        self.freeze_timer = 0
        self.is_frozen = False
        self.dot_timer = 0
        self.dot_tick_timer = 0
        self.dot_damage = 0
        self.is_burning = False
        self.reward_given = False  # Nova flag para controlar se já deu recompensa
        
    @classmethod
    def should_spawn(cls):
        return random.randint(1, 100) <= cls.SPAWN_CHANCE
        
    def take_damage(self, damage):
        """Aplica dano ao inimigo e retorna True se ele morreu"""
        self.health -= damage
        return self.health <= 0
        
    def apply_freeze(self, duration_frames=30):
        """Aplica efeito de congelamento"""
        if not self.is_frozen:  # Só aplica se não estiver já sob efeito
            self.freeze_timer = duration_frames
            self.speed = 0  # Paralisa completamente
            self.is_frozen = True
        
    def apply_dot(self, damage, duration_frames=120):
        """Aplica dano ao longo do tempo"""
        # Atualiza o DoT apenas se o novo dano for maior ou se não houver DoT ativo
        if not self.is_burning or damage > self.dot_damage:
            self.dot_timer = duration_frames
            self.dot_tick_timer = 30  # Tick a cada 0.5 segundos
            self.dot_damage = damage
            self.is_burning = True
        
    def update(self):
        """Atualiza os efeitos de status"""
        # Atualiza efeito de congelamento
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.speed = self.base_speed
                self.is_frozen = False
                
        # Atualiza dano ao longo do tempo
        if self.dot_timer > 0:
            self.dot_timer -= 1
            if self.dot_timer <= 0:
                self.is_burning = False
                self.dot_damage = 0
            else:
                self.dot_tick_timer -= 1
                if self.dot_tick_timer <= 0:
                    if self.take_damage(self.dot_damage):
                        return "died"  # Retorna indicador de morte por DoT
                    self.dot_tick_timer = 30  # Reseta o timer do tick
        return False
        
    def move(self):
        update_result = self.update()
        if update_result == "died":  # Se morreu por DoT
            return "died"  # Propaga o indicador de morte por DoT
        
        if self.path_index >= len(self.path) - 1:
            return True  # Chegou ao final do caminho
            
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
        # Desenha o círculo do inimigo
        pygame.draw.circle(screen, self.COLOR, (int(self.x), int(self.y)), self.radius)
        
        # Desenha a barra de vida
        health_percentage = self.health / self.max_health
        bar_width = self.radius * 2
        bar_height = 4
        bar_x = self.x - self.radius
        bar_y = self.y - self.radius - 8
        
        # Fundo da barra (vermelho)
        pygame.draw.rect(screen, (255, 0, 0),
                        (bar_x, bar_y, bar_width, bar_height))
        # Frente da barra (verde)
        pygame.draw.rect(screen, (0, 255, 0),
                        (bar_x, bar_y, bar_width * health_percentage, bar_height))
        
        # Desenha efeitos de status
        if self.is_frozen:
            pygame.draw.circle(screen, (50, 150, 255), (int(self.x), int(self.y)), 
                             self.radius, 3)  # Círculo azul para congelamento
        if self.is_burning:
            pygame.draw.circle(screen, (255, 165, 0), (int(self.x), int(self.y)), 
                             self.radius + 3, 3)  # Círculo laranja para DoT

class TankEnemy(Enemy):
    COLOR = (150, 75, 0)  # Marrom
    BASE_HEALTH = 200  # Dobro de vida
    BASE_SPEED = 1.2  # 40% mais lento
    SPAWN_CHANCE = 20  # 20% de chance de spawn
    NAME = "Tanque"  # Nome do inimigo tanque
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 15  # Maior tamanho
        
    def apply_freeze(self, duration_frames=120):
        # Imune a freeze
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
    NAME = "Blindado"  # Nome do inimigo blindado
    
    def __init__(self, path):
        super().__init__(path)
        self.damage_reduction = 0.3  # 30% de redução de dano
        
    def take_damage(self, damage):
        # Reduz o dano recebido
        reduced_damage = damage * (1 - self.damage_reduction)
        self.health -= reduced_damage
        return self.health <= 0

class HealerEnemy(Enemy):
    COLOR = (144, 238, 144)  # Verde claro
    BASE_HEALTH = 180  # 80% mais vida
    BASE_SPEED = 1.4  # 60% mais lento
    SPAWN_CHANCE = 20  # 20% de chance de spawn
    NAME = "Curador"  # Nome do inimigo curador
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 10  # Tamanho menor
        self.heal_timer = 120  # 2 segundos (120 frames)
        self.heal_amount = 5  # Quantidade de cura
        self.heal_radius = 150  # Raio de cura
        
    def move(self):
        # Primeiro verifica se deve curar
        should_heal = False
        self.heal_timer -= 1
        if self.heal_timer <= 0:
            self.heal_timer = 120  # Reseta o timer
            should_heal = True
            
        # Depois move normalmente
        move_result = super().move()
        
        # Se chegou ao final do caminho ou morreu, retorna isso
        if move_result is True or move_result == "died":
            return move_result
            
        # Se deve curar, retorna "heal"
        if should_heal:
            return "heal"
            
        # Caso contrário, retorna False (continua movendo)
        return False
        
    def draw(self, screen):
        super().draw(screen)
        # Desenha o raio de cura como um círculo semi-transparente
        heal_surface = pygame.Surface((self.heal_radius * 2, self.heal_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(heal_surface, (*self.COLOR, 50), (self.heal_radius, self.heal_radius), self.heal_radius)
        screen.blit(heal_surface, (int(self.x - self.heal_radius), int(self.y - self.heal_radius)))

def spawn_random_enemy(path, wave_manager):
    """Spawna um inimigo aleatório baseado nas chances da onda atual"""
    chances = wave_manager.get_spawn_chances()
    roll = random.random() * 100  # Número entre 0 e 100
    
    cumulative = 0
    for enemy_type, chance in chances.items():
        cumulative += chance
        if roll <= cumulative:
            if enemy_type == 'normal':
                return Enemy(path), False
            elif enemy_type == 'tank':
                return TankEnemy(path), True
            elif enemy_type == 'speed':
                return SpeedEnemy(path), True
            elif enemy_type == 'armored':
                return ArmoredEnemy(path), True
            elif enemy_type == 'healer':
                return HealerEnemy(path), True
            break
            
    # Se algo der errado, retorna um inimigo normal
    return Enemy(path), False 