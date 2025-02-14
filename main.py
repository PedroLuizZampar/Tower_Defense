import pygame
import math
import os
import sys
import random
from enemy import spawn_random_enemy, Enemy, SpeedEnemy, TankEnemy, ArmoredEnemy, HealerEnemy, FreezeAuraEnemy, RageEnemy, StealthEnemy, ImmunityBoss, SpeedBoss
from defender import Defender, BlueDefender, RedDefender, YellowDefender, DefenderButton, BasicDefender, GreenDefender, OrangeDefender, PurpleDefender
from wave_manager import WaveManager
from base import Base, SkipButton
from upgrade_menu import UpgradeMenu
from spell import DamageSpell, FreezeSpell, DotSpell, SpellButton
from mission_manager import MissionManager

# Inicialização do Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 1000  # Removido menu lateral
WAVE_MENU_HEIGHT = 100  # Altura do menu superior
SCREEN_HEIGHT = 650  # Altura total reduzida em 100px
GAME_HEIGHT = SCREEN_HEIGHT - WAVE_MENU_HEIGHT  # Altura do jogo ajustada
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)

# Carrega o background
background = pygame.image.load(os.path.join('assets', 'background.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH, GAME_HEIGHT))

# Definição do caminho (waypoints)
PATH = [
    (0, 400),      # Início
    (165, 400),    # Primeiro ponto
    (165, 235),    # Subida 1
    (365, 235),    # Caminho reto superior
    (365, 460),    # Descida
    (630, 460),    # Caminho reto inferior
    (630, 350),    # Subida 2
    (SCREEN_WIDTH, 350)  # Final (ajustado para o novo menu lateral)
]

def is_point_on_path(x, y, path, margin=30):
    """Verifica se um ponto está próximo do caminho"""
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        
        # Calcula a distância do ponto até o segmento de linha
        line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_length == 0:
            continue
            
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_length**2)))
        
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        distance = math.sqrt((x - proj_x)**2 + (y - proj_y)**2)
        
        if distance < margin:
            return True
            
    return False

def draw_wave_menu(screen, wave_manager, skip_button):
    """Desenha o menu superior com informações da onda"""
    # Desenha o fundo do menu
    menu_rect = pygame.Rect(0, 0, SCREEN_WIDTH, WAVE_MENU_HEIGHT)
    pygame.draw.rect(screen, MENU_GRAY, menu_rect)
    
    # Desenha uma linha separadora
    pygame.draw.line(screen, WHITE, (0, WAVE_MENU_HEIGHT), (SCREEN_WIDTH, WAVE_MENU_HEIGHT), 2)
    
    # Título "ONDAS"
    font = pygame.font.Font(None, 36)
    title = font.render("ONDAS", True, WHITE)
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, y=20)
    screen.blit(title, title_rect)
    
    # Status da onda atual
    wave_text = font.render(wave_manager.get_wave_status(), True, WHITE)
    wave_rect = wave_text.get_rect(centerx=SCREEN_WIDTH//2, y=60)
    screen.blit(wave_text, wave_rect)
    
    # Desenha o botão de pular no canto superior direito
    skip_button.rect.x = SCREEN_WIDTH - skip_button.width - 10
    skip_button.rect.y = 10
    skip_button.draw(screen, wave_manager.wave_active)

def is_valid_placement(x, y, path, game_height, defenders, is_spell=False):
    """Verifica se é uma posição válida para colocar um defensor ou feitiço"""
    # Não pode colocar no menu lateral
    if x <= 0:
        return False
    
    # Não pode colocar no menu superior
    if y <= WAVE_MENU_HEIGHT:
        return False
    
    if x < 200 and y > SCREEN_HEIGHT - 80:
        return False
    
    # Se for um defensor, verifica regras específicas
    if not is_spell:
        # Verifica pontos em um raio de 20px ao redor do mouse
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            check_x = x + 25 * math.cos(rad)
            check_y = y + 25 * math.sin(rad)
            
            # Não pode colocar no caminho
            if is_point_on_path(check_x, check_y, path):
                return False
        
        # Não pode colocar muito próximo de outros defensores
        if Defender.is_too_close(x, y, defenders):
            return False
    
    return True
def draw_enemy_path(screen, path):
    """Desenha o caminho dos inimigos com uma cor semi-transparente"""
    pass  # Removida a visualização do caminho

class EnemyShopMenu:
    def __init__(self):
        self.width = 250
        self.height = SCREEN_HEIGHT - WAVE_MENU_HEIGHT
        self.is_expanded = False
        self.header_rect = None
        self.current_page = 0  # Current page index
        self.enemies_per_page = 5  # Number of enemies per page
        self.prev_button_rect = None  # Rectangle for previous page button
        self.next_button_rect = None  # Rectangle for next page button
        self.enemies = [Enemy, TankEnemy, SpeedEnemy, ArmoredEnemy, HealerEnemy, FreezeAuraEnemy, RageEnemy, StealthEnemy]
        
    def draw(self, screen, wave_manager):
        # Desenha o cabeçalho (sempre visível)
        header_width = 40
        header_height = 100
        header_x = SCREEN_WIDTH - header_width
        self.header_rect = pygame.Rect(header_x, WAVE_MENU_HEIGHT + 98, header_width, header_height)
        
        # Se expandido, desenha o resto do menu
        if self.is_expanded:
            panel_rect = pygame.Rect(SCREEN_WIDTH - self.width - header_width, WAVE_MENU_HEIGHT, 
                                   self.width, self.height)
            pygame.draw.rect(screen, MENU_GRAY, panel_rect)
            pygame.draw.rect(screen, WHITE, panel_rect, 2)
            
            font = pygame.font.Font(None, 28)
            text = font.render("INIMIGOS", True, WHITE)
            text_rect = text.get_rect(center=(panel_rect.centerx, WAVE_MENU_HEIGHT + 25))
            screen.blit(text, text_rect)
            
            # Draw only the enemies for the current page
            start_index = self.current_page * self.enemies_per_page
            end_index = min(start_index + self.enemies_per_page, len(self.enemies))
            
            y_offset = WAVE_MENU_HEIGHT + 45
            font = pygame.font.Font(None, 20)
            font_title = pygame.font.Font(None, 24)
            
            for enemy_class in self.enemies[start_index:end_index]:
                # Fundo do card do inimigo
                card_height = 90
                card_rect = pygame.Rect(panel_rect.x + 10, y_offset, self.width - 20, card_height)
                pygame.draw.rect(screen, WHITE, card_rect, 1)
                
                # Nome do inimigo
                name_text = font_title.render(enemy_class.NAME, True, WHITE)
                name_rect = name_text.get_rect(x=card_rect.x + 10, y=y_offset + 10)
                screen.blit(name_text, name_rect)
                
                # Ícone do inimigo
                pygame.draw.circle(screen, enemy_class.COLOR,
                                 (card_rect.x + 30, y_offset + 50),
                                 12)
                
                # Estatísticas
                base_health = round(enemy_class.BASE_HEALTH * wave_manager.get_health_increase(), 1)
                health_text = font.render(f"Vida: {int(base_health)}", True, WHITE)
                screen.blit(health_text, (card_rect.x + 60, y_offset + 35))
                
                speed_text = font.render(f"Velocidade: {enemy_class.BASE_SPEED}", True, WHITE)
                screen.blit(speed_text, (card_rect.x + 60, y_offset + 50))
                
                # Características especiais
                special_text = None
                if enemy_class == TankEnemy:
                    special_text = "Imune a Freeze e Slow"
                elif enemy_class == SpeedEnemy:
                    special_text = "Imune a Queimaduras"
                elif enemy_class == ArmoredEnemy:
                    special_text = "-30% Dano Recebido"
                elif enemy_class == HealerEnemy:
                    special_text = "Cura Aliados Próximos"
                elif enemy_class == FreezeAuraEnemy:
                    special_text = "Congela Torres ao Morrer"
                elif enemy_class == RageEnemy:
                    special_text = "Acelera ao Perder Vida"
                elif enemy_class == StealthEnemy:
                    special_text = "Fica Invisível"
                    
                if special_text:
                    spec_text = font.render(special_text, True, (50, 255, 50))
                    screen.blit(spec_text, (card_rect.x + 60, y_offset + 65))
                
                y_offset += card_height + 5
            
            # Draw pagination controls
            button_width = 40
            button_height = 30
            spacing = 150
            start_x = panel_rect.right - 240
            button_y = panel_rect.top + 10
            
            font_back_next = pygame.font.Font(None, 35)
            
            # Previous page button
            self.prev_button_rect = pygame.Rect(start_x, button_y, button_width, button_height)
            prev_color = MENU_LIGHT_GRAY if self.current_page > 0 else (60, 60, 60)
            pygame.draw.rect(screen, prev_color, self.prev_button_rect)
            pygame.draw.rect(screen, WHITE, self.prev_button_rect, 1)
            
            prev_text = font_back_next.render("<", True, WHITE if self.current_page > 0 else (150, 150, 150))
            prev_rect = prev_text.get_rect(center=self.prev_button_rect.center)
            screen.blit(prev_text, prev_rect)
            
            # Next page button
            self.next_button_rect = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
            next_color = MENU_LIGHT_GRAY if end_index < len(self.enemies) else (60, 60, 60)
            pygame.draw.rect(screen, next_color, self.next_button_rect)
            pygame.draw.rect(screen, WHITE, self.next_button_rect, 1)
            
            next_text = font_back_next.render(">", True, WHITE if end_index < len(self.enemies) else (150, 150, 150))
            next_rect = next_text.get_rect(center=self.next_button_rect.center)
            screen.blit(next_text, next_rect)
            
            # Page indicator
            total_pages = (len(self.enemies) + self.enemies_per_page - 1) // self.enemies_per_page
            page_text = font.render(f"{self.current_page + 1}/{total_pages}", True, WHITE)
            page_rect = page_text.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 10)
            screen.blit(page_text, page_rect)
        
        # Sempre desenha o botão da aba
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        # Desenha o ícone na vertical
        font = pygame.font.Font(None, 18)
        text = font.render("Inimigos", True, WHITE)
        
        # Rotaciona o texto em 90 graus
        text_vertical = pygame.transform.rotate(text, 270)
        
        # Obtém a nova posição central para manter alinhado
        text_rect = text_vertical.get_rect(center=self.header_rect.center)
        
        # Desenha na tela
        screen.blit(text_vertical, text_rect)
        
    def handle_click(self, pos):
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            return True
            
        if self.is_expanded:
            # Handle pagination button clicks
            if self.prev_button_rect and self.prev_button_rect.collidepoint(pos) and self.current_page > 0:
                self.current_page -= 1
                return True
                
            if self.next_button_rect and self.next_button_rect.collidepoint(pos):
                next_page_start = (self.current_page + 1) * self.enemies_per_page
                if next_page_start < len(self.enemies):
                    self.current_page += 1
                    return True
                    
        return False

class DefenderShopMenu:
    def __init__(self, mission_manager):
        self.width = 250
        self.height = SCREEN_HEIGHT - WAVE_MENU_HEIGHT
        self.is_expanded = False
        self.header_rect = None
        self.mission_manager = mission_manager
        self.selected_button = None
        self.current_page = 0  # Current page index
        self.defenders_per_page = 5  # Number of defenders per page
        self.prev_button_rect = None  # Rectangle for previous page button
        self.next_button_rect = None  # Rectangle for next page button
        self.defender_buttons = []  # Initialize empty list first
        self.setup_buttons()  # Then call setup_buttons
        
    def setup_buttons(self):
        button_spacing = 90
        start_y = WAVE_MENU_HEIGHT + 30
        x_pos = SCREEN_WIDTH - self.width - 30
        
        self.defender_buttons = [
            DefenderButton(BasicDefender, x_pos, self.mission_manager),
            DefenderButton(RedDefender, x_pos, self.mission_manager),
            DefenderButton(YellowDefender, x_pos, self.mission_manager),
            DefenderButton(GreenDefender, x_pos, self.mission_manager),
            DefenderButton(BlueDefender, x_pos, self.mission_manager),
            DefenderButton(OrangeDefender, x_pos, self.mission_manager),
            DefenderButton(PurpleDefender, x_pos, self.mission_manager)
        ]
        
        # Update positions based on current page
        self.update_button_positions()
        
    def update_button_positions(self):
        button_spacing = 90
        start_y = WAVE_MENU_HEIGHT + 30
        start_index = self.current_page * self.defenders_per_page
        end_index = min(start_index + self.defenders_per_page, len(self.defender_buttons))
        
        for i, button in enumerate(self.defender_buttons[start_index:end_index], 0):
            button.rect.y = start_y + (i * button_spacing) + 15
    
    def draw(self, screen, gold, selected_button=None):
        header_width = 40
        header_height = 100
        header_x = SCREEN_WIDTH - header_width
        self.header_rect = pygame.Rect(header_x, WAVE_MENU_HEIGHT, header_width, header_height)
        
        if self.is_expanded:
            panel_rect = pygame.Rect(SCREEN_WIDTH - self.width - header_width, WAVE_MENU_HEIGHT, 
                                   self.width, self.height)
            pygame.draw.rect(screen, MENU_GRAY, panel_rect)
            pygame.draw.rect(screen, WHITE, panel_rect, 2)
            
            font = pygame.font.Font(None, 28)
            text = font.render("DEFENSORES", True, WHITE)
            text_rect = text.get_rect(center=(panel_rect.centerx, WAVE_MENU_HEIGHT + 25))
            screen.blit(text, text_rect)
            
            # Draw only the defenders for the current page
            start_index = self.current_page * self.defenders_per_page
            end_index = min(start_index + self.defenders_per_page, len(self.defender_buttons))
            
            y_offset = WAVE_MENU_HEIGHT + 45
            font = pygame.font.Font(None, 20)
            font_title = pygame.font.Font(None, 24)
            
            for i, button in enumerate(self.defender_buttons[start_index:end_index]):
                # Fundo do card do defensor
                card_height = 90
                card_rect = pygame.Rect(panel_rect.x + 10, y_offset, self.width - 20, card_height)
                pygame.draw.rect(screen, (60, 60, 60), card_rect)
                pygame.draw.rect(screen, WHITE, card_rect, 1)
                
                # Nome do defensor
                name_text = font_title.render(button.defender_class.NAME, True, WHITE)
                name_rect = name_text.get_rect(x=card_rect.x + 10, y=y_offset + 10)
                screen.blit(name_text, name_rect)
                
                # Ícone do defensor (agora como retângulo)
                icon_size = 24  # Tamanho do retângulo
                icon_rect = pygame.Rect(card_rect.x + 18, y_offset + 38, icon_size, icon_size)
                pygame.draw.rect(screen, button.defender_class.COLOR, icon_rect)
                pygame.draw.rect(screen, WHITE, icon_rect, 1)  # Borda branca
                
                # Dano e DPS
                damage_text = font.render(f"Dano: {button.defender_class.BASE_DAMAGE}         DPS: {round(button.defender_class.BASE_DAMAGE * (60 / button.defender_class.BASE_ATTACK_COOLDOWN), 1)}", True, WHITE)
                screen.blit(damage_text, (card_rect.x + 60, y_offset + 35))

                # Range e Hits para Ativação
                if button.defender_class.HITS_TO_ACTIVATE != 0:
                    range_text = font.render(f"Range: {button.defender_class.RANGE}     Ativar: {button.defender_class.HITS_TO_ACTIVATE}", True, WHITE)
                else:
                    range_text = font.render(f"Range: {button.defender_class.RANGE}", True, WHITE)
                screen.blit(range_text, (card_rect.x + 60, y_offset + 50))
                
                # Habilidade especial
                special_text = None
                if button.defender_class == BlueDefender:
                    special_text = "Congela Inimigos"
                elif button.defender_class == RedDefender:
                    special_text = "Aplica Queimaduras"
                elif button.defender_class == YellowDefender:
                    special_text = "Aumenta Dano Aliado"
                elif button.defender_class == GreenDefender:
                    special_text = "Desacelera Inimigos"
                elif button.defender_class == OrangeDefender:
                    special_text = "Atira em 2 Alvos"
                elif button.defender_class == PurpleDefender:
                    special_text = "Aplica Fraqueza"
                
                if special_text:
                    spec_text = font.render(special_text, True, (50, 255, 50))
                    screen.blit(spec_text, (card_rect.x + 60, y_offset + 65))
                
                # Desenha o botão
                button.rect.y = y_offset
                button.draw(screen, gold, 0)
                
                y_offset += card_height + 5
            
            # Draw pagination controls
            button_width = 40
            button_height = 30
            spacing = 150
            start_x = panel_rect.right - 240
            button_y = panel_rect.top + 10
            
            font_back_next = pygame.font.Font(None, 35)
            
            # Previous page button
            self.prev_button_rect = pygame.Rect(start_x, button_y, button_width, button_height)
            prev_color = MENU_LIGHT_GRAY if self.current_page > 0 else (60, 60, 60)
            pygame.draw.rect(screen, prev_color, self.prev_button_rect)
            pygame.draw.rect(screen, WHITE, self.prev_button_rect, 1)
            
            prev_text = font_back_next.render("<", True, WHITE if self.current_page > 0 else (150, 150, 150))
            prev_rect = prev_text.get_rect(center=self.prev_button_rect.center)
            screen.blit(prev_text, prev_rect)
            
            # Next page button
            self.next_button_rect = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
            next_color = MENU_LIGHT_GRAY if end_index < len(self.defender_buttons) else (60, 60, 60)
            pygame.draw.rect(screen, next_color, self.next_button_rect)
            pygame.draw.rect(screen, WHITE, self.next_button_rect, 1)
            
            next_text = font_back_next.render(">", True, WHITE if end_index < len(self.defender_buttons) else (150, 150, 150))
            next_rect = next_text.get_rect(center=self.next_button_rect.center)
            screen.blit(next_text, next_rect)
            
            # Page indicator
            total_pages = (len(self.defender_buttons) + self.defenders_per_page - 1) // self.defenders_per_page
            page_text = font.render(f"{self.current_page + 1}/{total_pages}", True, WHITE)
            page_rect = page_text.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 10)
            screen.blit(page_text, page_rect)
        
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        font = pygame.font.Font(None, 18)
        text = font.render("Defensores", True, WHITE)
        text_vertical = pygame.transform.rotate(text, 270)
        text_rect = text_vertical.get_rect(center=self.header_rect.center)
        screen.blit(text_vertical, text_rect)
    
    def handle_click(self, pos, gold):
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            return None, True
            
        if self.is_expanded:
            # Handle pagination button clicks
            if self.prev_button_rect and self.prev_button_rect.collidepoint(pos) and self.current_page > 0:
                self.current_page -= 1
                self.update_button_positions()
                return None, False
                
            if self.next_button_rect and self.next_button_rect.collidepoint(pos):
                next_page_start = (self.current_page + 1) * self.defenders_per_page
                if next_page_start < len(self.defender_buttons):
                    self.current_page += 1
                    self.update_button_positions()
                    return None, False
            
            # Handle defender button clicks
            start_index = self.current_page * self.defenders_per_page
            end_index = min(start_index + self.defenders_per_page, len(self.defender_buttons))
            
            for button in self.defender_buttons[start_index:end_index]:
                if button.handle_click(pos, gold):
                    self.is_expanded = False  # Fecha o menu ao selecionar um defensor
                    return button, False
                    
        return None, False
    
class BossShopMenu:
    def __init__(self):
        self.width = 250
        self.height = SCREEN_HEIGHT - WAVE_MENU_HEIGHT
        self.is_expanded = False
        self.header_rect = None
        self.current_page = 0  # Current page index
        self.bosses_per_page = 2  # Number of bosses per page
        self.prev_button_rect = None  # Rectangle for previous page button
        self.next_button_rect = None  # Rectangle for next page button
        self.bosses = [
            {
                'class': ImmunityBoss,
                'wave': 10,
                'description1': 'Aplica imunidade em',
                'description2': 'inimigos próximos',
                'ability_duration': '2s',
                'ability_cooldown': '3s'
            },
            {
                'class': SpeedBoss,
                'wave': 20,
                'description1': 'Aumenta velocidade de',
                'description2': 'todos os inimigos',
                'ability_duration': '2s',
                'ability_cooldown': '5s'
            }
        ]
        
    def draw(self, screen, wave_manager):
        # Desenha o cabeçalho (sempre visível)
        header_width = 40
        header_height = 100
        header_x = SCREEN_WIDTH - header_width
        self.header_rect = pygame.Rect(header_x, WAVE_MENU_HEIGHT + 196, header_width, header_height)
        
        # Se expandido, desenha o resto do menu
        if self.is_expanded:
            panel_rect = pygame.Rect(SCREEN_WIDTH - self.width - header_width, WAVE_MENU_HEIGHT, 
                                   self.width, self.height)
            pygame.draw.rect(screen, MENU_GRAY, panel_rect)
            pygame.draw.rect(screen, WHITE, panel_rect, 2)
            
            font = pygame.font.Font(None, 28)
            text = font.render("CHEFÕES", True, WHITE)
            text_rect = text.get_rect(center=(panel_rect.centerx, WAVE_MENU_HEIGHT + 25))
            screen.blit(text, text_rect)
            
            # Draw only the bosses for the current page
            start_index = self.current_page * self.bosses_per_page
            end_index = min(start_index + self.bosses_per_page, len(self.bosses))
            
            y_offset = WAVE_MENU_HEIGHT + 45
            font = pygame.font.Font(None, 16)
            font_title = pygame.font.Font(None, 24)
            
            for boss_info in self.bosses[start_index:end_index]:
                boss_class = boss_info['class']
                # Fundo do card do chefão
                card_height = 100
                card_rect = pygame.Rect(panel_rect.x + 10, y_offset, self.width - 20, card_height)
                
                pygame.draw.rect(screen, (40, 40, 40), card_rect)
                pygame.draw.rect(screen, WHITE, card_rect, 1)
                
                # Nome do chefão
                name_text = font_title.render(boss_class.NAME, True, WHITE)
                name_rect = name_text.get_rect(x=card_rect.x + 10, y=y_offset + 10)
                screen.blit(name_text, name_rect)
                
                font_wave = pygame.font.Font(None, 20)
                # Onda de aparição
                wave_text = font_wave.render(f"Onda {boss_info['wave']}", True, WHITE)
                wave_rect = wave_text.get_rect(right=card_rect.right - 10, y=y_offset + 10)
                screen.blit(wave_text, wave_rect)
                
                # Ícone do chefão
                pygame.draw.circle(screen, boss_class.COLOR,
                                 (card_rect.x + 30, y_offset + 50),
                                 15)  # Raio maior para chefões
                
                # Estatísticas
                base_health = round(boss_class.BASE_HEALTH * wave_manager.get_health_increase(), 1)
                health_text = font.render(f"Vida: {int(base_health)} | Velocidade: {boss_class.BASE_SPEED}", True, WHITE)
                screen.blit(health_text, (card_rect.x + 60, y_offset + 35))
                
                # Descrição da habilidade
                desc_text = font.render(boss_info['description1'], True, (50, 255, 50))
                screen.blit(desc_text, (card_rect.x + 60, y_offset + 50))

                # Descrição da habilidade
                desc_text = font.render(boss_info['description2'], True, (50, 255, 50))
                screen.blit(desc_text, (card_rect.x + 60, y_offset + 65))
                
                # Duração e cooldown
                timing_text = font.render(f"Duração: {boss_info['ability_duration']} | Cooldown: {boss_info['ability_cooldown']}", 
                                        True, WHITE)
                screen.blit(timing_text, (card_rect.x + 60, y_offset + 80))
                
                y_offset += card_height + 10
            
            # Draw pagination controls
            button_width = 40
            button_height = 30
            spacing = 150
            start_x = panel_rect.right - 240
            button_y = panel_rect.top + 10
            
            font_back_next = pygame.font.Font(None, 35)
            
            # Previous page button
            self.prev_button_rect = pygame.Rect(start_x, button_y, button_width, button_height)
            prev_color = MENU_LIGHT_GRAY if self.current_page > 0 else (60, 60, 60)
            pygame.draw.rect(screen, prev_color, self.prev_button_rect)
            pygame.draw.rect(screen, WHITE, self.prev_button_rect, 1)
            
            prev_text = font_back_next.render("<", True, WHITE if self.current_page > 0 else (150, 150, 150))
            prev_rect = prev_text.get_rect(center=self.prev_button_rect.center)
            screen.blit(prev_text, prev_rect)
            
            # Next page button
            self.next_button_rect = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
            next_color = MENU_LIGHT_GRAY if end_index < len(self.bosses) else (60, 60, 60)
            pygame.draw.rect(screen, next_color, self.next_button_rect)
            pygame.draw.rect(screen, WHITE, self.next_button_rect, 1)
            
            next_text = font_back_next.render(">", True, WHITE if end_index < len(self.bosses) else (150, 150, 150))
            next_rect = next_text.get_rect(center=self.next_button_rect.center)
            screen.blit(next_text, next_rect)
            
            # Page indicator
            total_pages = (len(self.bosses) + self.bosses_per_page - 1) // self.bosses_per_page
            page_text = font_wave.render(f"{self.current_page + 1}/{total_pages}", True, WHITE)
            page_rect = page_text.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 10)
            screen.blit(page_text, page_rect)
        
        # Sempre desenha o botão da aba
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        # Desenha o texto "CHEFÕES" na vertical
        font = pygame.font.Font(None, 18)
        text = font.render("Chefões", True, WHITE)
        text_vertical = pygame.transform.rotate(text, 270)
        text_rect = text_vertical.get_rect(center=self.header_rect.center)
        screen.blit(text_vertical, text_rect)
        
    def handle_click(self, pos):
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            return True
            
        if self.is_expanded:
            # Handle pagination button clicks
            if self.prev_button_rect and self.prev_button_rect.collidepoint(pos) and self.current_page > 0:
                self.current_page -= 1
                return True
                
            if self.next_button_rect and self.next_button_rect.collidepoint(pos):
                next_page_start = (self.current_page + 1) * self.bosses_per_page
                if next_page_start < len(self.bosses):
                    self.current_page += 1
                    return True
                    
        return False

def main():
    # Lista de inimigos, defensores e feitiços
    enemies = []
    defenders = []
    spells = []  # Nova lista para feitiços ativos

    # Sistema de ondas e recursos
    wave_manager = WaveManager()
    gold = 300  # Ouro inicial
    
    # Sistema de missões
    mission_manager = MissionManager()

    # Interface
    enemy_shop = EnemyShopMenu()  # Menu lateral de inimigos
    defender_shop = DefenderShopMenu(mission_manager)  # Menu lateral de defensores
    boss_shop = BossShopMenu()  # Menu lateral de chefões
    selected_button = None
    skip_button = SkipButton()
    base = Base()
    upgrade_menu = UpgradeMenu()

    # Calcula as posições dos botões de feitiço
    spell_spacing = 60
    spell_start_x = 400  # Posição inicial dos botões de feitiço
    
    # Interface
    spell_buttons = [
        SpellButton(FreezeSpell, spell_start_x),
        SpellButton(DotSpell, spell_start_x + spell_spacing),
        SpellButton(DamageSpell, spell_start_x + spell_spacing * 2),
    ]
    selected_spell = None

    # Fonte para textos
    font = pygame.font.Font(None, 36)

    # Controle de seleção
    selected_defender = None

    # Game loop
    running = True
    clock = pygame.time.Clock()
    immunity_boss = None  # Referência para o boss de imunidade

    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_wave = wave_manager.current_wave
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Verifica clique no botão de pular
                if skip_button.handle_click(mouse_pos, wave_manager.wave_active):
                    wave_manager.skip_preparation()
                    continue
                    
                # Verifica clique nas missões
                if mission_manager.handle_click(mouse_pos):
                    continue
                    
                # Verifica clique no menu de inimigos
                if enemy_shop.handle_click(mouse_pos):
                    if enemy_shop.is_expanded:
                        defender_shop.is_expanded = False
                        boss_shop.is_expanded = False
                    continue
                    
                # Verifica clique no menu de defensores
                button, was_header_click = defender_shop.handle_click(mouse_pos, gold)
                if was_header_click:
                    if defender_shop.is_expanded:
                        enemy_shop.is_expanded = False
                        boss_shop.is_expanded = False
                    continue
                if button:
                    # Se já tinha um botão selecionado, desseleciona
                    if selected_button and selected_button != button:
                        selected_button.selected = False
                    selected_button = button if button.selected else None
                    # Desseleciona defensor atual
                    if selected_defender:
                        selected_defender.selected = False
                        selected_defender = None
                    continue
                    
                # Verifica clique no menu de chefões
                if boss_shop.handle_click(mouse_pos):
                    if boss_shop.is_expanded:
                        enemy_shop.is_expanded = False
                        defender_shop.is_expanded = False
                    continue
                    
                # Verifica clique nos botões de feitiço
                clicked_spell = False
                for button in spell_buttons:
                    if button.handle_click(mouse_pos, gold):
                        # Desseleciona outros botões
                        for other_button in spell_buttons:
                            if other_button != button:
                                other_button.selected = False
                        selected_spell = button if button.selected else None
                        clicked_spell = True
                        # Desseleciona defensor e botão de defensor
                        if selected_defender:
                            selected_defender.selected = False
                            selected_defender = None
                        if selected_button:
                            selected_button.selected = False
                            selected_button = None
                        break
                        
                if clicked_spell:
                    continue
                    
                # Verifica clique nos botões de upgrade/venda
                action, value = upgrade_menu.handle_click(mouse_pos, selected_defender, gold, current_wave)
                if action == "upgrade":
                    gold -= value
                    selected_defender.upgrade()
                    continue
                elif action == "sell":
                    gold += value
                    defenders.remove(selected_defender)
                    selected_defender = None
                    continue
                    
                # Se um botão estiver selecionado e tem ouro suficiente, adiciona defensor
                if selected_button and selected_button.selected and gold >= selected_button.cost:
                    # Verifica se o ponto é válido para colocação
                    if is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders):
                        defenders.append(selected_button.defender_class(mouse_pos[0], mouse_pos[1], current_wave))
                        gold -= selected_button.cost
                        selected_button.selected = False
                        selected_button = None
                        # Mantém o menu de defensores aberto
                        defender_shop.is_expanded = True
                else:
                    # Verifica clique em defensores existentes
                    clicked_defender = None
                    for defender in defenders:
                        if defender.handle_click(mouse_pos):
                            clicked_defender = defender
                            break
                            
                    # Desseleciona o defensor anterior
                    if selected_defender and selected_defender != clicked_defender:
                        selected_defender.selected = False
                        
                    selected_defender = clicked_defender
                    
                    # Se selecionou um defensor, fecha os menus
                    if selected_defender:
                        enemy_shop.is_expanded = False
                        defender_shop.is_expanded = False
                
                # Se um feitiço estiver selecionado e tem ouro suficiente
                if selected_spell and selected_spell.selected:
                    # Verifica se o ponto é válido para colocação
                    if is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders, is_spell=True):
                        if isinstance(selected_spell.spell_class, DamageSpell):
                            spells.append(selected_spell.spell_class(mouse_pos[0], mouse_pos[1], wave_manager))
                        else:
                            spells.append(selected_spell.spell_class(mouse_pos[0], mouse_pos[1]))
                        selected_spell.start_cooldown()  # Inicia o cooldown do feitiço
                        selected_spell = None
                    continue

        # Atualização da onda
        wave_manager.update()
        
        # Atualização dos feitiços
        for spell in spells[:]:  # Usa uma cópia da lista para poder modificá-la durante a iteração
            spell_result = spell.update(enemies)
            
            # Se o feitiço matou um inimigo
            if spell_result == "died":
                # Processa todos os inimigos mortos pelo feitiço
                if hasattr(spell, 'killed_enemies'):
                    for dead_enemy in spell.killed_enemies:
                        if dead_enemy in enemies and not dead_enemy.reward_given:
                            # Identifica o tipo do inimigo
                            if isinstance(dead_enemy, SpeedEnemy):
                                enemy_type = 'speed'
                            elif isinstance(dead_enemy, TankEnemy):
                                enemy_type = 'tank'
                            elif isinstance(dead_enemy, ArmoredEnemy):
                                enemy_type = 'armored'
                            elif isinstance(dead_enemy, HealerEnemy):
                                enemy_type = 'healer'
                            elif isinstance(dead_enemy, FreezeAuraEnemy):
                                enemy_type = 'freeze_aura'
                            elif isinstance(dead_enemy, RageEnemy):
                                enemy_type = 'rage'
                            elif isinstance(dead_enemy, StealthEnemy):
                                enemy_type = 'stealth'
                            elif isinstance(dead_enemy, ImmunityBoss) or isinstance(dead_enemy, SpeedBoss):
                                enemy_type = 'boss'
                            else:
                                enemy_type = 'normal'
                            
                            # Adiciona o ouro
                            gold += wave_manager.enemy_defeated(enemy_type)
                            dead_enemy.reward_given = True
                            enemies.remove(dead_enemy)
                            mission_manager.update_kills()  # Atualiza contagem de kills
            elif not spell_result:  # Se o feitiço terminou
                spells.remove(spell)
        
        # Atualiza os cooldowns dos botões de feitiço
        for button in spell_buttons:
            button.update()
        
        # Spawn de inimigos
        spawn_result = wave_manager.should_spawn_enemy()
        if spawn_result:
            if spawn_result == "immunity_boss":
                # Spawna o boss de imunidade
                immunity_boss = ImmunityBoss(PATH)
                immunity_boss.set_enemies_list(enemies)
                enemies.append(immunity_boss)
            elif spawn_result == "speed_boss":
                # Spawna o boss de velocidade
                speed_boss = SpeedBoss(PATH)
                speed_boss.set_enemies_list(enemies)
                enemies.append(speed_boss)
            else:
                enemy, is_special = spawn_random_enemy(PATH, wave_manager)
                enemy.set_enemies_list(enemies)
                enemies.append(enemy)
            
        # Atualização dos inimigos
        for enemy in enemies[:]:
            enemy.set_enemies_list(enemies)  # Atualiza a lista de inimigos
            move_result = enemy.move()  # Agora pode retornar True, False, "died" ou "heal"
            
            # Primeiro verifica se chegou ao final do caminho
            if move_result is True:  # True significa que chegou ao final do caminho
                enemies.remove(enemy)
                if base.take_damage(10):  # Inimigo atingiu a base
                    running = False  # Game over se a base for destruída
                continue
            
            # Depois verifica cura
            if isinstance(enemy, HealerEnemy) and move_result == "heal":
                # Cria efeito visual de cura
                heal_effect = pygame.Surface((enemy.heal_radius * 2, enemy.heal_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(heal_effect, (*enemy.COLOR, 100), 
                                (enemy.heal_radius, enemy.heal_radius), enemy.heal_radius)
                screen.blit(heal_effect, (int(enemy.x - enemy.heal_radius), 
                                        int(enemy.y - enemy.heal_radius)))
                # Cura todos os inimigos próximos
                for other_enemy in enemies:
                    if other_enemy != enemy:
                        dx = other_enemy.x - enemy.x
                        dy = other_enemy.y - enemy.y
                        distance = math.sqrt(dx ** 2 + dy ** 2)
                        if distance <= enemy.heal_radius:
                            other_enemy.health = min(other_enemy.max_health, 
                                                   other_enemy.health + enemy.heal_amount)
            
            # Verifica morte por DoT
            elif move_result == "died":  # Morreu por dano ao longo do tempo
                # Identifica o tipo do inimigo e adiciona o ouro
                if isinstance(enemy, SpeedEnemy):
                    enemy_type = 'speed'
                elif isinstance(enemy, TankEnemy):
                    enemy_type = 'tank'
                elif isinstance(enemy, ArmoredEnemy):
                    enemy_type = 'armored'
                elif isinstance(enemy, HealerEnemy):
                    enemy_type = 'healer'
                elif isinstance(enemy, FreezeAuraEnemy):
                    enemy_type = 'freeze_aura'
                elif isinstance(enemy, RageEnemy):
                    enemy_type = 'rage'
                elif isinstance(enemy, StealthEnemy):
                    enemy_type = 'stealth'
                elif isinstance(enemy, ImmunityBoss) or isinstance(enemy, SpeedBoss):
                    enemy_type = 'boss'
                else:
                    enemy_type = 'normal'
                
                if not enemy.reward_given:
                    gold += wave_manager.enemy_defeated(enemy_type)
                    enemy.reward_given = True
                    mission_manager.update_kills()
                enemies.remove(enemy)
        
        # Atualização dos defensores
        for defender in defenders:
            if isinstance(defender, YellowDefender):
                defender.update(enemies, defenders)
            else:
                defender.update(enemies)
                
            # Verifica os projéteis que atingiram inimigos
            for projectile in defender.projectiles[:]:
                if projectile.move():
                    if projectile.target and hasattr(projectile.target, 'take_damage'):
                        # Verifica se o alvo está protegido pela aura de imunidade
                        is_immune = False
                        for enemy in enemies:
                            if isinstance(enemy, ImmunityBoss) and enemy.is_immunized:
                                immune_enemies = enemy.get_enemies_in_immunity_range(enemies)
                                if projectile.target in immune_enemies:
                                    is_immune = True
                                    break
                        
                        if not is_immune:
                            # Se o inimigo morreu com este projétil
                            damage_result = projectile.target.take_damage(projectile.damage)
                            
                            # Se o inimigo é um FreezeAuraEnemy e morreu, aplica congelamento em área
                            if isinstance(projectile.target, FreezeAuraEnemy) and damage_result == "freeze_aura":
                                projectile.target.apply_freeze_aura(defenders)
                                
                            if damage_result:  # Se morreu normalmente
                                # Identifica o tipo do inimigo
                                if isinstance(projectile.target, SpeedEnemy):
                                    enemy_type = 'speed'
                                elif isinstance(projectile.target, TankEnemy):
                                    enemy_type = 'tank'
                                elif isinstance(projectile.target, ArmoredEnemy):
                                    enemy_type = 'armored'
                                elif isinstance(projectile.target, HealerEnemy):
                                    enemy_type = 'healer'
                                elif isinstance(projectile.target, FreezeAuraEnemy):
                                    enemy_type = 'freeze_aura'
                                elif isinstance(projectile.target, RageEnemy):
                                    enemy_type = 'rage'
                                elif isinstance(projectile.target, StealthEnemy):
                                    enemy_type = 'stealth'
                                elif isinstance(projectile.target, ImmunityBoss) or isinstance(projectile.target, SpeedBoss):
                                    enemy_type = 'boss'
                                else:
                                    enemy_type = 'normal'
                                
                                # Adiciona o ouro e remove o inimigo
                                if not projectile.target.reward_given:  # Verifica se já deu recompensa
                                    gold += wave_manager.enemy_defeated(enemy_type)
                                    projectile.target.reward_given = True  # Marca que já deu recompensa
                                    mission_manager.update_kills()  # Atualiza contagem de kills quando inimigo morre por projétil
                                if projectile.target in enemies:  # Verifica se o inimigo ainda está na lista
                                    enemies.remove(projectile.target)
                                if projectile.target == defender.current_target:
                                    defender.current_target = None
                    
                    defender.projectiles.remove(projectile)
            
        # Verifica se a onda terminou
        if wave_manager.check_wave_complete(enemies):
            if not wave_manager.start_next_wave():
                # Jogador venceu o jogo
                running = False
                print("Parabéns! Você completou todas as ondas!")
            else:
                mission_manager.update_wave(wave_manager.current_wave - 1)  # Atualiza contagem de ondas
        
        # Desenho
        screen.fill(MENU_GRAY)
        
        # Desenha o menu superior de ondas
        draw_wave_menu(screen, wave_manager, skip_button)
        
        # Desenha o background após o menu lateral e superior
        screen.blit(background, (0, WAVE_MENU_HEIGHT))
        
        # Desenha todos os inimigos
        for enemy in enemies:
            enemy.draw(screen)
            
        # Desenha todos os feitiços ativos
        for spell in spells:
            spell.draw(screen)
        
        # Desenha todos os defensores
        for defender in defenders:
            defender.draw(screen)
            
        # Desenha os botões de feitiço
        for button in spell_buttons:
            button.draw(screen, gold)
        
        # Desenha os menus laterais
        enemy_shop.draw(screen, wave_manager)
        defender_shop.draw(screen, gold, selected_button)
        boss_shop.draw(screen, wave_manager)
        
        # Se um feitiço estiver selecionado, mostra a prévia
        if selected_spell and selected_spell.selected:
            # Verifica se a posição é válida
            is_valid = is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders, is_spell=True)
            if is_valid:
                # Desenha o raio do feitiço
                color = (*selected_spell.spell_class.COLOR, 128)
                spell_surface = pygame.Surface((selected_spell.radius * 2, selected_spell.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(spell_surface, color, (selected_spell.radius, selected_spell.radius), selected_spell.radius)
                screen.blit(spell_surface, (mouse_pos[0] - selected_spell.radius, mouse_pos[1] - selected_spell.radius))
        
        # Se um botão de defensor estiver selecionado, mostra a prévia
        if selected_button and selected_button.selected:
            # Verifica se a posição é válida
            is_valid = is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders)
            
            # Desenha o range (vermelho se inválido, cinza se válido)
            color = (255, 0, 0, 128) if not is_valid else (200, 200, 200, 128)
            range_surface = pygame.Surface((selected_button.defender_class.RANGE * 2, selected_button.defender_class.RANGE * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, color, (selected_button.defender_class.RANGE, selected_button.defender_class.RANGE), selected_button.defender_class.RANGE)
            screen.blit(range_surface, (mouse_pos[0] - selected_button.defender_class.RANGE, mouse_pos[1] - selected_button.defender_class.RANGE))
            
            # Desenha o retângulo menor com a mesma cor do range
            preview_size = 30  # Tamanho do retângulo de preview
            preview_surface = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)
            pygame.draw.rect(preview_surface, color, (0, 0, preview_size, preview_size))
            screen.blit(preview_surface, (mouse_pos[0] - preview_size//2, mouse_pos[1] - preview_size//2))
            
            # Desenha a prévia do defensor
            selected_button.defender_class.draw_preview(screen, mouse_pos[0], mouse_pos[1], is_valid)
        
        # Desenha o menu de upgrade se houver um defensor selecionado
        if selected_defender:
            upgrade_menu.draw(screen, selected_defender, gold, current_wave)
            
        # Desenha a barra de vida da base
        base.draw(screen)
        
        # Desenha o menu de missões por último para ficar sempre visível
        mission_manager.draw(screen)
        
        # Desenha o texto de ouro e orbes no canto inferior esquerdo
        font = pygame.font.Font(None, 28)
        info_menu_rect = pygame.Rect(0, SCREEN_HEIGHT - 70, 200, 70)
        pygame.draw.rect(screen, MENU_GRAY, info_menu_rect)
        pygame.draw.rect(screen, WHITE, info_menu_rect, 2)
        
        gold_text = font.render(f"Ouro: {gold}", True, (255, 215, 0))
        screen.blit(gold_text, (20, SCREEN_HEIGHT - 60))
        
        orb_text = font.render(f"Orbes: {mission_manager.orbes}", True, (50, 255, 50))
        screen.blit(orb_text, (20, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
