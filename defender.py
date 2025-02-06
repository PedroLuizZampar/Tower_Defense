import pygame
import math
from projectile import Projectile

class Defender:
    SIZE = 30  # Tamanho do quadrado do defensor
    RANGE = 150  # Alcance do defensor
    MIN_DISTANCE = 40  # Distância mínima entre defensores
    COST = 100  # Custo do defensor
    BASE_UPGRADE_COST = 15  # Custo base da melhoria
    UPGRADE_SELL_BONUS = 5  # Bônus de venda por melhoria
    COLOR = (0, 0, 255)  # Cor padrão (azul)
    PROJECTILE_COLOR = (255, 255, 0)  # Cor padrão do projétil
    DAMAGE_BUFF = 10  # Buff fixo de dano
    NAME = "Defensor"  # Nome padrão
    BASE_DAMAGE = 10  # Dano base
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
        self.damage_multiplier = 1.0
        self.has_yellow_buff = False  # Novo atributo para controlar buff amarelo

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
        upgrade_bonus = self.upgrades_count * self.UPGRADE_SELL_BONUS  # 5 de ouro por melhoria
        return base_return + upgrade_bonus
        
    def upgrade(self):
        cost = self.get_upgrade_cost()
        self.level += 1
        self.total_invested += cost
        self.bonus_damage += round(self.base_damage * 0.1, 1) # Aumenta o dano em 2 por upgrade
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
        # Se já tem um alvo e ele ainda está vivo e no alcance, mantém o mesmo alvo
        if self.current_target in enemies:
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
        
    def update(self, enemies):
        # Atualiza o cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            
        # Procura alvo e atira
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
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
    BASE_DAMAGE = 8
    BASE_ATTACK_COOLDOWN = 35  # Ataque mais lento
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.damage_multiplier = 1.0

class BlueDefender(Defender):
    COLOR = (0, 0, 255)  # Azul
    PROJECTILE_COLOR = (43, 181, 255)  # Azul claro
    COST = 75
    NAME = "Congelante"
    BASE_DAMAGE = 10
    BASE_ATTACK_COOLDOWN = 30
    UNLOCK_COST = 2  # Custo em orbes para desbloquear
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.attacks_until_slow = 8
        self.attack_counter = 0

class RedDefender(Defender):
    COLOR = (255, 0, 0)  # Vermelho
    PROJECTILE_COLOR = (255, 100, 100)  # Vermelho claro
    COST = 100
    NAME = "Flamejante"
    BASE_DAMAGE = 12
    BASE_ATTACK_COOLDOWN = 25
    UNLOCK_COST = 3  # Custo em orbes para desbloquear
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.damage_multiplier = 1.2
        self.attacks_until_burn = 5
        self.attack_counter = 0

class YellowDefender(Defender):
    COLOR = (194, 187, 0)  # Amarelo
    PROJECTILE_COLOR = (255, 255, 150)  # Amarelo claro
    COST = 125
    NAME = "Luminoso"
    BASE_DAMAGE = 15
    BASE_ATTACK_COOLDOWN = 35
    UNLOCK_COST = 5  # Custo em orbes para desbloquear
    
    def __init__(self, x, y, current_wave):
        super().__init__(x, y, current_wave)
        self.damage_multiplier = 1.5
        self.attacks_until_buff = 10
        self.attack_counter = 0

class DefenderButton:
    def __init__(self, defender_class, x_pos, mission_manager=None):
        self.width = 100
        self.height = 100
        self.color = defender_class.get_preview_color()
        self.rect = pygame.Rect(x_pos, 700, self.width, self.height)
        self.selected = False
        self.cost = defender_class.COST
        self.defender_class = defender_class
        self.range = defender_class.RANGE
        self.mission_manager = mission_manager
        self.unlocked = not hasattr(defender_class, 'UNLOCK_COST')  # Básico já vem desbloqueado
        
    def is_available(self, gold):
        if not self.unlocked:
            return False
        return gold >= self.cost
        
    def draw(self, screen, gold):
        # Desenha o fundo do botão
        button_color = (100, 100, 100)  # Cor base para botão bloqueado/indisponível
        
        if self.unlocked:
            button_color = self.color if gold >= self.cost else (100, 100, 100)
        
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        
        # Desenha o defensor
        inner_size = 70
        inner_rect = pygame.Rect(
            self.rect.centerx - inner_size//2,
            self.rect.centery - inner_size//2,
            inner_size,
            inner_size
        )
        pygame.draw.rect(screen, button_color, inner_rect)
        
        # Desenha borda quando selecionado
        if self.selected:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
            
        # Desenha o custo ou requisito de desbloqueio
        font = pygame.font.Font(None, 24)
        if not self.unlocked and hasattr(self.defender_class, 'UNLOCK_COST'):
            text = font.render(f"{self.defender_class.UNLOCK_COST} Orbes", True, (50, 255, 50))
        else:
            text_color = (255, 215, 0) if gold >= self.cost else (255, 0, 0)
            text = font.render(str(self.cost), True, text_color)
        
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom + 10))
        screen.blit(text, text_rect)
        
        # Se estiver bloqueado, desenha um cadeado
        if not self.unlocked:
            lock_text = font.render("Bloqueado", True, (255, 15, 15))
            lock_rect = lock_text.get_rect(center=inner_rect.center)
            screen.blit(lock_text, lock_rect)
            
    def handle_click(self, pos, gold):
        if self.rect.collidepoint(pos):
            if not self.unlocked and hasattr(self.defender_class, 'UNLOCK_COST'):
                # Tenta desbloquear com orbes
                if (self.mission_manager and 
                    self.mission_manager.orbes >= self.defender_class.UNLOCK_COST):
                    self.mission_manager.orbes -= self.defender_class.UNLOCK_COST
                    self.unlocked = True
                return False
            elif self.unlocked and gold >= self.cost:
                self.selected = not self.selected
                return True
        return False 