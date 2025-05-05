import pygame
from spell import DamageSpell, FreezeSpell, DotSpell, SlowSpell, WeaknessSpell, SpellButton

# Cores
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)
WHITE = (255, 255, 255)

class ThrowableSpellsMenu:
    def __init__(self):
        self.is_expanded = False
        self.width = 250
        self.height = 180
        self.header_rect = None
        self.rect = None
        self.spells = [FreezeSpell, DotSpell, DamageSpell, SlowSpell, WeaknessSpell]
        self.spells_per_row = 4  # Maximum spells per row
        
    def draw(self, screen, spell_buttons):
        # Define a posição do header (parte inferior da tela)
        header_width = 250  
        header_height = 35  
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        header_x = screen_width // 2 - header_width - 71
        header_y = screen_height - header_height
        
        self.header_rect = pygame.Rect(header_x, header_y, header_width, header_height)
        
        # Define a área principal do menu
        self.rect = pygame.Rect(header_x, screen_height - header_height - self.height, 
                              self.width, self.height)
        
        # Desenha o header
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        # Texto do header
        font = pygame.font.Font(None, 24)
        text = font.render("Feitiços Arremessáveis", True, WHITE)
        text_rect = text.get_rect(center=self.header_rect.center)
        screen.blit(text, text_rect)
        
        # Se o menu estiver expandido, desenha o conteúdo
        if self.is_expanded:
            # Posição e tamanho do menu
            menu_rect = pygame.Rect(header_x, screen_height - header_height - self.height, 
                                  self.width, self.height)
            pygame.draw.rect(screen, MENU_GRAY, menu_rect)
            pygame.draw.rect(screen, WHITE, menu_rect, 2)
            
            # Configuração da grid
            icon_size = 40
            spacing = 20
            x_start = menu_rect.x + 15
            y_start = menu_rect.y + 15
            
            for i, spell_class in enumerate(self.spells):
                # Calcula posição na grid
                row = i // self.spells_per_row
                col = i % self.spells_per_row
                
                x_pos = x_start + (icon_size + spacing) * col
                y_pos = y_start + (icon_size + spacing) * row
                
                # Encontra o botão correspondente
                spell_button = next((button for button in spell_buttons 
                                   if button.spell_class == spell_class), None)
                if not spell_button:
                    continue
                
                # Atualiza a posição do botão
                spell_button.rect = pygame.Rect(x_pos, y_pos, icon_size, icon_size)
                
                # Desenha o fundo do botão
                pygame.draw.rect(screen, (60, 60, 60), spell_button.rect)
                
                # Desenha o círculo do feitiço com cor normal ou acinzentada
                center_x = spell_button.rect.centerx
                center_y = spell_button.rect.centery
                if spell_button.cooldown_timer > 0:
                    color = spell_button.color
                    gray = (color[0] * 0.3 + color[1] * 0.59 + color[2] * 0.11) * 0.6
                    spell_color = (gray, gray, gray)
                else:
                    spell_color = spell_button.color
                pygame.draw.circle(screen, spell_color, (center_x, center_y), icon_size//2 - 5)
                
                # Se estiver selecionado, desenha borda
                if spell_button.selected:
                    pygame.draw.rect(screen, WHITE, spell_button.rect, 3)
                
                # Desenha o nome do feitiço
                name_font = pygame.font.Font(None, 16)
                name_text = name_font.render(spell_class.NAME, True, WHITE)
                name_rect = name_text.get_rect(centerx=center_x, top=spell_button.rect.bottom + 5)
                screen.blit(name_text, name_rect)
                
                # Se estiver em cooldown, desenha o tempo restante
                if spell_button.cooldown_timer > 0:
                    cooldown_font = pygame.font.Font(None, 24)
                    seconds = spell_button.cooldown_timer // 60
                    cooldown_text = cooldown_font.render(str(seconds), True, WHITE)
                    text_rect = cooldown_text.get_rect(center=spell_button.rect.center)
                    screen.blit(cooldown_text, text_rect)
    
    def handle_click(self, pos, spell_buttons):
        # Verifica clique no header
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            # Se o menu está fechando, desseleciona todos os feitiços e limpa suas posições
            if not self.is_expanded:
                for button in spell_buttons:
                    button.selected = False
                    if button.spell_class in self.spells:
                        button.rect.x = 0  # Reseta a posição
            return True
            
        # Se expandido, verifica cliques nos feitiços
        if self.is_expanded:
            for button in spell_buttons:
                if button.spell_class in self.spells and button.rect:
                    if button.rect.collidepoint(pos) and button.cooldown_timer <= 0:
                        # Desseleciona outros botões
                        for other_button in spell_buttons:
                            if other_button != button:
                                other_button.selected = False
                        button.selected = not button.selected
                        # Se selecionou, fecha o menu
                        if button.selected:
                            self.is_expanded = False
                        return True
        return False

class ConsumableSpellsMenu:
    def __init__(self):
        self.is_expanded = False
        self.width = 250
        self.height = 180
        self.header_rect = None
        self.rect = None
        self.spells = []
        self.spells_per_row = 4  # Maximum spells per row
        
    def draw(self, screen, spell_buttons):
        # Define a posição do header (parte inferior da tela)
        header_width = 250
        header_height = 35
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        header_x = screen_width // 2  - 72
        header_y = screen_height - header_height
        
        self.header_rect = pygame.Rect(header_x, header_y, header_width, header_height)
        
        # Define a área principal do menu
        self.rect = pygame.Rect(header_x, screen_height - header_height - self.height, 
                              self.width, self.height)
        
        # Desenha o header
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        # Texto do header
        font = pygame.font.Font(None, 24)
        text = font.render("Feitiços Consumíveis", True, WHITE)
        text_rect = text.get_rect(center=self.header_rect.center)
        screen.blit(text, text_rect)
        
        # Se o menu estiver expandido, desenha o conteúdo
        if self.is_expanded:
            # Posição e tamanho do menu
            menu_rect = pygame.Rect(header_x, screen_height - header_height - self.height, 
                                  self.width, self.height)
            pygame.draw.rect(screen, MENU_GRAY, menu_rect)
            pygame.draw.rect(screen, WHITE, menu_rect, 2)
            
            # Configuração da grid
            icon_size = 40
            spacing = 20
            x_start = menu_rect.x + 15
            y_start = menu_rect.y + 15
            
            for i, spell_class in enumerate(self.spells):
                # Calcula posição na grid
                row = i // self.spells_per_row
                col = i % self.spells_per_row
                
                x_pos = x_start + (icon_size + spacing) * col
                y_pos = y_start + (icon_size + spacing) * row
                
                # Encontra o botão correspondente
                spell_button = next((button for button in spell_buttons 
                                   if button.spell_class == spell_class), None)
                if not spell_button:
                    continue
                
                # Atualiza a posição do botão
                spell_button.rect = pygame.Rect(x_pos, y_pos, icon_size, icon_size)
                
                # Desenha o fundo do botão
                pygame.draw.rect(screen, (60, 60, 60), spell_button.rect)
                
                # Desenha o círculo do feitiço com cor normal ou acinzentada
                center_x = spell_button.rect.centerx
                center_y = spell_button.rect.centery
                if spell_button.cooldown_timer > 0:
                    color = spell_button.color
                    gray = (color[0] * 0.3 + color[1] * 0.59 + color[2] * 0.11) * 0.6
                    spell_color = (gray, gray, gray)
                else:
                    spell_color = spell_button.color
                pygame.draw.circle(screen, spell_color, (center_x, center_y), icon_size//2 - 5)
                
                # Se estiver selecionado, desenha borda
                if spell_button.selected:
                    pygame.draw.rect(screen, WHITE, spell_button.rect, 3)
                
                # Desenha o nome do feitiço
                name_font = pygame.font.Font(None, 16)
                name_text = name_font.render(spell_class.NAME, True, WHITE)
                name_rect = name_text.get_rect(centerx=center_x, top=spell_button.rect.bottom + 5)
                screen.blit(name_text, name_rect)
                
                # Se estiver em cooldown, desenha o tempo restante
                if spell_button.cooldown_timer > 0:
                    cooldown_font = pygame.font.Font(None, 24)
                    seconds = spell_button.cooldown_timer // 60
                    cooldown_text = cooldown_font.render(str(seconds), True, WHITE)
                    text_rect = cooldown_text.get_rect(center=spell_button.rect.center)
                    screen.blit(cooldown_text, text_rect)
    
    def handle_click(self, pos, spell_buttons):
        # Verifica clique no header
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            # Se o menu está fechando, desseleciona todos os feitiços e limpa suas posições
            if not self.is_expanded:
                for button in spell_buttons:
                    button.selected = False
                    if button.spell_class in self.spells:
                        button.rect.x = 0  # Reseta a posição
            return True
            
        # Se expandido, verifica cliques nos feitiços
        if self.is_expanded:
            for button in spell_buttons:
                if button.spell_class in self.spells and button.rect:
                    if button.rect.collidepoint(pos) and button.cooldown_timer <= 0:
                        # Desseleciona outros botões
                        for other_button in spell_buttons:
                            if other_button != button:
                                other_button.selected = False
                        button.selected = not button.selected
                        # Se selecionou, fecha o menu
                        if button.selected:
                            self.is_expanded = False
                        return True
        return False