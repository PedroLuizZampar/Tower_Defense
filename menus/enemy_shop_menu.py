import pygame
from enemy import Enemy, TankEnemy, SpeedEnemy, ArmoredEnemy, HealerEnemy, FreezeAuraEnemy, RageEnemy, StealthEnemy

# Cores
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)
WHITE = (255, 255, 255)

class EnemyShopMenu:
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT):
        self.width = 250
        self.height = SCREEN_HEIGHT - WAVE_MENU_HEIGHT
        self.is_expanded = False
        self.header_rect = None
        self.rect = None
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WAVE_MENU_HEIGHT = WAVE_MENU_HEIGHT
        self.current_page = 0  # Current page index
        self.enemies_per_page = 5  # Number of enemies per page
        self.prev_button_rect = None  # Rectangle for previous page button
        self.next_button_rect = None  # Rectangle for next page button
        self.enemies = [Enemy, TankEnemy, SpeedEnemy, ArmoredEnemy, HealerEnemy, FreezeAuraEnemy, RageEnemy, StealthEnemy]

    def draw(self, screen, wave_manager):
        # Desenha o cabeçalho (sempre visível)
        header_width = 40
        header_height = 100
        header_x = self.SCREEN_WIDTH - header_width
        self.header_rect = pygame.Rect(header_x, self.WAVE_MENU_HEIGHT + 98, header_width, header_height)
        
        # Define o rect principal do menu
        self.rect = pygame.Rect(self.SCREEN_WIDTH - self.width - header_width, self.WAVE_MENU_HEIGHT, 
                               self.width, self.height)
        
        # Se expandido, desenha o resto do menu
        if self.is_expanded:
            pygame.draw.rect(screen, MENU_GRAY, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            
            font = pygame.font.Font(None, 28)
            text = font.render("INIMIGOS", True, WHITE)
            text_rect = text.get_rect(center=(self.rect.centerx, self.WAVE_MENU_HEIGHT + 25))
            screen.blit(text, text_rect)
            
            # Draw only the enemies for the current page
            start_index = self.current_page * self.enemies_per_page
            end_index = min(start_index + self.enemies_per_page, len(self.enemies))
            
            y_offset = self.WAVE_MENU_HEIGHT + 45
            font = pygame.font.Font(None, 20)
            font_title = pygame.font.Font(None, 24)
            
            for enemy_class in self.enemies[start_index:end_index]:
                # Fundo do card do inimigo
                card_height = 90
                card_rect = pygame.Rect(self.rect.x + 10, y_offset, self.width - 20, card_height)
                pygame.draw.rect(screen, (40, 40, 40), card_rect)
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
            start_x = self.rect.right - 240
            button_y = self.rect.top + 10
            
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
            page_rect = page_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 10)
            screen.blit(page_text, page_rect)

        # Sempre desenha o botão da aba
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)

        # Desenha o texto "INIMIGOS" na vertical
        font = pygame.font.Font(None, 18)
        text = font.render("Inimigos", True, WHITE)
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
                next_page_start = (self.current_page + 1) * self.enemies_per_page
                if next_page_start < len(self.enemies):
                    self.current_page += 1
                    return True
                    
        return False