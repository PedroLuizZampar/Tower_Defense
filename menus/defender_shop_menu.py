import pygame
from defender import Defender, BasicDefender, RedDefender, YellowDefender, GreenDefender, BlueDefender, PinkDefender, OrangeDefender, PurpleDefender

WHITE = (255, 255, 255)
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)

class DefenderButton:
    def __init__(self, defender_class, x_pos, mission_manager=None):
        self.width = 230
        self.height = 90
        self.defender_class = defender_class
        self.cost = defender_class.COST
        self.selected = False
        self.rect = pygame.Rect(x_pos, 0, self.width, self.height)
        self.mission_manager = mission_manager
        self.unlocked = not hasattr(defender_class, 'UNLOCK_COST')
        
    def draw(self, screen, gold, ajust):        
        if self.selected:
            rect_copy = self.rect.copy()
            pygame.draw.rect(screen, (255, 255, 255), rect_copy, 3)
        
        if not self.unlocked:
            lock_surface = pygame.Surface((self.rect.width, self.rect.height))  
            lock_surface.set_alpha(240)
            lock_surface.fill((99, 99, 99))
            screen.blit(lock_surface, (self.rect.x, self.rect.y + ajust))

            font_block = pygame.font.Font(None, 24)
            orb_text = font_block.render(f"{self.defender_class.UNLOCK_COST} Orbes", True, (50, 255, 50))
            orb_rect = orb_text.get_rect(center=(self.rect.centerx, self.rect.centery + ajust + 15))
            screen.blit(orb_text, orb_rect)
            
            lock_text = font_block.render("Bloqueado", True, (252, 25, 25))
            lock_rect = lock_text.get_rect(center=(self.rect.centerx, self.rect.centery + ajust - 15))
            screen.blit(lock_text, lock_rect)
        else:
            font = pygame.font.Font(None, 20)
            cost_text = font.render(f"Custo: {self.cost}", True, 
                                    (255, 215, 0) if gold >= self.cost else (255, 0, 0))
            cost_rect = cost_text.get_rect(x=self.rect.x + 150, centery=self.rect.top + ajust + 15)
            screen.blit(cost_text, cost_rect)

    def handle_click(self, pos, gold):
        if self.rect.collidepoint(pos):
            if not self.unlocked and hasattr(self.defender_class, 'UNLOCK_COST'):
                if self.mission_manager and self.mission_manager.orbes >= self.defender_class.UNLOCK_COST:
                    self.mission_manager.orbes -= self.defender_class.UNLOCK_COST
                    self.unlocked = True
                return False
            elif self.unlocked and gold >= self.cost:
                self.selected = not self.selected
                return True
        return False

class DefenderShopMenu:
    def __init__(self, mission_manager, screen_width, screen_height, wave_menu_height):
        self.width = 250
        self.height = screen_height - wave_menu_height
        self.screen_width = screen_width
        self.wave_menu_height = wave_menu_height
        self.is_expanded = False
        self.header_rect = None
        self.mission_manager = mission_manager
        self.selected_button = None
        self.current_page = 0  # Current page index
        self.defenders_per_page = 5  # Number of defenders per page
        self.prev_button_rect = None
        self.next_button_rect = None
        self.defender_buttons = []  # Initialize empty list first
        self.setup_buttons()  # Then call setup_buttons
        
    def setup_buttons(self):
        button_spacing = 90
        start_y = self.wave_menu_height + 30
        x_pos = self.screen_width - self.width - 30
        
        self.defender_buttons = [
            DefenderButton(BasicDefender, x_pos, self.mission_manager),
            DefenderButton(RedDefender, x_pos, self.mission_manager),
            DefenderButton(YellowDefender, x_pos, self.mission_manager),
            DefenderButton(GreenDefender, x_pos, self.mission_manager),
            DefenderButton(BlueDefender, x_pos, self.mission_manager),
            DefenderButton(PinkDefender, x_pos, self.mission_manager),
            DefenderButton(OrangeDefender, x_pos, self.mission_manager),
            DefenderButton(PurpleDefender, x_pos, self.mission_manager),
        ]
        
        # Update positions based on current page
        self.update_button_positions()
        
    def update_button_positions(self):
        button_spacing = 90
        start_y = self.wave_menu_height + 30
        start_index = self.current_page * self.defenders_per_page
        end_index = min(start_index + self.defenders_per_page, len(self.defender_buttons))
        
        for i, button in enumerate(self.defender_buttons[start_index:end_index], 0):
            button.rect.y = start_y + (i * button_spacing) + 15
            
    def draw(self, screen, gold, selected_button=None):
        header_width = 40
        header_height = 104
        header_x = self.screen_width - header_width
        self.header_rect = pygame.Rect(header_x, self.wave_menu_height, header_width, header_height)
        
        # Define o rect principal do menu
        self.rect = pygame.Rect(self.screen_width - self.width - header_width, self.wave_menu_height, 
                               self.width, self.height)
        
        if self.is_expanded:
            pygame.draw.rect(screen, MENU_GRAY, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            
            font = pygame.font.Font(None, 28)
            text = font.render("DEFENSORES", True, WHITE)
            text_rect = text.get_rect(center=(self.rect.centerx, self.wave_menu_height + 25))
            screen.blit(text, text_rect)
            
            # Draw only the defenders for the current page
            start_index = self.current_page * self.defenders_per_page
            end_index = min(start_index + self.defenders_per_page, len(self.defender_buttons))
            
            y_offset = self.wave_menu_height + 45
            font = pygame.font.Font(None, 20)
            font_title = pygame.font.Font(None, 24)
            
            for i, button in enumerate(self.defender_buttons[start_index:end_index]):
                # Fundo do card do defensor
                card_height = 90
                card_rect = pygame.Rect(self.rect.x + 10, y_offset, self.width - 20, card_height)
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
                
                # Dano e DPS já com os buffs das vantagens
                base_damage = button.defender_class.BASE_DAMAGE
                if button.defender_class.advantages_menu and button.defender_class.advantages_menu.damage_advantage:
                    damage_bonus = button.defender_class.advantages_menu.damage_advantage.get_current_bonus() / 100
                    damage = base_damage * (1 + damage_bonus)
                else:
                    damage = base_damage

                base_attack_speed = 60 / button.defender_class.BASE_ATTACK_COOLDOWN
                if button.defender_class.advantages_menu and button.defender_class.advantages_menu.cooldown_advantage:
                    cooldown_bonus = button.defender_class.advantages_menu.cooldown_advantage.get_current_bonus() / 100
                    attack_speed = base_attack_speed * (1 + cooldown_bonus)
                else:
                    attack_speed = base_attack_speed

                dps = damage * attack_speed
                damage_text = font.render(f"Dano: {round(damage, 1)}         DPS: {round(dps, 1)}", True, WHITE)
                screen.blit(damage_text, (card_rect.x + 60, y_offset + 35))

                # Range e informações adicionais
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
                elif button.defender_class == PinkDefender:
                    special_text = "Empilha o Dano"
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
            next_color = MENU_LIGHT_GRAY if end_index < len(self.defender_buttons) else (60, 60, 60)
            pygame.draw.rect(screen, next_color, self.next_button_rect)
            pygame.draw.rect(screen, WHITE, self.next_button_rect, 1)
            
            next_text = font_back_next.render(">", True, WHITE if end_index < len(self.defender_buttons) else (150, 150, 150))
            next_rect = next_text.get_rect(center=self.next_button_rect.center)
            screen.blit(next_text, next_rect)
            
            # Page indicator
            total_pages = (len(self.defender_buttons) + self.defenders_per_page - 1) // self.defenders_per_page
            page_text = font.render(f"{self.current_page + 1}/{total_pages}", True, WHITE)
            page_rect = page_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 10)
            screen.blit(page_text, page_rect)
        
        pygame.draw.rect(screen, MENU_GRAY, self.header_rect)
        pygame.draw.rect(screen, WHITE, self.header_rect, 2)
        
        font = pygame.font.Font(None, 18)
        text = pygame.font.Font(None, 18).render("Defensores", True, WHITE)
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