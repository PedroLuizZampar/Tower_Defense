import pygame
from spell import DamageSpell, FreezeSpell, DotSpell, SlowSpell, WeaknessSpell, SpellButton

# Cores
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)
WHITE = (255, 255, 255)

class SpellShopMenu:
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
        self.spells_per_page = 4
        self.prev_button_rect = None
        self.next_button_rect = None
        self.spells = [FreezeSpell, DotSpell, DamageSpell, SlowSpell, WeaknessSpell]
        self.upgrade_buttons = {}
        
    def handle_click(self, pos, spell_buttons, mission_manager):
        # Verifica clique no header
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            return True
            
        # Se o menu estiver expandido
        if self.is_expanded and self.rect and self.rect.collidepoint(pos):
            # Verifica clique nos botões de paginação
            if self.prev_button_rect and self.prev_button_rect.collidepoint(pos):
                if self.current_page > 0:
                    self.current_page -= 1
                return True
                
            if self.next_button_rect and self.next_button_rect.collidepoint(pos):
                total_pages = (len(self.spells) + self.spells_per_page - 1) // self.spells_per_page
                if self.current_page < total_pages - 1:
                    self.current_page += 1
                return True
                
            # Verifica clique nos botões de upgrade
            for spell_class, upgrade_button in self.upgrade_buttons.items():
                if upgrade_button.collidepoint(pos):
                    # Encontra o botão correspondente
                    for button in spell_buttons:
                        if button.spell_class == spell_class:
                            if button.level < spell_class.MAX_LEVEL and button.can_upgrade(mission_manager.orbes):
                                upgrade_cost = button.get_upgrade_cost()
                                mission_manager.orbes -= upgrade_cost
                                button.upgrade()
                            return True
            return True
            
        return False
        
    def draw(self, screen, spell_buttons, mission_manager):
        # Limpa os botões de upgrade para evitar ações em páginas anteriores
        self.upgrade_buttons.clear()
        
        # Desenha o cabeçalho (sempre visível)
        header_width = 40
        header_height = 104
        header_x = self.SCREEN_WIDTH - header_width
        header_y = self.WAVE_MENU_HEIGHT + 306
        self.header_rect = pygame.Rect(header_x, header_y, header_width, header_height)
        
        # Define o rect principal do menu
        self.rect = pygame.Rect(self.SCREEN_WIDTH - self.width - header_width, self.WAVE_MENU_HEIGHT, 
                               self.width, self.height)
        
        # Desenha o botão da aba
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        # Desenha o texto "FEITIÇOS" na vertical
        font = pygame.font.Font(None, 18)
        text = font.render("Feitiços", True, WHITE)
        text_vertical = pygame.transform.rotate(text, 270)
        text_rect = text_vertical.get_rect(center=self.header_rect.center)
        screen.blit(text_vertical, text_rect)
        
        # Se expandido, desenha o resto do menu
        if self.is_expanded:
            pygame.draw.rect(screen, MENU_GRAY, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            
            font = pygame.font.Font(None, 28)
            text = font.render("FEITIÇOS", True, WHITE)
            text_rect = text.get_rect(center=(self.rect.centerx, self.WAVE_MENU_HEIGHT + 25))
            screen.blit(text, text_rect)
            
            # Draw only the spells for the current page
            start_index = self.current_page * self.spells_per_page
            end_index = min(start_index + self.spells_per_page, len(self.spells))
            
            y_offset = self.WAVE_MENU_HEIGHT + 45
            font = pygame.font.Font(None, 16)
            font_title = pygame.font.Font(None, 24)
            font_upgrade = pygame.font.Font(None, 20)
            
            for i, spell_class in enumerate(self.spells[start_index:end_index]):
                # Encontra o botão correspondente
                spell_button = None
                for button in spell_buttons:
                    if button.spell_class == spell_class:
                        spell_button = button
                        break
                
                if not spell_button:
                    continue
                
                # Fundo do card do feitiço
                card_height = 110  # Aumentado para acomodar o botão de upgrade
                card_rect = pygame.Rect(self.rect.x + 10, y_offset, self.width - 20, card_height)
                pygame.draw.rect(screen, (40, 40, 40), card_rect)
                pygame.draw.rect(screen, WHITE, card_rect, 1)
                
                # Nome do feitiço e nível
                name_text = font_title.render(f"{spell_class.NAME} Nv.{spell_button.level}", True, WHITE)
                name_rect = name_text.get_rect(x=card_rect.x + 10, y=y_offset + 10)
                screen.blit(name_text, name_rect)
                
                # Cooldown
                cooldown_text = font.render(f"Recarga: {spell_class.COOLDOWN // 60}s", True, WHITE)
                cooldown_rect = cooldown_text.get_rect(right=card_rect.right - 10, y=y_offset + 10)
                screen.blit(cooldown_text, cooldown_rect)
                
                # Ícone do feitiço (círculo com a cor do feitiço)
                pygame.draw.circle(screen, spell_class.COLOR,
                                 (card_rect.x + 30, y_offset + 50),
                                 15)
                
                # Estatísticas atuais
                current_stats = spell_button.get_current_stats()
                stats_y = y_offset + 35
                for stat_name, value in current_stats.items():
                    stat_text = font.render(f"{stat_name}: {value}", True, WHITE)
                    screen.blit(stat_text, (card_rect.x + 60, stats_y))
                    stats_y += 15
                
                # Descrição e imunidades
                if spell_class == FreezeSpell:
                    stats_text = font.render(f"Raio: {spell_class.RADIUS}px", True, WHITE)
                    screen.blit(stats_text, (card_rect.x + 60, y_offset + 35))
                    desc_text = font.render("Congela inimigos na área", True, (50, 255, 50))
                    screen.blit(desc_text, (card_rect.x + 60, y_offset + 50))
                    immune_text = font.render("Inimigos Tanque são imunes", True, (255, 100, 100))
                    screen.blit(immune_text, (card_rect.x + 60, y_offset + 65))
                elif spell_class == SlowSpell:
                    stats_text = font.render(f"Raio: {spell_class.RADIUS}px", True, WHITE)
                    screen.blit(stats_text, (card_rect.x + 60, y_offset + 35))
                    desc_text = font.render("Desacelera inimigos na área", True, (50, 255, 50))
                    screen.blit(desc_text, (card_rect.x + 60, y_offset + 50))
                    immune_text = font.render("Inimigos Tanque são imunes", True, (255, 100, 100))
                    screen.blit(immune_text, (card_rect.x + 60, y_offset + 65))
                elif spell_class == WeaknessSpell:
                    duration = (spell_button.spell_class.WEAKNESS_DURATION + (spell_button.level - 1) * spell_button.spell_class.DURATION_INCREASE) / 60
                    stats_text = font.render(f"Raio: {spell_class.RADIUS}px | Duração: {duration:.1f}s", True, WHITE)
                    screen.blit(stats_text, (card_rect.x + 60, y_offset + 35))
                    desc_text = font.render("Enfraquece inimigos em 30%", True, (50, 255, 50))
                    screen.blit(desc_text, (card_rect.x + 60, y_offset + 50))
                    immune_text = font.render(f"por {duration:.1f} segundos", True, (50, 255, 50))
                    screen.blit(immune_text, (card_rect.x + 60, y_offset + 65))
                elif spell_class == DotSpell:
                    damage = spell_button.spell_class.DOT_DAMAGE
                    for _ in range(spell_button.level - 1):
                        damage *= (1 + spell_button.spell_class.DAMAGE_INCREASE_PERCENT)
                    duration = (spell_button.spell_class.DOT_DURATION + ((spell_button.level) // 5 * 60)) / 60
                    stats_text = font.render(f"Raio: {spell_class.RADIUS}px | Dano: {int(damage)}/s", True, WHITE)
                    screen.blit(stats_text, (card_rect.x + 60, y_offset + 35))
                    desc_text = font.render(f"Causa dano por {duration:.1f} segundos", True, (50, 255, 50))
                    screen.blit(desc_text, (card_rect.x + 60, y_offset + 50))
                    immune_text = font.render("Inimigos Velozes são imunes", True, (255, 100, 100))
                    screen.blit(immune_text, (card_rect.x + 60, y_offset + 65))
                elif spell_class == DamageSpell:
                    damage = spell_button.spell_class.DAMAGE
                    for _ in range(spell_button.level - 1):
                        damage *= (1 + spell_button.spell_class.DAMAGE_INCREASE_PERCENT)
                    stats_text = font.render(f"Raio: {spell_class.RADIUS}px | Dano: {int(damage)}", True, WHITE)
                    screen.blit(stats_text, (card_rect.x + 60, y_offset + 35))
                    desc_text = font.render("Dano instantâneo na área", True, (50, 255, 50))
                    screen.blit(desc_text, (card_rect.x + 60, y_offset + 50))
                    immune_text = font.render("-30% de dano em Blindados", True, (255, 100, 100))
                    screen.blit(immune_text, (card_rect.x + 60, y_offset + 65))

                # Botão de upgrade
                if spell_button.level < spell_class.MAX_LEVEL:
                    upgrade_cost = spell_button.get_upgrade_cost()
                    can_upgrade = spell_button.can_upgrade(mission_manager.orbes)
                    
                    upgrade_button = pygame.Rect(card_rect.x + 10, y_offset + card_height - 30, 
                                               self.width - 40, 25)
                    self.upgrade_buttons[spell_class] = upgrade_button
                    
                    # Cor do botão baseada se pode melhorar ou não
                    button_color = (50, 200, 50) if can_upgrade else (100, 100, 100)
                    text_color = WHITE if can_upgrade else (150, 150, 150)
                    
                    pygame.draw.rect(screen, button_color, upgrade_button)
                    pygame.draw.rect(screen, WHITE, upgrade_button, 1)
                    
                    # Texto do botão
                    upgrade_text = font_upgrade.render(f"Melhorar ({upgrade_cost} Orbes)", True, text_color)
                    text_rect = upgrade_text.get_rect(center=upgrade_button.center)
                    screen.blit(upgrade_text, text_rect)
                else:
                    max_text = font_upgrade.render("NÍVEL MÁXIMO", True, (50, 255, 50))
                    text_rect = max_text.get_rect(centerx=card_rect.centerx, y=y_offset + card_height - 25)
                    screen.blit(max_text, text_rect)
                
                y_offset += card_height + 10
            
            # Draw pagination controls if needed
            if len(self.spells) > self.spells_per_page:
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
                next_color = MENU_LIGHT_GRAY if end_index < len(self.spells) else (60, 60, 60)
                pygame.draw.rect(screen, next_color, self.next_button_rect)
                pygame.draw.rect(screen, WHITE, self.next_button_rect, 1)
                
                next_text = font_back_next.render(">", True, WHITE if end_index < len(self.spells) else (150, 150, 150))
                next_rect = next_text.get_rect(center=self.next_button_rect.center)
                screen.blit(next_text, next_rect)
                
                # Page indicator
                total_pages = (len(self.spells) + self.spells_per_page - 1) // self.spells_per_page
                page_text = font_upgrade.render(f"{self.current_page + 1}/{total_pages}", True, WHITE)
                page_rect = page_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 10)
                screen.blit(page_text, page_rect)
