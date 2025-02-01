import pygame
import math
from enemy import TankEnemy, ArmoredEnemy, SpeedEnemy, HealerEnemy

class Spell:
    COST = 100  # Custo base
    RADIUS = 100  # Raio base
    COLOR = (255, 255, 255)  # Cor base
    NAME = "Feitiço Base"
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.duration = 60  # 1 segundo em frames
        self.current_duration = self.duration
        self.active = True
        self.effect_applied = False  # Flag para controlar se o efeito já foi aplicado
        
    def update(self, enemies):
        if self.active and not self.effect_applied:
            self.apply_effect(enemies)
            self.effect_applied = True
            
        self.current_duration -= 1
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
                affected.append(enemy)
        return affected
        
    def apply_effect(self, enemies):
        """Método base para aplicar o efeito do feitiço"""
        pass

class DamageSpell(Spell):
    COST = 150
    RADIUS = 100
    COLOR = (255, 50, 50)  # Vermelho
    NAME = "Explosão"
    DAMAGE = 200
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = 30  # 0.5 segundos
        self.current_duration = self.duration
        
    def update(self, enemies):
        """Atualiza o feitiço e retorna True se ainda está ativo"""
        if self.active and not self.effect_applied:
            affected = self.affect_enemies(enemies)
            for enemy in affected[:]:
                damage = self.DAMAGE * 0.7 if isinstance(enemy, ArmoredEnemy) else self.DAMAGE
                damage_result = enemy.take_damage(damage)
                
                if damage_result == "split":
                    return "split"  # Retorna split para o inimigo que se divide
                elif damage_result:  # Se o inimigo morreu
                    return "died"  # Retorna died para dar ouro
            self.effect_applied = True
            
        self.current_duration -= 1
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
            
    def apply_effect(self, enemies):
        """Aplica dano instantâneo em área"""
        affected = self.affect_enemies(enemies)
        for enemy in affected[:]:  # Usa uma cópia da lista para poder modificá-la
            damage = self.DAMAGE * 0.7 if isinstance(enemy, ArmoredEnemy) else self.DAMAGE
            if enemy.take_damage(damage):  # Se o inimigo morreu
                if enemy in enemies:
                    enemies.remove(enemy)
                    return "died"  # Retorna "died" assim como o DoT faz

class FreezeSpell(Spell):
    COST = 100
    RADIUS = 150
    COLOR = (50, 150, 255)  # Azul claro
    NAME = "Congelar"
    FREEZE_DURATION = 90  # 1.5 segundos
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = 30  # 0.5 segundos
        self.current_duration = self.duration
        
    def apply_effect(self, enemies):
        """Aplica efeito de lentidão em área"""
        affected = self.affect_enemies(enemies)
        for enemy in affected:
            if not isinstance(enemy, TankEnemy):  # Tanques são imunes ao congelamento
                enemy.apply_slow(self.FREEZE_DURATION)

class DotSpell(Spell):
    COST = 125
    RADIUS = 200
    COLOR = (255, 165, 0)  # Laranja
    NAME = "Veneno"
    DOT_DAMAGE = 20
    DOT_DURATION = 300  # 5 segundos
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = 30  # 0.5 segundos
        self.current_duration = self.duration
        
    def apply_effect(self, enemies):
        """Aplica dano ao longo do tempo em área"""
        affected = self.affect_enemies(enemies)
        for enemy in affected:
            if not isinstance(enemy, SpeedEnemy):  # Inimigos velozes são imunes ao DoT
                if isinstance(enemy, ArmoredEnemy):
                    # Inimigos blindados recebem 30% menos dano
                    enemy.apply_dot(self.DOT_DAMAGE * 0.7, self.DOT_DURATION)
                else:
                    enemy.apply_dot(self.DOT_DAMAGE, self.DOT_DURATION)

class SpellButton:
    def __init__(self, spell_class, x_pos):
        self.width = 50  # Botões menores que os de defensores
        self.height = 50
        self.color = spell_class.COLOR
        self.rect = pygame.Rect(x_pos, 610, self.width, self.height)  # Posicionado acima da loja
        self.selected = False
        self.cost = spell_class.COST
        self.spell_class = spell_class
        self.radius = spell_class.RADIUS
        
    def draw(self, screen, gold):
        # Desenha o fundo do botão
        button_color = self.color if gold >= self.cost else (100, 100, 100)
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        
        # Desenha o círculo do feitiço
        inner_size = 30
        pygame.draw.circle(screen, button_color,
                         (self.rect.centerx, self.rect.centery),
                         inner_size // 2)
        
        # Desenha borda quando selecionado
        if self.selected:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
            
        # Desenha o custo
        font = pygame.font.Font(None, 24)
        text_color = (255, 215, 0) if gold >= self.cost else (255, 0, 0)
        text = font.render(str(self.cost), True, text_color)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom + 10))
        screen.blit(text, text_rect)
        
    def handle_click(self, pos, gold):
        if self.rect.collidepoint(pos) and gold >= self.cost:
            self.selected = not self.selected
            return True
        return False 