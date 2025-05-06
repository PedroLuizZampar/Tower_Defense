import pygame
from spell import DamageSpell, FreezeSpell, DotSpell, SlowSpell, WeaknessSpell

# Cores
WHITE = (255, 255, 255)
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)

class SpellsMenu:
    def __init__(self):
        self.is_expanded = False
        self.button_size = 50
        self.button_spacing = 10
        self.total_spells = 5  # Total de feitiços disponíveis
        self.total_width = (self.button_size * self.total_spells) + (self.button_spacing * (self.total_spells - 1))
        # Mapeamento de feitiço para tecla de atalho
        self.spell_shortcuts = {
            FreezeSpell: 'G',    # Gelo
            DotSpell: 'F',       # Fogo
            DamageSpell: 'E',    # Explosão
            SlowSpell: 'L',      # Lentidão
            WeaknessSpell: 'W',  # enfraquecimento (Weakness)
        }
        
    def draw(self, screen, spell_buttons):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calcula a posição inicial para centralizar os botões
        start_x = (screen_width - self.total_width) // 2
        y_pos = screen_height - self.button_size
        
        # Atualiza a posição dos botões
        for i, button in enumerate(spell_buttons):
            button.rect.x = start_x + i * (self.button_size + self.button_spacing)
            button.rect.y = y_pos
            button.rect.width = self.button_size
            button.rect.height = self.button_size
            
            # Desenha o botão
            pygame.draw.rect(screen, MENU_LIGHT_GRAY, button.rect)
            pygame.draw.rect(screen, WHITE, button.rect, 1)
            
            # Desenha o círculo do feitiço
            center_x = button.rect.centerx
            center_y = button.rect.centery
            circle_radius = self.button_size // 3
            
            # Define a cor baseada no cooldown
            if button.cooldown_timer > 0:
                color = button.color
                gray = (color[0] * 0.3 + color[1] * 0.59 + color[2] * 0.11) * 0.6
                spell_color = (gray, gray, gray)
            else:
                spell_color = button.color
                
            pygame.draw.circle(screen, spell_color, (center_x, center_y), circle_radius)
            
            # Se estiver selecionado, desenha borda branca mais grossa
            if button.selected:
                pygame.draw.rect(screen, WHITE, button.rect, 3)
            
            # Se estiver em cooldown, desenha o tempo restante
            if button.cooldown_timer > 0:
                cooldown_font = pygame.font.Font(None, 24)
                seconds = button.cooldown_timer // 60
                cooldown_text = cooldown_font.render(str(seconds), True, WHITE)
                text_rect = cooldown_text.get_rect(center=button.rect.center)
                screen.blit(cooldown_text, text_rect)
            
            # Desenha a letra de atalho entre parênteses abaixo do botão
            shortcut = self.spell_shortcuts.get(button.spell_class, '')
            name_font = pygame.font.Font(None, 24)
            shortcut_text = name_font.render(f'({shortcut})', True, WHITE)
            shortcut_rect = shortcut_text.get_rect(centerx=center_x, bottom=button.rect.top - 5)
            screen.blit(shortcut_text, shortcut_rect)
    
    def handle_click(self, pos, spell_buttons):
        """
        Trata o clique nos botões de feitiço.
        Retorna True se um botão foi clicado.
        """
        for button in spell_buttons:
            if button.rect.collidepoint(pos) and button.cooldown_timer <= 0:
                # Desseleciona outros botões
                for other_button in spell_buttons:
                    if other_button != button:
                        other_button.selected = False
                # Alterna seleção do botão clicado
                button.selected = not button.selected
                return True
        return False