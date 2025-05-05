import pygame
from advantages import DamageAdvantage, CooldownAdvantage, GoldAdvantage

# Cores
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)
WHITE = (255, 255, 255)

class AdvantagesMenu:
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT):
        self.width = 250
        self.height = SCREEN_HEIGHT - WAVE_MENU_HEIGHT
        self.is_expanded = False
        self.header_rect = None
        self.rect = None
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WAVE_MENU_HEIGHT = WAVE_MENU_HEIGHT
        
        # Lista de vantagens
        self.advantages = [DamageAdvantage(), CooldownAdvantage(), GoldAdvantage()]
        
        # Para manter compatibilidade com código existente
        self.damage_advantage = self.advantages[0]
        self.cooldown_advantage = self.advantages[1]
        self.gold_advantage = self.advantages[2]
    
    def draw(self, screen, mission_manager):
        # Desenha o cabeçalho (sempre visível)
        header_width = 40
        header_height = 104
        header_x = self.SCREEN_WIDTH - header_width
        self.header_rect = pygame.Rect(header_x, self.WAVE_MENU_HEIGHT + 408, header_width, header_height)
        
        # Define o rect principal do menu
        self.rect = pygame.Rect(self.SCREEN_WIDTH - self.width - header_width, self.WAVE_MENU_HEIGHT, 
                               self.width, self.height)
        
        # Se expandido, desenha o resto do menu
        if self.is_expanded:
            pygame.draw.rect(screen, MENU_GRAY, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            
            # Título "VANTAGENS"
            font_title = pygame.font.Font(None, 28)
            text = font_title.render("VANTAGENS", True, WHITE)
            text_rect = text.get_rect(center=(self.rect.centerx, self.WAVE_MENU_HEIGHT + 25))
            screen.blit(text, text_rect)
            
            # Card do upgrade de dano
            card_height = 110
            card_rect = pygame.Rect(self.rect.x + 10, self.WAVE_MENU_HEIGHT + 45, self.width - 20, card_height)
            pygame.draw.rect(screen, (60, 60, 60), card_rect)
            pygame.draw.rect(screen, WHITE, card_rect, 1)
            
            # Nome do upgrade
            font = pygame.font.Font(None, 24)
            name_text = font.render("Dano", True, WHITE)
            name_rect = name_text.get_rect(x=card_rect.x + 10, y=self.WAVE_MENU_HEIGHT + 55)
            screen.blit(name_text, name_rect)
            
            # Ícone representativo (um pequeno quadrado vermelho)
            pygame.draw.rect(screen, (255, 50, 50), 
                           (card_rect.x + 15, name_rect.bottom + 15, 30, 30))
            
            # Status atual em duas linhas
            level_text = font.render(f"Nv.{self.damage_advantage.level}", True, WHITE)
            screen.blit(level_text, (name_rect.right + 5, name_rect.top))
                       
            font_stats = pygame.font.Font(None, 16)
            bonus_text = font_stats.render(f"Aumenta em {self.damage_advantage.get_current_bonus()}% o dano", True, (50, 255, 50))
            screen.blit(bonus_text, (card_rect.x + 60, name_rect.bottom + 15))
            
            # Descrição do upgrade
            desc_text = font_stats.render("base dos defensores", True, (50, 255, 50))
            screen.blit(desc_text, (card_rect.x + 60, name_rect.bottom + 30))
            
            # Botão de upgrade de dano
            upgrade_cost = self.damage_advantage.get_upgrade_cost()
            can_upgrade = mission_manager.orbes >= upgrade_cost
            
            upgrade_button = pygame.Rect(card_rect.x + 10, card_rect.bottom - 30, self.width - 40, 25)
            self.damage_upgrade_button = upgrade_button
            
            button_color = (50, 200, 50) if can_upgrade else (100, 100, 100)
            text_color = WHITE if can_upgrade else (150, 150, 150)
            
            pygame.draw.rect(screen, button_color, upgrade_button)
            pygame.draw.rect(screen, WHITE, upgrade_button, 1)
            
            font_upgrade = pygame.font.Font(None, 20)
            upgrade_text = font_upgrade.render(f"Melhorar ({upgrade_cost} Orbes)", True, text_color)
            text_rect = upgrade_text.get_rect(center=upgrade_button.center)
            screen.blit(upgrade_text, text_rect)

            # Card do upgrade de cooldown
            cooldown_card_rect = pygame.Rect(self.rect.x + 10, card_rect.bottom + 10, self.width - 20, card_height)
            pygame.draw.rect(screen, (60, 60, 60), cooldown_card_rect)
            pygame.draw.rect(screen, WHITE, cooldown_card_rect, 1)
            
            # Nome do upgrade de cooldown
            name_text = font.render("Velocidade", True, WHITE)
            name_rect = name_text.get_rect(x=cooldown_card_rect.x + 10, y=cooldown_card_rect.y + 10)
            screen.blit(name_text, name_rect)
            
            # Ícone representativo (um pequeno quadrado azul)
            pygame.draw.rect(screen, (50, 50, 255), 
                           (cooldown_card_rect.x + 15, name_rect.bottom + 15, 30, 30))
            
            # Status atual
            level_text = font.render(f"Nv.{self.cooldown_advantage.level}", True, WHITE)
            screen.blit(level_text, (name_rect.right + 5, name_rect.top))
            
            bonus_text = font_stats.render(f"Reduz em {self.cooldown_advantage.get_current_bonus()}% o tempo", True, (50, 255, 50))
            screen.blit(bonus_text, (cooldown_card_rect.x + 60, name_rect.bottom + 15))
            
            desc_text = font_stats.render("entre ataques dos defensores", True, (50, 255, 50))
            screen.blit(desc_text, (cooldown_card_rect.x + 60, name_rect.bottom + 30))
            
            # Botão de upgrade de cooldown
            upgrade_cost = self.cooldown_advantage.get_upgrade_cost()
            can_upgrade = mission_manager.orbes >= upgrade_cost and self.cooldown_advantage.level < self.cooldown_advantage.max_level
            
            upgrade_button = pygame.Rect(cooldown_card_rect.x + 10, cooldown_card_rect.bottom - 30, self.width - 40, 25)
            self.cooldown_upgrade_button = upgrade_button
            
            button_color = (50, 200, 50) if can_upgrade else (100, 100, 100)
            text_color = WHITE if can_upgrade else (150, 150, 150)
            
            pygame.draw.rect(screen, button_color, upgrade_button)
            pygame.draw.rect(screen, WHITE, upgrade_button, 1)
            
            if self.cooldown_advantage.level >= self.cooldown_advantage.max_level:
                button_text = "NÍVEL MÁXIMO"
            else:
                button_text = f"Melhorar ({upgrade_cost} Orbes)"
                
            upgrade_text = font_upgrade.render(button_text, True, text_color)
            text_rect = upgrade_text.get_rect(center=upgrade_button.center)
            screen.blit(upgrade_text, text_rect)

            # Card da vantagem de troca de orbe por ouro
            gold_card_rect = pygame.Rect(self.rect.x + 10, cooldown_card_rect.bottom + 10, self.width - 20, card_height)
            pygame.draw.rect(screen, (60, 60, 60), gold_card_rect)
            pygame.draw.rect(screen, WHITE, gold_card_rect, 1)
            
            # Nome da vantagem
            name_text = font.render("Troca por Ouro", True, WHITE)
            name_rect = name_text.get_rect(x=gold_card_rect.x + 10, y=gold_card_rect.y + 10)
            screen.blit(name_text, name_rect)
            
            # Ícone representativo (um pequeno quadrado dourado)
            pygame.draw.rect(screen, (255, 215, 0), 
                           (gold_card_rect.x + 15, name_rect.bottom + 15, 30, 30))
            
            # Descrição da troca
            desc_text = font_stats.render(f"Troque 1 orbe por {self.gold_advantage.get_gold_value()} de ouro", True, (50, 255, 50))
            screen.blit(desc_text, (gold_card_rect.x + 60, name_rect.bottom + 15))
            
            # Botão de troca
            can_exchange = mission_manager.orbes >= 1
            exchange_button = pygame.Rect(gold_card_rect.x + 10, gold_card_rect.bottom - 30, self.width - 40, 25)
            self.gold_exchange_button = exchange_button
            
            button_color = (50, 200, 50) if can_exchange else (100, 100, 100)
            text_color = WHITE if can_exchange else (150, 150, 150)
            
            pygame.draw.rect(screen, button_color, exchange_button)
            pygame.draw.rect(screen, WHITE, exchange_button, 1)
            
            upgrade_text = font_upgrade.render("Trocar 1 Orbe", True, text_color)
            text_rect = upgrade_text.get_rect(center=exchange_button.center)
            screen.blit(upgrade_text, text_rect)
        
        # Sempre desenha o botão da aba
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        # Desenha o texto "Vantagens" na vertical
        font = pygame.font.Font(None, 18)
        text = font.render("Vantagens", True, WHITE)
        text_vertical = pygame.transform.rotate(text, 270)
        text_rect = text_vertical.get_rect(center=self.header_rect.center)
        screen.blit(text_vertical, text_rect)
        
    def handle_click(self, pos, mission_manager):
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            return 0
            
        if self.is_expanded:
            # Se o menu estiver expandido, verifica se clicou dentro da área dele
            if not self.rect.collidepoint(pos):
                self.is_expanded = False
                return 0
                
            # Verifica clique no botão de upgrade de dano
            if hasattr(self, 'damage_upgrade_button') and self.damage_upgrade_button.collidepoint(pos):
                if self.damage_advantage.upgrade(mission_manager):
                    return 0
                    
            # Verifica clique no botão de upgrade de cooldown
            if hasattr(self, 'cooldown_upgrade_button') and self.cooldown_upgrade_button.collidepoint(pos):
                if self.cooldown_advantage.upgrade(mission_manager):
                    return 0
                    
            # Verifica clique no botão de troca por ouro
            if hasattr(self, 'gold_exchange_button') and self.gold_exchange_button.collidepoint(pos):
                return self.gold_advantage.exchange(mission_manager)
                    
        return 0
