import pygame
from enemy import ImmunityBoss, SpeedBoss, MagnetBoss, VampiricBoss, SplitBoss

# Cores
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)
WHITE = (255, 255, 255)

class BossShopMenu:
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT):
        self.width = 250
        self.height = SCREEN_HEIGHT - WAVE_MENU_HEIGHT
        self.is_expanded = False
        self.header_rect = None
        self.rect = None
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WAVE_MENU_HEIGHT = WAVE_MENU_HEIGHT
        self.current_page = 0
        self.bosses_per_page = 4
        self.bosses = [
            {
                'class': SpeedBoss,
                'wave': 10,
                'description1': "Aumenta a velocidade de",
                'description2': "todos os inimigos em 50%",
                'ability_name': "Aura de Velocidade",
                'duration': "2s",
                'cooldown': "5s"
            },
            {
                'class': SplitBoss,
                'wave': 20,
                'description1': "Ao morrer, se divide em",
                'description2': "dois minions mais fracos",
                'ability_name': "Divisão",
                'duration': "N/A",
                'cooldown': "N/A"
            },
            {
                'class': MagnetBoss,
                'wave': 30,
                'description1': "Atrai todos os projéteis",
                'description2': "para si, protegendo aliados",
                'ability_name': "Atração Magnética",
                'duration': "3s",
                'cooldown': "5s"
            },
            {
                'class': VampiricBoss,
                'wave': 40,
                'description1': "Rouba 50% da vida dos inimigos",
                'description2': "ao morrer +10% de vida por inimigo",
                'ability_name': "Drenagem Vital",
                'duration': "N/A",
                'cooldown': "N/A"
            },
            {
                'class': ImmunityBoss,
                'wave': 50,
                'description1': "Protege aliados próximos",
                'description2': "de todo dano e feitiço",
                'ability_name': "Aura de Imunidade",
                'duration': "2s",
                'cooldown': "3s"
            }
        ]
        
    def draw(self, screen, wave_manager):
        # Desenha o cabeçalho (sempre visível)
        header_width = 40
        header_height = 100
        header_x = self.SCREEN_WIDTH - header_width
        self.header_rect = pygame.Rect(header_x, self.WAVE_MENU_HEIGHT + 196, header_width, header_height)
        
        # Define o rect principal do menu
        self.rect = pygame.Rect(self.SCREEN_WIDTH - self.width - header_width, self.WAVE_MENU_HEIGHT, 
                               self.width, self.height)
        
        # Se expandido, desenha o resto do menu
        if self.is_expanded:
            pygame.draw.rect(screen, MENU_GRAY, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            
            font = pygame.font.Font(None, 28)
            text = font.render("CHEFÕES", True, WHITE)
            text_rect = text.get_rect(center=(self.rect.centerx, self.WAVE_MENU_HEIGHT + 25))
            screen.blit(text, text_rect)
            
            # Draw only the bosses for the current page
            start_index = self.current_page * self.bosses_per_page
            end_index = min(start_index + self.bosses_per_page, len(self.bosses))
            
            y_offset = self.WAVE_MENU_HEIGHT + 45
            font = pygame.font.Font(None, 16)
            vampiric_font = pygame.font.Font(None, 14)
            font_title = pygame.font.Font(None, 24)
            
            for boss_info in self.bosses[start_index:end_index]:
                boss_class = boss_info['class']
                # Fundo do card do chefão
                card_height = 100
                card_rect = pygame.Rect(self.rect.x + 10, y_offset, self.width - 20, card_height)
                
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
                
                if boss_class == VampiricBoss:
                    font = vampiric_font
                    # Descrição da habilidade em duas linhas
                    desc_text1 = font.render(boss_info['description1'], True, (50, 255, 50))
                    desc_text2 = font.render(boss_info['description2'], True, (50, 255, 50))
                    screen.blit(desc_text1, (card_rect.x + 60, y_offset + 50))
                    screen.blit(desc_text2, (card_rect.x + 60, y_offset + 65))
                    font = pygame.font.Font(None, 16)
                else:
                    # Descrição da habilidade em duas linhas
                    desc_text1 = font.render(boss_info['description1'], True, (50, 255, 50))
                    desc_text2 = font.render(boss_info['description2'], True, (50, 255, 50))
                    screen.blit(desc_text1, (card_rect.x + 60, y_offset + 50))
                    screen.blit(desc_text2, (card_rect.x + 60, y_offset + 65))

                # Duração e cooldown
                timing_text = font.render(f"Duração: {boss_info['duration']} | Cooldown: {boss_info['cooldown']}", 
                                        True, WHITE)
                screen.blit(timing_text, (card_rect.x + 60, y_offset + 80))
                
                y_offset += card_height + 10
            
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
            next_color = MENU_LIGHT_GRAY if end_index < len(self.bosses) else (60, 60, 60)
            pygame.draw.rect(screen, next_color, self.next_button_rect)
            pygame.draw.rect(screen, WHITE, self.next_button_rect, 1)
            
            next_text = font_back_next.render(">", True, WHITE if end_index < len(self.bosses) else (150, 150, 150))
            next_rect = next_text.get_rect(center=self.next_button_rect.center)
            screen.blit(next_text, next_rect)
            
            # Page indicator
            total_pages = (len(self.bosses) + self.bosses_per_page - 1) // self.bosses_per_page
            page_text = font_wave.render(f"{self.current_page + 1}/{total_pages}", True, WHITE)
            page_rect = page_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 10)
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