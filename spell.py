import pygame
import math
from enemy import TankEnemy, ArmoredEnemy, SpeedEnemy, HealerEnemy
from base import GameSpeed

class Spell:
    COST = 0  # Removido custo em ouro
    RADIUS = 100  # Raio base
    COLOR = (255, 255, 255)  # Cor base
    NAME = "Feitiço Base"
    COOLDOWN = 600  # Cooldown base (10 segundos)
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.duration = 60  # 1 segundo em frames
        self.current_duration = self.duration
        self.active = True
        self.effect_applied = False  # Flag para controlar se o efeito já foi aplicado
        
    def update(self, enemies=None, defenders=None):
        # AQUI É ONDE RECEBE A LISTA DE INIMIGOS (PASSAR TAMBÉM A LISTA DE DEFENSORES)
        if enemies:
            if self.active and not self.effect_applied:
                self.apply_effect(enemies)
                self.effect_applied = True
                
            self.current_duration -= GameSpeed.get_instance().current_multiplier
            if self.current_duration <= 0:
                self.active = False
            return self.active
        elif defenders:
            if self.active and not self.effect_aplied:
                self.apply_effect(defenders)
                self.effect_applied = True

            self.current_duration -= GameSpeed.get_instance().current_multiplier
            if self.current_duration <= 0:
                self.active = False
            return self.active
            
    def draw(self, screen):
        if self.active:
            # Calcula a opacidade baseada no tempo restante
            opacity = int((self.current_duration / self.duration) * 100)
            surface = pygame.Surface((self.RADIUS * 2, self.RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.COLOR, opacity), (self.RADIUS, self.RADIUS), self.RADIUS)
            screen.blit(surface, (int(self.x - self.RADIUS), int(self.y - self.RADIUS)))
            
    def affect_enemies(self, enemies):
        affected = []
        for enemy in enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= self.RADIUS:
                # Verifica se o inimigo está protegido por uma aura de imunidade
                is_immune = False
                for potential_boss in enemies:
                    if hasattr(potential_boss, 'get_enemies_in_immunity_range') and potential_boss.is_immunized:
                        immune_enemies = potential_boss.get_enemies_in_immunity_range(enemies)
                        if enemy in immune_enemies:
                            is_immune = True
                            break
                
                if not is_immune:
                    affected.append(enemy)
        return affected
    
    def affect_defenders(self, defenders):
        affected = []
        for defender in defenders:
            dx = defender.x - self.x
            dy = defender.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= self.RADIUS:
                affected.append(defender)
        return affected
        
    def apply_effect(self, enemies):
        """Método base para aplicar o efeito do feitiço"""
        pass

class DamageSpell(Spell):
    COST = 0
    RADIUS = 100
    COLOR = (255, 50, 50)  # Vermelho
    NAME = "Explosão"
    DAMAGE = 250
    COOLDOWN = 3600  # 1 minuto de cooldown
    UPGRADE_COSTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Custo em orbes para cada nível
    DAMAGE_INCREASE_PERCENT = 0.2  # 20% de aumento de dano por nível
    MAX_LEVEL = 10

    def __init__(self, x, y, wave_manager=None):
        super().__init__(x, y)
        self.duration = 30  # 0.5 segundos
        self.current_duration = self.duration
        self.killed_enemies = []  # Lista para controlar inimigos mortos
        self.level = 1  # Nível atual do feitiço
        
    def get_damage(self):
        """Retorna o dano atual baseado no nível"""
        damage = self.DAMAGE
        for _ in range(self.level - 1):
            damage *= (1 + self.DAMAGE_INCREASE_PERCENT)
        return damage
        
    def get_cooldown(self):
        """Retorna o cooldown atual baseado no nível"""
        return self.COOLDOWN
        
    def update(self, enemies):
        """Atualiza o feitiço e retorna True se ainda está ativo"""
        if self.active and not self.effect_applied:
            affected = self.affect_enemies(enemies)
            for enemy in affected[:]:
                damage = self.get_damage()
                damage_result = enemy.take_damage(damage)
                
                if damage_result:  # Se o inimigo morreu
                    self.killed_enemies.append(enemy)  # Adiciona à lista de mortos
            
            self.effect_applied = True
            if self.killed_enemies:  # Se matou algum inimigo
                return "died"  # Retorna died apenas uma vez
            
        self.current_duration -= GameSpeed.get_instance().current_multiplier
        if self.current_duration <= 0:
            self.active = False
            return False
        return self.active
        
    def draw(self, screen):
        if self.active:
            # Calcula a opacidade baseada no tempo restante
            opacity = int((self.current_duration / self.duration) * 100)
            surface = pygame.Surface((self.RADIUS * 2, self.RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.COLOR, opacity), (self.RADIUS, self.RADIUS), self.RADIUS)
            screen.blit(surface, (int(self.x - self.RADIUS), int(self.y - self.RADIUS)))
            
    def apply_effect(self, enemies):
        """Aplica dano instantâneo em área"""
        affected = self.affect_enemies(enemies)
        for enemy in affected[:]:  # Usa uma cópia da lista para poder modificá-la
            damage = self.get_damage()
            if enemy.take_damage(damage):  # Se o inimigo morreu
                self.killed_enemies.append(enemy)  # Adiciona à lista de mortos
                
        if self.killed_enemies:  # Se matou algum inimigo
            return "died"  # Retorna died apenas uma vez

class FreezeSpell(Spell):
    COST = 0
    RADIUS = 150
    COLOR = (50, 150, 255)  # Azul claro
    NAME = "Gelo"
    FREEZE_DURATION = 90  # 1.5 segundos
    COOLDOWN = 3600  # 1 minuto de cooldown
    UPGRADE_COSTS = [2, 4, 6, 8, 10]  # Custo em orbes para cada nível
    DURATION_INCREASE = 30  # Aumento da duração por nível (0.5 segundos)
    MAX_LEVEL = 5
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = 30  # 0.5 segundos
        self.current_duration = self.duration
        self.level = 1  # Nível atual do feitiço
        
    def get_freeze_duration(self):
        """Retorna a duração do congelamento baseado no nível"""
        return self.FREEZE_DURATION + (self.level - 1) * self.DURATION_INCREASE
        
    def get_cooldown(self):
        """Retorna o cooldown atual baseado no nível"""
        return self.COOLDOWN
        
    def apply_effect(self, enemies):
        """Aplica efeito de congelamento em área"""
        affected = self.affect_enemies(enemies)
        for enemy in affected:
            if not isinstance(enemy, TankEnemy):  # Tanques são imunes ao congelamento
                enemy.apply_freeze(self.get_freeze_duration())

class SlowSpell(Spell):
    COST = 0
    RADIUS = 180
    COLOR = (30, 180, 30)  # Verde
    NAME = "Lentidão"
    SLOW_DURATION = 90  # 1.5 segundos
    COOLDOWN = 3600  # 1 minuto de cooldown
    UPGRADE_COSTS = [2, 4, 6, 8, 10]  # Custo em orbes para cada nível
    DURATION_INCREASE = 30  # Aumento da duração por nível (0.5 segundos)
    MAX_LEVEL = 5
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = 30  # 0.5 segundos
        self.current_duration = self.duration
        self.level = 1  # Nível atual do feitiço
        
    def get_slow_duration(self):
        """Retorna a duração do congelamento baseado no nível"""
        return self.SLOW_DURATION + (self.level - 1) * self.DURATION_INCREASE
        
    def get_cooldown(self):
        """Retorna o cooldown atual baseado no nível"""
        return self.COOLDOWN
        
    def apply_effect(self, enemies):
        """Aplica efeito de congelamento em área"""
        affected = self.affect_enemies(enemies)
        for enemy in affected:
            if not isinstance(enemy, TankEnemy):  # Tanques são imunes ao slow
                enemy.apply_slow(self.get_slow_duration())

class DotSpell(Spell):
    COST = 0
    RADIUS = 200
    COLOR = (255, 165, 0)  # Laranja
    NAME = "Fogo"
    DOT_DAMAGE = 30  # Dano por segundo
    DOT_DURATION = 300  # 5 segundos
    COOLDOWN = 2700  # 45 segundos de cooldown
    UPGRADE_COSTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Custo em orbes para cada nível
    DAMAGE_INCREASE_PERCENT = 0.10  # 10% de aumento de dano por nível
    DURATION_INCREASE = 60  # Aumento da duração por nível (1 segundo) (LOGICA NO CÓDIGO -> A CADA 5 NÍVEIS)
    MAX_LEVEL = 10
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = 60  # 1 segundo
        self.current_duration = self.duration
        self.level = 1  # Nível atual do feitiço
        self.killed_enemies = []  # Lista para controlar inimigos mortos
        
    def get_dot_damage(self):
        """Retorna o dano por segundo baseado no nível"""
        damage = self.DOT_DAMAGE
        for _ in range(self.level - 1):
            damage *= (1 + self.DAMAGE_INCREASE_PERCENT)
        return damage
        
    def get_dot_duration(self):
        """Retorna a duração do DoT baseado no nível"""
        extra_duration = (self.level) // 5 * self.DURATION_INCREASE  # +1 segundo a cada 5 níveis
        return self.DOT_DURATION + extra_duration
        
    def get_cooldown(self):
        """Retorna o cooldown atual baseado no nível"""
        return self.COOLDOWN
        
    def update(self, enemies):
        """Atualiza o feitiço e retorna True se ainda está ativo"""
        if self.active and not self.effect_applied:
            self.apply_effect(enemies)
            self.effect_applied = True
            
        self.current_duration -= GameSpeed.get_instance().current_multiplier
        if self.current_duration <= 0:
            self.active = False
            return False
        return self.active
        
    def apply_effect(self, enemies):
        """Aplica dano ao longo do tempo em área"""
        affected = self.affect_enemies(enemies)
        for enemy in affected:
            if not isinstance(enemy, SpeedEnemy):  # Inimigos velozes são imunes ao DoT
                if isinstance(enemy, ArmoredEnemy):
                    # Inimigos blindados recebem menos dano
                    enemy.apply_dot(self.get_dot_damage() * (1 - enemy.damage_reduction), self.get_dot_duration())
                else:
                    enemy.apply_dot(self.get_dot_damage(), self.get_dot_duration())

class SpeedSpell(Spell):
    COST = 0
    RADIUS = 100
    COLOR = (250, 60, 250)  # Rosa-claro
    NAME = "Fúria"
    COOLDOWN = 2700  # 45 segundos de cooldown
    UPGRADE_COSTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Custo em orbes para cada nível
    VELOCITY_DURATION = 180 # Duração do efeito (3 segundos)
    VELOCITY_BOOST = 0.55 # 55% de boost de velocidade
    VELOCITY_INCREASE_PERCENT = 0.05  # 5% de aumento de dano por nível
    DURATION_INCREASE = 30  # Aumento da duração por nível (0.5 segundos)  (LOGICA NO CÓDIGO -> A CADA 2 NÍVEIS)
    MAX_LEVEL = 10
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = 60  # 1 segundo
        self.current_duration = self.duration
        self.level = 1  # Nível atual do feitiço
        self.killed_enemies = []  # Lista para controlar inimigos mortos
    
    def get_velocity(self):
        """Retorna o buff de velocidade baseado no nível"""
        velocity_buff = self.VELOCITY_BOOST
        for _ in range(self.level - 1):
            velocity_buff += self.VELOCITY_INCREASE_PERCENT
        return velocity_buff
        
    def get_velocity_duration(self):
        """Retorna a duração do buff de velocidade baseado no nível"""
        extra_duration = (self.level) // 2 * self.DURATION_INCREASE  # +0.5 segundos a cada 2 níveis
        return self.VELOCITY_DURATION + extra_duration
        
    def get_cooldown(self):
        """Retorna o cooldown atual baseado no nível"""
        return self.COOLDOWN
        
    def update(self, defenders):
        """Atualiza o feitiço e retorna True se ainda está ativo"""
        if self.active and not self.effect_applied:
            self.apply_effect(defenders)
            self.effect_applied = True
            
        self.current_duration -= GameSpeed.get_instance().current_multiplier
        if self.current_duration <= 0:
            self.active = False
            return False
        return self.active
        
    def apply_effect(self, defenders):
        """Aplica dano ao longo do tempo em área"""
        affected = self.affect_defenders(defenders)
        for defender in affected:
            defender.apply_speed(self.get_velocity(), self.get_velocity_duration()) 

class SpellButton:
    def __init__(self, spell_class, x_pos):
        self.width = 50
        self.height = 50
        self.color = spell_class.COLOR
        self.rect = pygame.Rect(x_pos, 600, self.width, self.height)
        self.selected = False
        self.spell_class = spell_class
        self.radius = spell_class.RADIUS
        self.cooldown_timer = 0
        self.level = 1  # Nível atual do feitiço
        
    def get_current_stats(self):
        """Retorna as estatísticas atuais do feitiço baseado no nível"""
        if isinstance(self.spell_class, DamageSpell):
            damage = self.spell_class.DAMAGE * (1 + (self.level - 1) * self.spell_class.DAMAGE_INCREASE_PERCENT)
            cooldown = self.spell_class.COOLDOWN - (self.level - 1)
            return {
                "Dano": damage,
                "Recarga": f"{cooldown // 60}s"
            }
        elif isinstance(self.spell_class, FreezeSpell):
            duration = (self.spell_class.FREEZE_DURATION + (self.level - 1) * self.spell_class.DURATION_INCREASE) / 60
            cooldown = self.spell_class.COOLDOWN - (self.level - 1)
            return {
                "Duração": f"{duration:.1f}s",
                "Recarga": f"{cooldown // 60}s"
            }
        elif isinstance(self.spell_class, DotSpell):
            damage = self.spell_class.DOT_DAMAGE * (1 + (self.level - 1) * self.spell_class.DAMAGE_INCREASE_PERCENT)
            cooldown = self.spell_class.COOLDOWN - (self.level - 1)
            return {
                "DPS": damage,
                "Recarga": f"{cooldown // 60}s"
            }
        return {}  # Retorna um dicionário vazio se não for nenhum dos tipos conhecidos
            
    def get_next_level_stats(self):
        """Retorna as estatísticas do próximo nível do feitiço"""
        if self.level >= self.spell_class.MAX_LEVEL:
            return None
            
        if isinstance(self.spell_class, DamageSpell):
            damage = self.spell_class.get_damage() * (1 + self.level * self.spell_class.DAMAGE_INCREASE_PERCENT)
            cooldown = self.spell_class.get_cooldown()
            return {
                "Dano": damage,
                "Recarga": f"{cooldown // 60}s"
            }
        elif isinstance(self.spell_class, FreezeSpell):
            duration = (self.spell_class.get_freeze_duration()) / 60
            cooldown = self.spell_class.get_cooldown()
            return {
                "Duração": f"{duration:.1f}s",
                "Recarga": f"{cooldown // 60}s"
            }
        elif isinstance(self.spell_class, SlowSpell):
            duration = (self.spell_class.get_slow_duration()) / 60
            cooldown = self.spell_class.get_cooldown()
            return {
                "Duração": f"{duration:.1f}s",
                "Recarga": f"{cooldown // 60}s"
            }
        elif isinstance(self.spell_class, SpeedSpell):
            duration = (self.spell_class.get_velocity_duration()) / 60
            buff = self.spell_class.get_velocity()
            return {
                "Duração": f"{duration:.1f}s",
                "Incremento": f"{buff * 100}%"
            }
        elif isinstance(self.spell_class, DotSpell):
            damage = self.spell_class.get_dot_damage() * (1 + self.level * self.spell_class.DAMAGE_INCREASE_PERCENT)
            cooldown = self.spell_class.get_cooldown()
            return {
                "DPS": damage,
                "Recarga": f"{cooldown // 60}s"
            }
            
    def get_upgrade_cost(self):
        """Retorna o custo da próxima melhoria em orbes"""
        if self.level > self.spell_class.MAX_LEVEL:
            return None
        return self.spell_class.UPGRADE_COSTS[self.level - 1]
        
    def can_upgrade(self, orbes):
        """Verifica se pode melhorar o feitiço"""
        if self.level >= self.spell_class.MAX_LEVEL:
            return False
        return orbes >= self.get_upgrade_cost()
        
    def upgrade(self):
        """Melhora o feitiço"""
        if self.level < self.spell_class.MAX_LEVEL:
            self.level += 1
            return True
        return False
        
    def draw(self, screen, gold):
        # Desenha o fundo do botão
        button_color = self.color if self.cooldown_timer <= 0 else (100, 100, 100)
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        
        # Desenha o círculo do feitiço
        inner_size = 35
        pygame.draw.circle(screen, button_color,
                         (self.rect.centerx, self.rect.centery),
                         inner_size // 2)
        
        # Desenha borda quando selecionado
        if self.selected:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
            
        # Se estiver em cooldown, desenha o tempo restante
        if self.cooldown_timer > 0:
            font = pygame.font.Font(None, 28)
            seconds = self.cooldown_timer // 60  # Converte frames para segundos
            text = font.render(str(seconds), True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom - 25))
            screen.blit(text, text_rect)
            
        # Desenha o nome do feitiço
        font = pygame.font.Font(None, 22)
        text = font.render(self.spell_class.NAME, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.top - 18))
        screen.blit(text, text_rect)
        
    def update(self):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= GameSpeed.get_instance().current_multiplier
        
    def handle_click(self, pos, gold):
        if self.rect.collidepoint(pos) and self.cooldown_timer <= 0:
            self.selected = not self.selected
            return True
        return False
        
    def start_cooldown(self):
        """Inicia o cooldown baseado no nível atual"""
        if isinstance(self.spell_class, (DamageSpell, FreezeSpell, DotSpell, SlowSpell)):
            cooldown = self.spell_class.get_cooldown()
            self.cooldown_timer = cooldown
        else:
            self.cooldown_timer = self.spell_class.COOLDOWN
            self.selected = False 