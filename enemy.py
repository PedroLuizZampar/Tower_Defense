import pygame
import math
import random

class Enemy:
    COLOR = (225, 148, 255)  # Cor padrão roxa
    BASE_HEALTH = 80  # Reduzido para 80
    BASE_SPEED = 1.8  # Reduzido para 1.8
    SPAWN_CHANCE = 65  # Aumentado para 65%
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
        self.slow_timer = 0  # Timer para o efeito de slow
        self.is_slowed = False  # Flag para indicar se está sob efeito de slow
        self.weakness_timer = 0  # Timer para o efeito de fraqueza
        self.is_weakened = False  # Flag para indicar se está sob efeito de fraqueza
        
    @classmethod
    def should_spawn(cls):
        return random.randint(1, 100) <= cls.SPAWN_CHANCE
        
    def take_damage(self, damage):
        """Aplica dano ao inimigo e retorna True se ele morreu"""
        # Se estiver sob efeito de fraqueza, aumenta o dano em 30%
        if self.is_weakened:
            damage *= 1.3
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
        
    def apply_slow(self, duration_frames=180):  # 3 segundos de duração
        """Aplica efeito de lentidão"""
        if not self.is_slowed and not self.is_frozen:  # Só aplica se não estiver já sob efeito de slow ou freeze
            self.slow_timer = duration_frames
            self.speed = self.base_speed * 0.5  # Reduz a velocidade pela metade
            self.is_slowed = True
        
    def apply_weakness(self, duration_frames=240):  # 4 segundos = 240 frames
        """Aplica efeito de fraqueza"""
        self.weakness_timer = duration_frames
        self.is_weakened = True
        
    def update(self):
        """Atualiza os efeitos de status"""
        # Atualiza efeito de fraqueza
        if self.weakness_timer > 0:
            self.weakness_timer -= 1
            if self.weakness_timer <= 0:
                self.is_weakened = False
                
        # Atualiza efeito de congelamento
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.speed = self.base_speed if not self.is_slowed else self.base_speed * 0.5
                self.is_frozen = False
                
        # Atualiza efeito de slow
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.speed = self.base_speed
                self.is_slowed = False
                
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
        if self.is_slowed:
            pygame.draw.circle(screen, (0, 100, 0), (int(self.x), int(self.y)), 
                             self.radius + 4, 3)  # Círculo verde escuro para slow
        if self.is_weakened:
            # Cria uma superfície com transparência para o efeito de fraqueza
            weakness_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(weakness_surface, (0, 0, 0, 128), (self.radius, self.radius), self.radius)
            screen.blit(weakness_surface, (int(self.x - self.radius), int(self.y - self.radius)))

class TankEnemy(Enemy):
    COLOR = (150, 75, 0)  # Marrom
    BASE_HEALTH = 250  # Aumentado para 250
    BASE_SPEED = 1.0  # Reduzido para 1.0
    SPAWN_CHANCE = 15  # Reduzido para 15%
    NAME = "Tanque"  # Nome do inimigo tanque
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 16  # Aumentado para 16
        
    def apply_freeze(self, duration_frames=120):
        # Imune a freeze
        pass
        
    def apply_slow(self, duration_frames=180):
        # Imune a slow
        pass

class SpeedEnemy(Enemy):
    COLOR = (50, 255, 50)  # Verde
    BASE_HEALTH = 50  # Reduzido para 50
    BASE_SPEED = 3.2  # Aumentado para 3.2
    SPAWN_CHANCE = 25  # Reduzido para 25%
    NAME = "Célere"  # Nome do inimigo veloz
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 8  # Reduzido para 8
        
    def apply_dot(self, damage, duration_frames=120):
        # Imune a DoT
        pass

class ArmoredEnemy(Enemy):
    COLOR = (128, 128, 128)  # Cinza
    BASE_HEALTH = 180  # Aumentado para 180
    BASE_SPEED = 1.4  # Reduzido para 1.4
    SPAWN_CHANCE = 20  # Reduzido para 20%
    NAME = "Blindado"  # Nome do inimigo blindado
    
    def __init__(self, path):
        super().__init__(path)
        self.damage_reduction = 0.35  # Aumentado para 35%
        
    def take_damage(self, damage):
        # Reduz o dano recebido
        reduced_damage = damage * (1 - self.damage_reduction)
        self.health -= reduced_damage
        return self.health <= 0

class HealerEnemy(Enemy):
    COLOR = (144, 238, 144)  # Verde claro
    BASE_HEALTH = 120  # Reduzido para 120
    BASE_SPEED = 1.6  # Ajustado para 1.6
    SPAWN_CHANCE = 15  # Reduzido para 15%
    NAME = "Curador"  # Nome do inimigo curador
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 10
        self.heal_timer = 60  # Reduzido para 1 segundo
        self.heal_amount = 8  # Aumentado para 8
        self.heal_radius = 150  # Reduzido para 150
        
    def move(self):
        # Primeiro verifica se deve curar
        should_heal = False
        self.heal_timer -= 1
        if self.heal_timer <= 0:
            self.heal_timer = 90  # Reseta o timer
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

class FreezeAuraEnemy(Enemy):
    COLOR = (135, 206, 235)  # Azul claro
    BASE_HEALTH = 100  # Reduzido para 100
    BASE_SPEED = 2.0  # Aumentado para 2.0
    SPAWN_CHANCE = 15  # Reduzido para 15%
    NAME = "Gelado"
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 11
        self.freeze_radius = 100  # Reduzido para 100
        
    def take_damage(self, damage):
        """Aplica dano e retorna True se morreu, aplicando congelamento em todas as torres próximas"""
        self.health -= damage
        if self.health <= 0:
            return "freeze_aura"  # Retorna indicador especial para aplicar o efeito
        return False
        
    def get_defenders_in_range(self, defenders):
        """Retorna todos os defensores dentro do raio de congelamento"""
        in_range = []
        for defender in defenders:
            dx = defender.x - self.x
            dy = defender.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= self.freeze_radius:
                in_range.append(defender)
        return in_range
        
    def apply_freeze_aura(self, defenders):
        """Aplica o efeito de congelamento em todos os defensores no alcance"""
        affected_defenders = self.get_defenders_in_range(defenders)
        for defender in affected_defenders:
            defender.apply_freeze(90)  # 1.5 segundos de congelamento
        
    def draw(self, screen):
        super().draw(screen)
        # Desenha uma aura indicando o raio de efeito
        aura_surface = pygame.Surface((self.freeze_radius * 2, self.freeze_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (*self.COLOR, 30), (self.freeze_radius, self.freeze_radius), self.freeze_radius)
        screen.blit(aura_surface, (int(self.x - self.freeze_radius), int(self.y - self.freeze_radius)))

class RageEnemy(Enemy):
    COLOR = (139, 0, 0)  # Vermelho escuro
    BASE_HEALTH = 140  # Reduzido para 140
    BASE_SPEED = 1.6  # Ajustado para 1.6
    SPAWN_CHANCE = 20  # Reduzido para 20%
    NAME = "Furioso"
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 13
        self.original_speed = self.speed
        self.max_speed_multiplier = 2.5  # Reduzido para 2.5x
        
    def update(self):
        result = super().update()
        
        # Calcula a velocidade base considerando a raiva
        health_percent = self.health / self.max_health
        rage_multiplier = 1 + ((1 - health_percent) * (self.max_speed_multiplier - 1))
        
        # Aplica a velocidade considerando os efeitos de status
        if self.is_frozen:
            self.speed = 0
        elif self.is_slowed:
            self.speed = (self.original_speed * rage_multiplier) * 0.5
        else:
            self.speed = self.original_speed * rage_multiplier
            
        return result
        
    def draw(self, screen):
        super().draw(screen)
        # Efeito visual de rage (partículas vermelhas) quando estiver rápido
        if self.speed > self.original_speed * 1.5:
            for _ in range(3):
                offset_x = random.randint(-self.radius, self.radius)
                offset_y = random.randint(-self.radius, self.radius)
                pygame.draw.circle(screen, (255, 0, 0), 
                                 (int(self.x + offset_x), int(self.y + offset_y)), 2)

class StealthEnemy(Enemy):
    COLOR = (128, 0, 128)  # Roxo
    BASE_HEALTH = 40  # Reduzido para 40
    BASE_SPEED = 2.0  # Ajustado para 2.0
    SPAWN_CHANCE = 15  # Reduzido para 15%
    NAME = "Furtivo"
    
    def __init__(self, path):
        super().__init__(path)
        self.radius = 10
        self.stealth_timer = 0
        self.stealth_interval = 120  # Aumentado para 2 segundos
        self.stealth_duration = 60  # Ajustado para 1 segundo
        self.is_stealthed = False
        self.fade_start = 20  # Frames para começar a aparecer/desaparecer
        
    def update(self):
        result = super().update()
        
        # Atualiza o timer de stealth
        self.stealth_timer += 1
        if self.stealth_timer >= self.stealth_interval:
            self.is_stealthed = True
            if self.stealth_timer >= self.stealth_interval + self.stealth_duration:
                self.stealth_timer = 0
                self.is_stealthed = False
                
        return result
        
    def draw(self, screen):
        # Calcula a opacidade baseada no estado de stealth
        if self.is_stealthed:
            # Começando a ficar invisível
            if self.stealth_timer - self.stealth_interval < self.fade_start:
                opacity = 255 * (1 - (self.stealth_timer - self.stealth_interval) / self.fade_start)
            # Começando a reaparecer
            elif self.stealth_timer >= self.stealth_interval + self.stealth_duration - self.fade_start:
                opacity = 255 * ((self.stealth_timer - (self.stealth_interval + self.stealth_duration - self.fade_start)) / self.fade_start)
            # Totalmente invisível
            else:
                opacity = 0
        else:
            opacity = 255
            
        # Cria uma superfície com transparência
        enemy_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Desenha o círculo do inimigo com a opacidade calculada
        pygame.draw.circle(enemy_surface, (*self.COLOR, int(opacity)), 
                         (self.radius, self.radius), self.radius)
        screen.blit(enemy_surface, (int(self.x - self.radius), int(self.y - self.radius)))
        
        # Desenha a barra de vida apenas se não estiver totalmente invisível
        if opacity > 0:
            health_percentage = self.health / self.max_health
            bar_width = self.radius * 2
            bar_height = 4
            bar_x = self.x - self.radius
            bar_y = self.y - self.radius - 8
            
            # Fundo da barra (vermelho)
            bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(bar_surface, (255, 0, 0, int(opacity)),
                           (0, 0, bar_width, bar_height))
            screen.blit(bar_surface, (bar_x, bar_y))
            
            # Frente da barra (verde)
            pygame.draw.rect(bar_surface, (0, 255, 0, int(opacity)),
                           (0, 0, bar_width * health_percentage, bar_height))
            screen.blit(bar_surface, (bar_x, bar_y))
            
        # Desenha efeitos de status com a mesma opacidade
        if self.is_frozen and opacity > 0:
            pygame.draw.circle(screen, (*[50, 150, 255], int(opacity)), 
                             (int(self.x), int(self.y)), self.radius, 3)
        if self.is_burning and opacity > 0:
            pygame.draw.circle(screen, (*[255, 165, 0], int(opacity)), 
                             (int(self.x), int(self.y)), self.radius + 3, 3)
        if self.is_slowed and opacity > 0:
            pygame.draw.circle(screen, (*[0, 100, 0], int(opacity)), 
                             (int(self.x), int(self.y)), self.radius + 4, 3)
        if self.is_weakened and opacity > 0:
            weakness_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(weakness_surface, (0, 0, 0, int(opacity * 0.5)), 
                             (self.radius, self.radius), self.radius)
            screen.blit(weakness_surface, (int(self.x - self.radius), int(self.y - self.radius)))

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
            elif enemy_type == 'freeze_aura':
                return FreezeAuraEnemy(path), True
            elif enemy_type == 'rage':
                return RageEnemy(path), True
            elif enemy_type == 'stealth':
                return StealthEnemy(path), True
            break
            
    # Se algo der errado, retorna um inimigo normal
    return Enemy(path), False 