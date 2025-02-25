import pygame
import math
from math import ceil
import random
from base import GameSpeed  # Adicione no topo do arquivo]
from wave_manager import WaveManager

class Enemy:
    COLOR = (225, 148, 255)  # Cor padrão roxa
    BASE_HEALTH = 80  # Reduzido para 80
    BASE_SPEED = 1.8  # Reduzido para 1.8
    SPAWN_CHANCE = 65  # Aumentado para 65%
    NAME = "Básico"  # Nome do inimigo padrão
    REWARD = 2  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        self.radius = 12
        self.path_index = 0
        self.path = path
        self.x, self.y = path[0]
        self.base_speed = self.BASE_SPEED
        self.speed = self.base_speed
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
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
        self.immunity_timer = 0  # Timer para o efeito de imunidade
        self.is_immunized = False  # Flag para indicar se está sob efeito de imunidade
        self.speed_timer = 0  # Timer para o efeito de aceleração
        self.is_accelerated = False  # Flag para indicar se está sob efeito de aceleração
        self._all_enemies = []  # Referência para a lista de todos os inimigos
        self.original_color = self.COLOR  # Guarda a cor original
        self.speed_boss_boost = False  # Nova flag para controlar o efeito visual
        
    @classmethod
    def should_spawn(cls):
        return random.randint(1, 100) <= cls.SPAWN_CHANCE
        
    def set_enemies_list(self, enemies):
        """Define a lista de inimigos para referência"""
        self._all_enemies = enemies
        
    def get_nearby_enemies(self):
        """Retorna a lista completa de inimigos"""
        return self._all_enemies
        
    def is_under_immunity_aura(self):
        """Verifica se o inimigo está sob efeito de alguma aura de imunidade"""
        for enemy in self._all_enemies:
            if isinstance(enemy, ImmunityBoss) and enemy.is_immunized:
                if enemy.get_enemies_in_immunity_range(self._all_enemies):
                    dx = self.x - enemy.x
                    dy = self.y - enemy.y
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    if distance <= enemy.immunity_radius:
                        return True
        return False
        
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
            self.dot_tick_timer = 0  # Começa em 0 para aplicar o primeiro tick imediatamente
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
        
    def apply_speed(self, duration_frames=120):  # 2 segundos de duração
        """Aplica efeito de velocidade aumentada"""
        self.speed_timer = duration_frames // GameSpeed.get_instance().current_multiplier  # Usa a duração base
        self.is_accelerated = True
        self.COLOR = SpeedEnemy.COLOR  # Muda a cor para a cor do SpeedEnemy
        if not self.is_frozen and not self.is_slowed:  # Corrigido a condição também
            self.speed = self.base_speed * 1.5  # Aumenta a velocidade em 50%
        
    def update(self):
        """Atualiza os efeitos de status"""
        # Atualiza efeito de fraqueza
        if self.weakness_timer > 0:
            self.weakness_timer -= GameSpeed.get_instance().current_multiplier
            if self.weakness_timer <= 0:
                self.is_weakened = False
                
        # Atualiza efeito de congelamento
        if self.freeze_timer > 0:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.speed = self.base_speed if not self.is_slowed else self.base_speed * 0.5
                if self.is_accelerated:
                    self.speed *= 1.5
                self.is_frozen = False
                
        # Atualiza efeito de slow
        if self.slow_timer > 0:
            self.slow_timer -= GameSpeed.get_instance().current_multiplier
            if self.slow_timer <= 0:
                self.is_slowed = False
                self.speed = self.base_speed
                if self.is_accelerated:
                    self.speed *= 1.5
                
        # Atualiza efeito de velocidade
        if self.speed_timer > 0:
            self.speed_timer -= GameSpeed.get_instance().current_multiplier
            if self.speed_timer <= 0:
                self.is_accelerated = False
                self.COLOR = self.original_color
                if not self.is_frozen:
                    self.speed = self.base_speed if not self.is_slowed else self.base_speed * 0.5
                
        # Atualiza dano ao longo do tempo
        if self.dot_timer > 0:
            self.dot_timer -= GameSpeed.get_instance().current_multiplier
            if self.dot_timer <= 0:
                self.is_burning = False
                self.dot_damage = 0
            else:
                self.dot_tick_timer -= GameSpeed.get_instance().current_multiplier
                if self.dot_tick_timer <= 0:
                    # Só aplica o dano se não estiver sob efeito de imunidade
                    if not self.is_under_immunity_aura():
                        if self.take_damage(self.dot_damage):
                            return "died"  # Retorna indicador de morte por DoT
                    self.dot_tick_timer = 60  # Reseta o timer do tick para 1 segundo
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
        
        # Verifica se há um SpeedBoss no jogo
        speed_multiplier = 1.0
        for enemy in self._all_enemies:
            if isinstance(enemy, SpeedBoss) and enemy != self:
                speed_multiplier += SpeedBoss.SPEED_BOOST
                self.speed_boss_boost = True
                break
        else:
            self.speed_boss_boost = False
        
        # Usa a velocidade atual multiplicada pelo multiplicador global e o boost do boss
        current_speed = self.speed * GameSpeed.get_instance().current_multiplier * speed_multiplier
        
        if distance < current_speed:
            self.path_index += 1
            if self.path_index < len(self.path) - 1:
                self.x, self.y = self.path[self.path_index]
        else:
            if distance != 0:
                dx = dx / distance * current_speed
                dy = dy / distance * current_speed
            else:
                dx, dy = 0, 0  # Ou alguma outra lógica para evitar a divisão
            self.x += dx
            self.y += dy            
        return False
        
    def draw(self, screen):
        # Desenha o círculo do inimigo
        pygame.draw.circle(screen, self.COLOR, (int(self.x), int(self.y)), self.radius)
        
        # Se estiver sob efeito do SpeedBoss, desenha partículas verdes
        if self.speed_boss_boost and not isinstance(self, SpeedBoss):
            for _ in range(2):  # Reduzido para 2 partículas para não ficar muito poluído
                offset_x = random.randint(-self.radius, self.radius)
                offset_y = random.randint(-self.radius, self.radius)
                pygame.draw.circle(screen, (22, 102, 58), 
                                 (int(self.x + offset_x), int(self.y + offset_y)), 2)
        
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
    BASE_HEALTH = 220  # Aumentado para 220
    BASE_SPEED = 1.0  # Reduzido para 1.0
    SPAWN_CHANCE = 15  # Reduzido para 15%
    NAME = "Tanque"  # Nome do inimigo tanque
    REWARD = 3  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 16  # Aumentado para 16
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def apply_freeze(self, duration_frames=120):
        # Imune a freeze
        pass
        
    def apply_slow(self, duration_frames=180):
        # Imune a slow
        pass

class SpeedEnemy(Enemy):
    COLOR = (50, 255, 50)  # Verde
    BASE_HEALTH = 50  # Reduzido para 50
    BASE_SPEED = 3.0  # Aumentado para 3.0
    SPAWN_CHANCE = 25  # Reduzido para 25%
    NAME = "Célere"  # Nome do inimigo veloz
    REWARD = 1  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 8  # Reduzido para 8
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def apply_dot(self, damage, duration_frames=120):
        # Imune a DoT
        pass

class ArmoredEnemy(Enemy):
    COLOR = (128, 128, 128)  # Cinza
    BASE_HEALTH = 135  # Aumentado para 135
    BASE_SPEED = 1.4  # Reduzido para 1.4
    SPAWN_CHANCE = 20  # Reduzido para 20%
    NAME = "Blindado"  # Nome do inimigo blindado
    REWARD = 3  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.damage_reduction = 0.30  # Aumentado para 30%
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
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
    REWARD = 3  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 10
        self.heal_timer = 60
        self.heal_amount = 10
        self.heal_radius = 150
        self.heal_effect_duration = 0  # Novo: duração do efeito visual
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def heal_nearby_enemies(self):
        """Cura inimigos próximos"""
        for enemy in self._all_enemies:
            if enemy != self:  # Não cura a si mesmo
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance <= self.heal_radius:
                    # Só cura se o inimigo não estiver com vida máxima
                    if enemy.health < enemy.max_health:
                        enemy.health = min(enemy.health + self.heal_amount, enemy.max_health)
        
    def move(self):
        self.heal_timer -= GameSpeed.get_instance().current_multiplier
        if self.heal_timer <= 0:
            self.heal_timer = 90
            self.heal_effect_duration = 30  # 0.5 segundos de efeito visual
            self.heal_nearby_enemies()  # Aplica a cura quando o timer zera
            
        # Atualiza a duração do efeito visual
        if self.heal_effect_duration > 0:
            self.heal_effect_duration -= GameSpeed.get_instance().current_multiplier
            
        # Depois move normalmente
        move_result = super().move()
        
        if move_result is True or move_result == "died":
            return move_result
            
        return False
        
    def draw(self, screen):
        super().draw(screen)
        
        # Desenha o efeito de cura apenas quando ativo
        if self.heal_effect_duration > 0:
            opacity = int((self.heal_effect_duration / 30) * 100)  # Fade out do efeito
            heal_surface = pygame.Surface((self.heal_radius * 2, self.heal_radius * 2), pygame.SRCALPHA)
            
            # Círculo externo que expande
            expansion = (30 - self.heal_effect_duration) * 2
            outer_radius = min(self.heal_radius, self.heal_radius - 20 + expansion)
            pygame.draw.circle(heal_surface, (*self.COLOR, opacity), 
                             (self.heal_radius, self.heal_radius), outer_radius, 3)
            
            # Círculo interno que brilha
            inner_opacity = int((self.heal_effect_duration / 30) * 150)
            pygame.draw.circle(heal_surface, (*self.COLOR, inner_opacity), 
                             (self.heal_radius, self.heal_radius), 30)
            
            screen.blit(heal_surface, (int(self.x - self.heal_radius), 
                                     int(self.y - self.heal_radius)))

class FreezeAuraEnemy(Enemy):
    COLOR = (135, 206, 235)  # Azul claro
    BASE_HEALTH = 100
    BASE_SPEED = 1.8
    SPAWN_CHANCE = 15
    NAME = "Gelado"
    REWARD = 2
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 11
        self.freeze_radius = 100
        self._all_defenders = []
        self.aura_duration = 60  # 1 segundo de efeito
        self.is_dying = False  # Flag para controlar o estado de morte
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.apply_freeze_aura(self._all_defenders)
            return False  # Não remove o inimigo ainda
        return self.health <= 0 and self.aura_duration <= 0  # Só remove quando o efeito acabar
        
    def move(self):
        if self.is_dying:
            self.aura_duration -= GameSpeed.get_instance().current_multiplier
            if self.aura_duration <= 0:
                return "died"  # Retorna "died" ao invés de True quando o efeito acabar
            return False
            
        # Se não estiver morrendo, usa o movimento normal
        move_result = super().move()
        
        # Se chegou ao final do caminho, retorna True
        if move_result is True:
            return True
            
        return False
        
    def draw(self, screen):
        if not self.is_dying:
            super().draw(screen)
            
        # Desenha a aura de congelamento quando está morrendo
        if self.is_dying and self.aura_duration > 0:
            # Calcula a opacidade baseada no tempo restante
            opacity = int((self.aura_duration / 60) * 100)
            
            # Cria uma superfície para a aura com transparência
            surface = pygame.Surface((self.freeze_radius * 2, self.freeze_radius * 2), pygame.SRCALPHA)
            
            # Desenha o círculo da aura com a opacidade calculada
            pygame.draw.circle(surface, (*self.COLOR, opacity), 
                             (self.freeze_radius, self.freeze_radius), 
                             self.freeze_radius)
            
            # Desenha a aura
            screen.blit(surface, (int(self.x - self.freeze_radius), 
                                int(self.y - self.freeze_radius)))
        
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

class RageEnemy(Enemy):
    COLOR = (139, 0, 0)  # Vermelho escuro
    BASE_HEALTH = 130  # Reduzido para 130
    BASE_SPEED = 1.6  # Ajustado para 1.6
    SPAWN_CHANCE = 20  # Reduzido para 20%
    NAME = "Furioso"
    REWARD = 4 # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 13
        self.original_speed = self.speed
        self.max_speed_multiplier = 2.5  # Reduzido para 2.5x
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def update(self):
        result = super().update()
        
        # Calcula a velocidade base considerando a raiva
        health_percent = self.health / self.max_health
        rage_multiplier = 1 + ((1 - health_percent) * (self.max_speed_multiplier - 1))
        
        # Aplica a velocidade considerando os efeitos de status
        if self.is_frozen:
            self.speed = 0
        elif self.is_slowed:
            base_speed = self.original_speed * rage_multiplier
            if self.is_accelerated:
                base_speed *= 1.5
            self.speed = base_speed * 0.5
        else:
            base_speed = self.original_speed * rage_multiplier
            if self.is_accelerated:
                base_speed *= 1.5
            self.speed = base_speed
            
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
    BASE_HEALTH = 80  # Reduzido para 80
    BASE_SPEED = 2.0  # Ajustado para 2.0
    SPAWN_CHANCE = 15  # Reduzido para 15%
    NAME = "Furtivo"
    REWARD = 3  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 10
        self.stealth_timer = 0
        self.stealth_interval = 60  # Aumentado para 1 segundo
        self.stealth_duration = 60  # Ajustado para 1 segundo
        self.is_stealthed = False
        self.fade_start = 20  # Frames para começar a aparecer/desaparecer
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
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
        
        # Se estiver sob efeito do SpeedBoss, desenha partículas verdes com a mesma opacidade
        if self.speed_boss_boost:
            for _ in range(2):
                offset_x = random.randint(-self.radius, self.radius)
                offset_y = random.randint(-self.radius, self.radius)
                particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, (22, 102, 58, int(opacity)), 
                                 (2, 2), 2)
                screen.blit(particle_surface, (int(self.x + offset_x - 2), 
                                            int(self.y + offset_y - 2)))
        
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
    
class SpeedBoss(Enemy):
    COLOR = (22, 102, 58)  # Verde escuro
    BASE_HEALTH = 850  # Mantido
    BASE_SPEED = 1.2  # Mantido
    NAME = "Veloz"
    SPAWN_CHANCE = 0  # Não spawna aleatoriamente
    REWARD = 50  # Mantido
    SPEED_BOOST = 0.20 # 20% de aumento de velocidade
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 20  # Raio maior que inimigos normais
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def draw(self, screen):
        # Desenha o boss com uma aura verde constante
        aura_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (*self.COLOR, 50), 
                         (self.radius * 1.5, self.radius * 1.5), 
                         self.radius * 1.5)
        screen.blit(aura_surface, (int(self.x - self.radius * 1.5), 
                                 int(self.y - self.radius * 1.5)))
        
        # Desenha o boss normalmente
        super().draw(screen)

class SplitBoss(Enemy):
    COLOR = (217, 217, 0)  # Amarelo
    BASE_HEALTH = 600  # Vida base
    BASE_SPEED = 1.2  # Velocidade
    NAME = "Divisor"
    SPAWN_CHANCE = 0  # Não spawna aleatoriamente
    REWARD = 50  # Recompensa em ouro
    wave_manager_global = None
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        global wave_manager_global
        self.radius = 20  # Raio maior que inimigos normais
        self.has_split = False  # Controla se já se dividiu
        self.original_color = self.COLOR
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        wave_manager_global = wave_manager
        
    def take_damage(self, damage):
        """Sobrescreve o método take_damage para implementar a mecânica de divisão"""
        self.health -= damage
        if self.health <= 0 and not self.has_split:
            # Ativa a habilidade de divisão
            self.split()
            return True
        return self.health <= 0
        
    def split(self):
        """Cria dois inimigos menores quando derrotado"""
        self.has_split = True
        # Cria dois minions em posições diferentes
        offsets = [(-20, -20), (20, 20)]  # Deslocamentos para cada minion
        for offset_x, offset_y in offsets:
            split = SplitMinion(self.path, self.path_index, wave_manager_global, self.x + offset_x, self.y + offset_y)
            split.set_enemies_list(self._all_enemies)
            self._all_enemies.append(split)

class SplitMinion(Enemy):
    """Classe para os minions criados quando o SplitBoss é derrotado"""
    COLOR = (245, 245, 86)  # Amarelo claro
    BASE_HEALTH = 300  # 50% da vida do boss
    BASE_SPEED = 1.8  # +50% da velocidade do boss
    NAME = "Dividido"
    SPAWN_CHANCE = 0
    REWARD = 10  # Recompensa em ouro
    
    def __init__(self, path, path_index, wave_manager, x, y):
        print(type(wave_manager_global))
        super().__init__(path, wave_manager_global)
        self.radius = 12  # Raio menor que o boss
        self.path_index = path_index  # Começa do ponto onde o boss morreu
        self.x = x
        self.y = y
        self.reward_given = False  # Permite que dê recompensa ao morrer
        self.max_health = ceil(self.BASE_HEALTH * wave_manager_global.get_health_increase())
        self.health = self.max_health
        
    def draw(self, screen):
        
        # Depois desenha o inimigo normalmente
        super().draw(screen)

class MagnetBoss(Enemy):
    COLOR = (200, 0, 0)  # Vermelho intenso
    BASE_HEALTH = 1250  # Vida base
    BASE_SPEED = 0.85  # Velocidade reduzida
    NAME = "Magnético"
    SPAWN_CHANCE = 0  # Não spawna aleatoriamente
    REWARD = 50  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 20
        self.magnet_interval = 300
        self.magnet_duration = 120
        self.magnet_timer = self.magnet_interval
        self.is_attracting = False
        self.attracted_projectiles = []
        self._all_defenders = []  # Nova lista para referência dos defensores
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def update(self):
        result = super().update()
        
        # Atualiza o timer do magnetismo
        if self.magnet_timer > 0:
            self.magnet_timer -= GameSpeed.get_instance().current_multiplier
            if self.magnet_timer <= 0:
                if self.is_attracting:
                    # Terminou fase de atração, começa intervalo
                    self.magnet_timer = self.magnet_interval
                    self.is_attracting = False
                    # Limpa a lista de projéteis atraídos
                    self.attracted_projectiles = []
                else:
                    # Terminou intervalo, começa atração
                    self.magnet_timer = self.magnet_duration
                    self.is_attracting = True
            
        # Se estiver na fase de atração, atrai todos os projéteis
        if self.is_attracting:
            for defender in self._all_defenders:  # Precisamos adicionar essa referência
                for projectile in defender.projectiles:
                    if projectile not in self.attracted_projectiles:
                        projectile.color = self.COLOR  # Muda a cor do projétil
                        projectile.target = self  # Redireciona o projétil para o boss
                        self.attracted_projectiles.append(projectile)
            
        return result
        
    def draw(self, screen):
        # Desenha o efeito magnético quando ativo
        if self.is_attracting:        
            # Desenha uma borda vermelho escuro em volta do boss
            pygame.draw.circle(screen, (139, 0, 0), (int(self.x), int(self.y)), self.radius + 4, 3)
            pygame.draw.circle(screen, (139, 0, 0), (int(self.x), int(self.y)), self.radius + 8, 2)
            pygame.draw.circle(screen, (139, 0, 0), (int(self.x), int(self.y)), self.radius + 10, 1)
        
        # Desenha o chefão normalmente
        super().draw(screen)

class VampiricBoss(Enemy):
    COLOR = (20, 0, 0)  # Preto avermelhado
    BASE_HEALTH = 600  # Vida base
    BASE_SPEED = 1.1  # Velocidade
    NAME = "Vampiro"
    SPAWN_CHANCE = 0  # Não spawna aleatoriamente
    REWARD = 50  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 20  # Raio maior que inimigos normais
        self.has_revived = False  # Controla se já usou a revive
        self.original_color = self.COLOR
        self.revival_health_percent = 0  # vida ao reviver
        self.drain_percent = 0.5  # 50% de drenagem de vida
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def take_damage(self, damage):
        """Sobrescreve o método take_damage para implementar a mecânica de revive"""
        self.health -= damage
        if self.health <= 0 and not self.has_revived:
            # Ativa a habilidade vampírica
            self.drain_life_from_allies()
            if self.revival_health_percent > 0:
                self.has_revived = True
                return False  # Não morre ainda
        return self.health <= 0
        
    def drain_life_from_allies(self):
        """Drena vida de aliados próximos"""
        total_health_drained = 0
        enemies_drained = 0
        
        # Drena vida de todos os outros inimigos
        for enemy in self._all_enemies:
            if enemy != self:  # Não drena de si mesmo
                health_to_drain = enemy.health * self.drain_percent
                enemy.health -= health_to_drain
                total_health_drained += health_to_drain
                enemies_drained += 1
        
        # Calcula a porcentagem de vida a ser recuperada
        self.revival_health_percent = min(enemies_drained * 0.1, 1.0)  # Máximo de 100%
        
        # Recupera vida baseado no total drenado e inimigos afetados
        self.health = self.max_health * self.revival_health_percent
        
    def draw(self, screen):
        # Efeito visual quando está com pouca vida
        if self.health < self.max_health * 0.3:
            self.COLOR = (min(255, self.original_color[0] + 100), 0, 0)  # Vermelho mais intenso
        else:
            self.COLOR = self.original_color
            
        # Desenha o chefão normalmente
        super().draw(screen)
        
        # Desenha aura vampírica quando está com pouca vida
        if self.health < self.max_health * 0.3 and not self.has_revived:
            aura_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (255, 0, 0, 30), 
                             (self.radius * 1.5, self.radius * 1.5), 
                             self.radius * 1.5)
            screen.blit(aura_surface, (int(self.x - self.radius * 1.5), 
                                     int(self.y - self.radius * 1.5)))

class ImmunityBoss(Enemy):
    COLOR = (255, 255, 255)  # Branco
    BASE_HEALTH = 800  # Aumentado para 1250
    BASE_SPEED = 0.8  # Velocidade reduzida
    NAME = "Protetor"
    SPAWN_CHANCE = 0  # Não spawna aleatoriamente
    REWARD = 50  # Recompensa em ouro
    
    def __init__(self, path, wave_manager):
        super().__init__(path, wave_manager)
        self.radius = 20  # Raio maior que inimigos normais
        self.immunity_radius = 150  # Raio da aura de imunidade
        self.immunity_interval = 180  # 3 segundos entre ativações
        self.immunity_duration = 120  # 2 segundos de duração
        self.immunity_timer = self.immunity_duration  # Começa com o timer cheio
        self.is_immunized = False  # Não começa imunizado
        self.in_immunity_phase = True  # Controla se está na fase de imunidade ou intervalo
        self.max_health = ceil(self.BASE_HEALTH * wave_manager.get_health_increase())
        self.health = self.max_health
        
    def update(self):
        result = super().update()
        
        # Atualiza o timer da imunidade
        if self.immunity_timer > 0:
            self.immunity_timer -= GameSpeed.get_instance().current_multiplier
            if self.immunity_timer <= 0:
                if self.in_immunity_phase:
                    # Terminou fase de imunidade, começa intervalo
                    self.immunity_timer = self.immunity_interval
                    self.is_immunized = False
                    self.in_immunity_phase = False
                else:
                    # Terminou intervalo, começa imunidade
                    self.immunity_timer = self.immunity_duration
                    self.is_immunized = True
                    self.in_immunity_phase = True
            
        return result
        
    def draw(self, screen):
        # Desenha a aura de imunidade se estiver ativa
        if self.is_immunized:
            immunity_surface = pygame.Surface((self.immunity_radius * 2, self.immunity_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(immunity_surface, (255, 255, 255, 50), 
                             (self.immunity_radius, self.immunity_radius), 
                             self.immunity_radius)
            screen.blit(immunity_surface, (int(self.x - self.immunity_radius), 
                                         int(self.y - self.immunity_radius)))
        
        # Desenha o inimigo normalmente
        super().draw(screen)
        
    def get_enemies_in_immunity_range(self, enemies):
        """Retorna todos os inimigos dentro do raio de imunidade"""
        in_range = []
        if self.is_immunized:
            for enemy in enemies:
                if enemy != self:  # Não inclui a si mesmo
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    if distance <= self.immunity_radius:
                        in_range.append(enemy)
        return in_range

def spawn_random_enemy(path, wave_manager):
    """Spawna um inimigo aleatório baseado nas chances da onda atual"""
    chances = wave_manager.get_spawn_chances()
    roll = random.random() * 100  # Número entre 0 e 100
    
    cumulative = 0
    for enemy_type, chance in chances.items():
        cumulative += chance
        if roll <= cumulative:
            if enemy_type == 'normal':
                return Enemy(path, wave_manager), False
            elif enemy_type == 'tank':
                return TankEnemy(path, wave_manager), True
            elif enemy_type == 'speed':
                return SpeedEnemy(path, wave_manager), True
            elif enemy_type == 'armored':
                return ArmoredEnemy(path, wave_manager), True
            elif enemy_type == 'healer':
                return HealerEnemy(path, wave_manager), True
            elif enemy_type == 'freeze_aura':
                return FreezeAuraEnemy(path, wave_manager), True
            elif enemy_type == 'rage':
                return RageEnemy(path, wave_manager), True
            elif enemy_type == 'stealth':
                return StealthEnemy(path, wave_manager), True
            elif enemy_type == 'magnet':
                return MagnetBoss(path, wave_manager), True
            elif enemy_type == 'vampiric':
                return VampiricBoss(path, wave_manager), True
            elif enemy_type == 'split':
                return SplitBoss(path, wave_manager), True
            break
            
    # Se algo der errado, retorna um inimigo normal
    return Enemy(path), False 