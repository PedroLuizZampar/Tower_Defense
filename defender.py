import pygame
import math
from projectile import Projectile
from base import GameSpeed  # Adicione no topo do arquivo

class Defender:
    SIZE = 30  # Tamanho do quadrado do defensor
    RANGE = 150  # Alcance do defensor
    MIN_DISTANCE = 40  # Distância mínima entre defensores
    COST = 100  # Custo do defensor
    BASE_UPGRADE_COST = 10  # Custo base da melhoria
    UPGRADE_SELL_BONUS = 5  # Bônus de venda por melhoria
    COLOR = (0, 0, 255)  # Cor padrão (azul)
    PROJECTILE_COLOR = (255, 255, 0)  # Cor padrão do projétil
    DAMAGE_BUFF = 15  # Buff fixo de dano
    NAME = "Defensor"  # Nome padrão
    BASE_DAMAGE = 8  # Dano base
    BASE_ATTACK_COOLDOWN = 30  # Frames base entre ataques
    
    def __init__(self, x, y, current_wave):
        self.x = x
        self.y = y
        self.color = self.COLOR
        self.base_attack_cooldown = self.BASE_ATTACK_COOLDOWN
        self.attack_cooldown = self.base_attack_cooldown
        self.cooldown_timer = 0
        self.projectiles = []
        self.current_target = None
        self.level = 1
        self.total_invested = self.COST
        self.base_damage = self.BASE_DAMAGE
        self.bonus_damage = 0  # Dano adicional de melhorias
        self.selected = False
        self.placed_wave = current_wave
        self.upgrades_count = 0
        self.has_damage_buff = False
        self.has_yellow_buff = False  # Novo atributo para controlar buff amarelo
        self.is_frozen = False  # Novo atributo para controlar efeito de congelamento
        self.freeze_timer = 0  # Timer para duração do efeito de congelamento

    @classmethod
    def get_preview_color(cls):
        return cls.COLOR
        
    def get_upgrade_cost(self):
        return self.BASE_UPGRADE_COST * self.level
        
    def get_sell_value(self, current_wave):
        # Se está na mesma onda em que foi colocado
        if current_wave == self.placed_wave:
            return self.COST + (self.upgrades_count * self.BASE_UPGRADE_COST)  # Valor total
            
        # Para ondas diferentes
        base_return = self.COST // 2  # 50% do custo base
        upgrade_bonus = self.upgrades_count * self.UPGRADE_SELL_BONUS
        return base_return + upgrade_bonus
        
    def upgrade(self):
        cost = self.get_upgrade_cost()
        self.level += 1
        self.total_invested += cost
        self.bonus_damage += round(self.get_total_damage() * 0.2, 1)
        self.attack_cooldown = self.base_attack_cooldown * (0.99 ** (self.level - 1))
        self.upgrades_count += 1
        return cost
        
    def get_total_damage(self):
        # Calcula o dano total considerando o dano base, bônus de upgrade e buffs
        total = self.base_damage + self.bonus_damage
        if self.has_damage_buff:
            total += self.DAMAGE_BUFF
        if self.has_yellow_buff:
            total *= 1.5  # Aumenta o dano em 50% com buff amarelo
        return total
        
    def find_target(self, enemies):
        # Se já tem um alvo e ele ainda está vivo, no alcance e não está invisível
        if self.current_target in enemies:
            # Verifica se o alvo está invisível
            if hasattr(self.current_target, 'is_stealthed') and self.current_target.is_stealthed:
                self.current_target = None
            else:
                dx = self.current_target.x - self.x
                dy = self.current_target.y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance <= self.RANGE:
                    return self.current_target
                
        # Se não tem alvo ou o alvo morreu/saiu do alcance, procura o mais próximo
        self.current_target = None
        closest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            # Ignora inimigos invisíveis
            if hasattr(enemy, 'is_stealthed') and enemy.is_stealthed:
                continue
                
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            
            if distance <= self.RANGE and distance < min_distance:
                closest_enemy = enemy
                min_distance = distance
                
        self.current_target = closest_enemy
        return closest_enemy
        
    def get_enemies_in_range(self, enemies):
        """Retorna todos os inimigos dentro do alcance"""
        in_range = []
        for enemy in enemies:
            # Ignora inimigos invisíveis
            if hasattr(enemy, 'is_stealthed') and enemy.is_stealthed:
                continue
                
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= self.RANGE:
                in_range.append(enemy)
        return in_range
        
    def get_defenders_in_range(self, defenders):
        """Retorna todos os defensores dentro do alcance"""
        in_range = []
        for defender in defenders:
            if defender != self:  # Não inclui a si mesmo
                dx = defender.x - self.x
                dy = defender.y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance <= self.RANGE:
                    in_range.append(defender)
        return in_range
        
    def apply_damage_buff(self):
        """Aplica o buff de dano do defensor amarelo"""
        self.has_yellow_buff = True
        
    def apply_freeze(self, duration_frames=90):  # 1.5 segundos = 90 frames
        """Aplica efeito de congelamento na torre"""
        self.is_frozen = True
        self.freeze_timer = duration_frames

    def update(self, enemies):
        # Atualiza o cooldown considerando o multiplicador de velocidade global
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
            
        # Atualiza o efeito de congelamento
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return  # Se estiver congelado, não faz mais nada
            
        # Procura alvo e atira
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                if hasattr(target, "is_dying"):
                    if not target.is_dying:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                        self.cooldown_timer = self.attack_cooldown
                        self.has_damage_buff = False  # Remove o buff após o ataque
                        self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                else:
                    projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                    projectile.damage = self.get_total_damage()
                    self.projectiles.append(projectile)
                    self.cooldown_timer = self.attack_cooldown
                    self.has_damage_buff = False  # Remove o buff após o ataque
                    self.has_yellow_buff = False  # Remove o buff amarelo após o ataque

    def draw(self, screen, show_range=False):
        # Desenha o range se solicitado ou se selecionado
        if show_range or self.selected:
            pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), 
                             self.RANGE, 1)
        
        # Desenha o efeito de congelamento (quadrado translúcido azul-claro)
        if self.is_frozen:
            freeze_surface = pygame.Surface((self.SIZE + 20, self.SIZE + 20), pygame.SRCALPHA)
            pygame.draw.rect(freeze_surface, (135, 206, 235, 128),  # Azul claro semi-transparente
                           (0, 0, self.SIZE + 20, self.SIZE + 20))
            screen.blit(freeze_surface, (self.x - (self.SIZE + 20)//2, 
                                     self.y - (self.SIZE + 20)//2))
        
        # Desenha o defensor
        base_color = (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50)) if self.selected else self.color
        pygame.draw.rect(screen, base_color, 
                        (self.x - self.SIZE//2, 
                         self.y - self.SIZE//2, 
                         self.SIZE, self.SIZE))
                         
        # Desenha borda amarela se tiver buff
        if self.has_yellow_buff:
            pygame.draw.rect(screen, (255, 255, 0), 
                           (self.x - self.SIZE//2, 
                            self.y - self.SIZE//2, 
                            self.SIZE, self.SIZE), 2)
                         
        # Desenha o nível
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.level), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
                         
        # Desenha os projéteis
        for projectile in self.projectiles:
            projectile.draw(screen)
            
    def handle_click(self, pos):
        # Verifica se o clique foi no defensor
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        if abs(dx) <= self.SIZE//2 and abs(dy) <= self.SIZE//2:
            self.selected = True
            return True
        return False

    @classmethod
    def draw_preview(cls, screen, x, y, is_valid):
        """Desenha uma prévia do defensor na posição do mouse"""
        color = cls.COLOR if is_valid else (255, 50, 50)  # Vermelho se posição inválida
        pygame.draw.rect(screen, color, 
                        (x - cls.SIZE//2, 
                         y - cls.SIZE//2, 
                         cls.SIZE, cls.SIZE))
                         
    @staticmethod
    def is_too_close(x, y, defenders):
        """Verifica se a posição está muito próxima de outros defensores"""
        for defender in defenders:
            dx = x - defender.x
            dy = y - defender.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance < Defender.MIN_DISTANCE:
                return True
        return False

class BasicDefender(Defender):
    COLOR = (28, 43, 61)  # Cinza azulado escuro
    PROJECTILE_COLOR = (66, 86, 110)  # Cinza azulado escuro mais claro
    COST = 50  # Defensor mais barato
    NAME = "Básico"
    BASE_DAMAGE = 11
    BASE_ATTACK_COOLDOWN = 30
    RANGE = 130
    HITS_TO_ACTIVATE = 0
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)

class RedDefender(Defender):
    COLOR = (255, 0, 0)  # Vermelho
    PROJECTILE_COLOR = (255, 100, 100)  # Vermelho claro
    COST = 75
    NAME = "Flamejante"
    BASE_DAMAGE = 9
    BASE_ATTACK_COOLDOWN = 25
    UNLOCK_COST = 2
    RANGE = 140
    HITS_TO_ACTIVATE = 6
    EFFECT_COLOR = (255, 165, 0)  # Laranja para o efeito de queimadura
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.HITS_TO_ACTIVATE = 6
        self.attack_counter = 0
        self.effect_duration = 0  # Duração do efeito visual
        
    def update(self, enemies):
        # Atualiza o efeito de congelamento primeiro
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return  # Se estiver congelado, não faz mais nada

        # Atualiza o cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
            
        # Atualiza a duração do efeito visual
        if self.effect_duration > 0:
            self.effect_duration -= GameSpeed.get_instance().current_multiplier
            
        # Procura alvo e atira
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                if hasattr(target, "is_dying"):
                    if not target.is_dying:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                        self.cooldown_timer = self.attack_cooldown
                        self.has_damage_buff = False  # Remove o buff após o ataque
                        self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                        
                        # Incrementa o contador de ataques
                        self.attack_counter += 1
                        
                        # Se atingiu o número necessário de ataques, ativa a habilidade especial
                        if self.attack_counter >= self.HITS_TO_ACTIVATE:
                            self.attack_counter = 0  # Reseta o contador
                            self.effect_duration = 60  # 1 segundo de efeito visual
                            # Aplica dano ao longo do tempo em todos os inimigos no alcance
                            dot_damage = projectile.damage * 0.5  # 50% do dano normal
                            for enemy in self.get_enemies_in_range(enemies):
                                enemy.apply_dot(dot_damage, duration_frames=180)
                else:
                    projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                    projectile.damage = self.get_total_damage()
                    self.projectiles.append(projectile)
                    self.cooldown_timer = self.attack_cooldown
                    self.has_damage_buff = False  # Remove o buff após o ataque
                    self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                    
                    # Incrementa o contador de ataques
                    self.attack_counter += 1
                    
                    # Se atingiu o número necessário de ataques, ativa a habilidade especial
                    if self.attack_counter >= self.HITS_TO_ACTIVATE:
                        self.attack_counter = 0  # Reseta o contador
                        self.effect_duration = 60  # 1 segundo de efeito visual
                        # Aplica dano ao longo do tempo em todos os inimigos no alcance
                        dot_damage = projectile.damage * 0.5  # 50% do dano normal
                        for enemy in self.get_enemies_in_range(enemies):
                            enemy.apply_dot(dot_damage, duration_frames=180)

    def draw(self, screen, show_range=False):
        # Desenha o efeito de queimadura se estiver ativo
        if self.effect_duration > 0:
            effect_surface = pygame.Surface((self.RANGE * 2, self.RANGE * 2), pygame.SRCALPHA)
            opacity = int((self.effect_duration / 60) * 50)  # Máximo de 50 de opacidade
            pygame.draw.circle(effect_surface, (*self.EFFECT_COLOR, opacity), 
                             (self.RANGE, self.RANGE), self.RANGE)
            screen.blit(effect_surface, (int(self.x - self.RANGE), int(self.y - self.RANGE)))
            
        super().draw(screen, show_range)

class YellowDefender(Defender):
    COLOR = (194, 187, 0)  # Amarelo
    PROJECTILE_COLOR = (255, 255, 150)  # Amarelo claro
    COST = 100
    NAME = "Luminoso"
    BASE_DAMAGE = 20
    BASE_ATTACK_COOLDOWN = 50
    UNLOCK_COST = 3
    RANGE = 200
    HITS_TO_ACTIVATE = 8
    EFFECT_COLOR = (255, 255, 0)  # Amarelo brilhante para o efeito de buff
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.attack_counter = 0
        self.effect_duration = 0  # Duração do efeito visual
        
    def update(self, enemies, defenders=None):
        # Atualiza o efeito de congelamento primeiro
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return  # Se estiver congelado, não faz mais nada

        # Atualiza o cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
            
        # Atualiza a duração do efeito visual
        if self.effect_duration > 0:
            self.effect_duration -= GameSpeed.get_instance().current_multiplier
            
        # Procura alvo e atira
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                if hasattr(target, "is_dying"):
                    if not target.is_dying:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                        self.cooldown_timer = self.attack_cooldown
                        self.has_damage_buff = False  # Remove o buff após o ataque
                        self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                        
                        # Incrementa o contador de ataques
                        self.attack_counter += 1
                        
                        # Se atingiu o número necessário de ataques, ativa a habilidade especial
                        if self.attack_counter >= self.HITS_TO_ACTIVATE and defenders:
                            self.attack_counter = 0  # Reseta o contador
                            self.effect_duration = 60  # 1 segundo de efeito visual
                            # Aplica buff de dano em todos os defensores no alcance
                            for defender in self.get_defenders_in_range(defenders):
                                defender.apply_damage_buff()
                else:
                    projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                    projectile.damage = self.get_total_damage()
                    self.projectiles.append(projectile)
                    self.cooldown_timer = self.attack_cooldown
                    self.has_damage_buff = False  # Remove o buff após o ataque
                    self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                    
                    # Incrementa o contador de ataques
                    self.attack_counter += 1
                    
                    # Se atingiu o número necessário de ataques, ativa a habilidade especial
                    if self.attack_counter >= self.HITS_TO_ACTIVATE and defenders:
                        self.attack_counter = 0  # Reseta o contador
                        self.effect_duration = 60  # 1 segundo de efeito visual
                        # Aplica buff de dano em todos os defensores no alcance
                        for defender in self.get_defenders_in_range(defenders):
                            defender.apply_damage_buff()

    def draw(self, screen, show_range=False):
        # Desenha o efeito de buff se estiver ativo
        if self.effect_duration > 0:
            effect_surface = pygame.Surface((self.RANGE * 2, self.RANGE * 2), pygame.SRCALPHA)
            opacity = int((self.effect_duration / 60) * 50)  # Máximo de 50 de opacidade
            pygame.draw.circle(effect_surface, (*self.EFFECT_COLOR, opacity), 
                             (self.RANGE, self.RANGE), self.RANGE)
            screen.blit(effect_surface, (int(self.x - self.RANGE), int(self.y - self.RANGE)))
            
        super().draw(screen, show_range)

class GreenDefender(Defender):
    COLOR = (0, 100, 0)  # Verde escuro
    PROJECTILE_COLOR = (0, 150, 0)  # Verde escuro mais claro
    COST = 125
    NAME = "Retardante"
    BASE_DAMAGE = 12
    BASE_ATTACK_COOLDOWN = 45
    RANGE = 130
    UNLOCK_COST = 4
    HITS_TO_ACTIVATE = 5
    EFFECT_COLOR = (0, 255, 0)  # Verde claro para o efeito de slow
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.attack_counter = 0
        self.effect_duration = 0  # Duração do efeito visual
        
    def update(self, enemies):
        # Atualiza o efeito de congelamento primeiro
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return  # Se estiver congelado, não faz mais nada

        # Atualiza o cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
            
        # Atualiza a duração do efeito visual
        if self.effect_duration > 0:
            self.effect_duration -= GameSpeed.get_instance().current_multiplier
            
        # Procura alvo e atira
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                if hasattr(target, "is_dying"):
                    if not target.is_dying:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                        self.cooldown_timer = self.attack_cooldown
                        self.has_damage_buff = False  # Remove o buff após o ataque
                        self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                        
                        # Incrementa o contador de ataques
                        self.attack_counter += 1
                        
                        # Se atingiu o número necessário de ataques, ativa a habilidade especial
                        if self.attack_counter >= self.HITS_TO_ACTIVATE:
                            self.attack_counter = 0  # Reseta o contador
                            self.effect_duration = 60  # 1 segundo de efeito visual
                            # Aplica slow em todos os inimigos no alcance
                            for enemy in self.get_enemies_in_range(enemies):
                                enemy.apply_slow(180)  # 3 segundos de slow'
                else:
                    projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                    projectile.damage = self.get_total_damage()
                    self.projectiles.append(projectile)
                    self.cooldown_timer = self.attack_cooldown
                    self.has_damage_buff = False  # Remove o buff após o ataque
                    self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                    
                    # Incrementa o contador de ataques
                    self.attack_counter += 1
                    
                    # Se atingiu o número necessário de ataques, ativa a habilidade especial
                    if self.attack_counter >= self.HITS_TO_ACTIVATE:
                        self.attack_counter = 0  # Reseta o contador
                        self.effect_duration = 60  # 1 segundo de efeito visual
                        # Aplica slow em todos os inimigos no alcance
                        for enemy in self.get_enemies_in_range(enemies):
                            enemy.apply_slow(180)  # 3 segundos de slow'

    def draw(self, screen, show_range=False):
        # Desenha o efeito de slow se estiver ativo
        if self.effect_duration > 0:
            effect_surface = pygame.Surface((self.RANGE * 2, self.RANGE * 2), pygame.SRCALPHA)
            opacity = int((self.effect_duration / 60) * 50)  # Máximo de 50 de opacidade
            pygame.draw.circle(effect_surface, (*self.EFFECT_COLOR, opacity), 
                             (self.RANGE, self.RANGE), self.RANGE)
            screen.blit(effect_surface, (int(self.x - self.RANGE), int(self.y - self.RANGE)))
            
        super().draw(screen, show_range)

class BlueDefender(Defender):
    COLOR = (0, 0, 255)  # Azul
    PROJECTILE_COLOR = (43, 181, 255)  # Azul claro
    COST = 150
    NAME = "Congelante"
    BASE_DAMAGE = 9
    BASE_ATTACK_COOLDOWN = 35
    UNLOCK_COST = 5
    RANGE = 140
    HITS_TO_ACTIVATE = 8
    EFFECT_COLOR = (135, 206, 235)  # Azul claro para o efeito de congelamento
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.attack_counter = 0
        self.effect_duration = 0  # Duração do efeito visual
        
    def update(self, enemies):
        # Atualiza o efeito de congelamento primeiro
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return  # Se estiver congelado, não faz mais nada

        # Atualiza o cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
            
        # Atualiza a duração do efeito visual
        if self.effect_duration > 0:
            self.effect_duration -= GameSpeed.get_instance().current_multiplier
            
        # Procura alvo e atira
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                if hasattr(target, "is_dying"):
                    if not target.is_dying:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                        self.cooldown_timer = self.attack_cooldown
                        self.has_damage_buff = False  # Remove o buff após o ataque
                        self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                        
                        # Incrementa o contador de ataques
                        self.attack_counter += 1
                        
                        # Se atingiu o número necessário de ataques, ativa a habilidade especial
                        if self.attack_counter >= self.HITS_TO_ACTIVATE:
                            self.attack_counter = 0  # Reseta o contador
                            self.effect_duration = 60  # 1 segundo de efeito visual
                            # Aplica freeze em todos os inimigos no alcance
                            for enemy in self.get_enemies_in_range(enemies):
                                enemy.apply_freeze(90)  # 1.5 segundos de freeze
                else:
                    projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                    projectile.damage = self.get_total_damage()
                    self.projectiles.append(projectile)
                    self.cooldown_timer = self.attack_cooldown
                    self.has_damage_buff = False  # Remove o buff após o ataque
                    self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                    
                    # Incrementa o contador de ataques
                    self.attack_counter += 1
                    
                    # Se atingiu o número necessário de ataques, ativa a habilidade especial
                    if self.attack_counter >= self.HITS_TO_ACTIVATE:
                        self.attack_counter = 0  # Reseta o contador
                        self.effect_duration = 60  # 1 segundo de efeito visual
                        # Aplica freeze em todos os inimigos no alcance
                        for enemy in self.get_enemies_in_range(enemies):
                            enemy.apply_freeze(90)  # 1.5 segundos de freeze

    def draw(self, screen, show_range=False):
        # Desenha o efeito de congelamento se estiver ativo
        if self.effect_duration > 0:
            effect_surface = pygame.Surface((self.RANGE * 2, self.RANGE * 2), pygame.SRCALPHA)
            opacity = int((self.effect_duration / 60) * 50)  # Máximo de 50 de opacidade
            pygame.draw.circle(effect_surface, (*self.EFFECT_COLOR, opacity), 
                             (self.RANGE, self.RANGE), self.RANGE)
            screen.blit(effect_surface, (int(self.x - self.RANGE), int(self.y - self.RANGE)))
            
        super().draw(screen, show_range)

class PinkDefender(Defender):
    COLOR = (255, 182, 193)  # Rosa claro
    PROJECTILE_COLOR = (255, 105, 180)  # Rosa mais escuro
    COST = 250
    UNLOCK_COST = 6
    NAME = "Empilhador"
    BASE_DAMAGE = 5
    BASE_ATTACK_COOLDOWN = 15
    RANGE = 180
    MAX_STACK_MULTIPLIER = 10
    HITS_TO_ACTIVATE = 4
    BASE_UPGRADE_COST = 30

    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.attack_counter = 0
        self.stack_multiplier = 1

    def find_target(self, enemies):
        previous_target = self.current_target
        new_target = super().find_target(enemies)
        if new_target != previous_target:
            self.stack_multiplier = 1  # Reset stack multiplier when target changes
            self.attack_counter = 0
            self.color = self.COLOR  # Reset color to default
        return new_target

    def update(self, enemies):
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return

        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier

        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                if hasattr(target, "is_dying"):
                    if not target.is_dying:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                        self.cooldown_timer = self.attack_cooldown
                        self.attack_counter += 1

                        if self.attack_counter >= self.HITS_TO_ACTIVATE:
                            self.attack_counter = 0
                            if self.stack_multiplier < self.MAX_STACK_MULTIPLIER:
                                self.stack_multiplier += 1
                                self.color = (
                                    min(255, self.COLOR[0] + self.stack_multiplier * 10),
                                    max(0, self.COLOR[1] - self.stack_multiplier * 20),
                                    max(0, self.COLOR[2] - self.stack_multiplier * 20),
                                )
                else:
                    projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                    projectile.damage = self.get_total_damage()
                    self.projectiles.append(projectile)
                    self.cooldown_timer = self.attack_cooldown
                    self.attack_counter += 1

                    if self.attack_counter >= self.HITS_TO_ACTIVATE:
                        self.attack_counter = 0
                        if self.stack_multiplier < self.MAX_STACK_MULTIPLIER:
                            self.stack_multiplier += 1
                            self.color = (
                                min(255, self.COLOR[0] + self.stack_multiplier * 10),
                                max(0, self.COLOR[1] - self.stack_multiplier * 20),
                                max(0, self.COLOR[2] - self.stack_multiplier * 20),
                            )

    def get_total_damage(self):
        return self.base_damage * self.stack_multiplier

    def upgrade(self):
        cost = self.get_upgrade_cost()
        self.level += 1
        self.total_invested += cost
        self.base_damage += 1  # Increase base damage by 1
        self.upgrades_count += 1
        return cost

    def draw(self, screen, show_range=False):
        super().draw(screen, show_range)

class OrangeDefender(Defender):
    COLOR = (255, 140, 0)  # Laranja
    PROJECTILE_COLOR = (255, 165, 0)  # Laranja mais claro
    COST = 175
    NAME = "Duplo"
    BASE_DAMAGE = 10
    BASE_ATTACK_COOLDOWN = 35
    RANGE = 160
    UNLOCK_COST = 6
    HITS_TO_ACTIVATE = 0
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        
    def find_targets(self, enemies):
        """Encontra os dois alvos mais próximos"""
        targets = []
        distances = []
        
        for enemy in enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            
            if distance <= self.RANGE:
                # Insere ordenado por distância
                insert_index = 0
                for i, d in enumerate(distances):
                    if distance > d:
                        insert_index = i + 1
                distances.insert(insert_index, distance)
                targets.insert(insert_index, enemy)
                
                if len(targets) > 2:  # Mantém apenas os 2 mais próximos
                    targets.pop()
                    distances.pop()
                    
        return targets
        
    def update(self, enemies):
        # Atualiza o efeito de congelamento primeiro
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return  # Se estiver congelado, não faz mais nada

        # Atualiza o cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
            
        # Procura alvos e atira
        if self.cooldown_timer <= 0:
            targets = self.find_targets(enemies)
            if targets:
                for target in targets:
                    if hasattr(target, "is_dying"):
                        if not target.is_dying:
                            projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                            projectile.damage = self.get_total_damage()
                            self.projectiles.append(projectile)
                    else:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                self.cooldown_timer = self.attack_cooldown
                self.has_damage_buff = False  # Remove o buff após o ataque
                self.has_yellow_buff = False  # Remove o buff amarelo após o ataque

class PurpleDefender(Defender):
    COLOR = (75, 0, 130)  # Roxo escuro
    PROJECTILE_COLOR = (128, 0, 128)  # Roxo mais claro para projéteis
    BASE_DAMAGE = 18
    COST = 200
    RANGE = 135
    NAME = "Enfraquecedor"
    UNLOCK_COST = 8
    BASE_ATTACK_COOLDOWN = 50
    HITS_TO_ACTIVATE = 8
    EFFECT_COLOR = (147, 112, 219)  # Roxo claro para o efeito de fraqueza
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.hits_counter = 0
        self.effect_duration = 0  # Duração do efeito visual
        
    def update(self, enemies):
        # Atualiza o efeito de congelamento primeiro
        if self.is_frozen:
            self.freeze_timer -= GameSpeed.get_instance().current_multiplier
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return  # Se estiver congelado, não faz mais nada

        # Atualiza o cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
            
        # Atualiza a duração do efeito visual
        if self.effect_duration > 0:
            self.effect_duration -= GameSpeed.get_instance().current_multiplier
            
        # Procura alvo e atira
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                if hasattr(target, "is_dying"):
                    if not target.is_dying:
                        projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                        projectile.damage = self.get_total_damage()
                        self.projectiles.append(projectile)
                        self.cooldown_timer = self.attack_cooldown
                        self.has_damage_buff = False  # Remove o buff após o ataque
                        self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                        
                        # Incrementa o contador de hits
                        self.hits_counter += 1
                        
                        # Se atingiu o número necessário de hits, aplica fraqueza em todos os inimigos no alcance
                        if self.hits_counter >= self.HITS_TO_ACTIVATE:
                            self.hits_counter = 0  # Reseta o contador
                            self.effect_duration = 60  # 1 segundo de efeito visual
                            # Aplica fraqueza em todos os inimigos no alcance
                            for enemy in self.get_enemies_in_range(enemies):
                                enemy.apply_weakness()  # Aplica o efeito de fraqueza
                        return projectile
                else:
                    projectile = Projectile(self.x, self.y, target, self.PROJECTILE_COLOR)
                    projectile.damage = self.get_total_damage()
                    self.projectiles.append(projectile)
                    self.cooldown_timer = self.attack_cooldown
                    self.has_damage_buff = False  # Remove o buff após o ataque
                    self.has_yellow_buff = False  # Remove o buff amarelo após o ataque
                    
                    # Incrementa o contador de hits
                    self.hits_counter += 1
                    
                    # Se atingiu o número necessário de hits, aplica fraqueza em todos os inimigos no alcance
                    if self.hits_counter >= self.HITS_TO_ACTIVATE:
                        self.hits_counter = 0  # Reseta o contador
                        self.effect_duration = 60  # 1 segundo de efeito visual
                        # Aplica fraqueza em todos os inimigos no alcance
                        for enemy in self.get_enemies_in_range(enemies):
                            enemy.apply_weakness()  # Aplica o efeito de fraqueza
                    return projectile
        return None
        
    def draw(self, screen, show_range=False):
        # Desenha o efeito de fraqueza se estiver ativo
        if self.effect_duration > 0:
            effect_surface = pygame.Surface((self.RANGE * 2, self.RANGE * 2), pygame.SRCALPHA)
            opacity = int((self.effect_duration / 60) * 50)  # Máximo de 50 de opacidade
            pygame.draw.circle(effect_surface, (*self.EFFECT_COLOR, opacity), 
                             (self.RANGE, self.RANGE), self.RANGE)
            screen.blit(effect_surface, (int(self.x - self.RANGE), int(self.y - self.RANGE)))
            
        super().draw(screen, show_range)


class DefenderButton:
    def __init__(self, defender_class, x_pos, mission_manager=None):
        self.width = 230
        self.height = 90
        self.defender_class = defender_class
        self.cost = defender_class.COST
        self.selected = False
        self.rect = pygame.Rect(x_pos, 0, self.width, self.height)
        self.mission_manager = mission_manager
        self.unlocked = not hasattr(defender_class, 'UNLOCK_COST')
        
    def draw(self, screen, gold, ajust):        
        if self.selected:
            rect_copy = self.rect.copy()
            pygame.draw.rect(screen, (255, 255, 255), rect_copy, 3)
        
        if not self.unlocked:
            lock_surface = pygame.Surface((self.rect.width, self.rect.height))  
            lock_surface.set_alpha(240)
            lock_surface.fill((99, 99, 99))
            screen.blit(lock_surface, (self.rect.x, self.rect.y + ajust))

            font_block = pygame.font.Font(None, 24)
            orb_text = font_block.render(f"{self.defender_class.UNLOCK_COST} Orbes", True, (50, 255, 50))
            orb_rect = orb_text.get_rect(center=(self.rect.centerx, self.rect.centery + ajust + 15))
            screen.blit(orb_text, orb_rect)
            
            lock_text = font_block.render("Bloqueado", True, (252, 25, 25))
            lock_rect = lock_text.get_rect(center=(self.rect.centerx, self.rect.centery + ajust - 15))
            screen.blit(lock_text, lock_rect)
        else:
            font = pygame.font.Font(None, 20)
            cost_text = font.render(f"Custo: {self.cost}", True, 
                                    (255, 215, 0) if gold >= self.cost else (255, 0, 0))
            cost_rect = cost_text.get_rect(x=self.rect.x + 150, centery=self.rect.top + ajust + 15)
            screen.blit(cost_text, cost_rect)

    def handle_click(self, pos, gold):
        if self.rect.collidepoint(pos):
            if not self.unlocked and hasattr(self.defender_class, 'UNLOCK_COST'):
                if self.mission_manager and self.mission_manager.orbes >= self.defender_class.UNLOCK_COST:
                    self.mission_manager.orbes -= self.defender_class.UNLOCK_COST
                    self.unlocked = True
                return False
            elif self.unlocked and gold >= self.cost:
                self.selected = not self.selected
                return True
        return False