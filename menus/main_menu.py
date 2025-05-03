import pygame
import os

WHITE = (255, 255, 255)
RED = (255, 0, 0)
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)

class MainMenu:
    def __init__(self):
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        self.font = pygame.font.Font(None, 40)
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        # Botão Novo Jogo
        self.new_game_rect = pygame.Rect(
            screen_width//2 - button_width//2,
            screen_height//2 - button_height - button_spacing//2,
            button_width,
            button_height
        )
        self.new_game_text = self.font.render("NOVO JOGO", True, (255, 255, 255))
        self.new_game_text_rect = self.new_game_text.get_rect(center=self.new_game_rect.center)
        
        # Botão Carregar Jogo
        self.load_game_rect = pygame.Rect(
            screen_width//2 - button_width//2,
            screen_height//2 + button_spacing//2,
            button_width,
            button_height
        )
        self.load_game_text_rect = self.new_game_text.get_rect(center=self.load_game_rect.center)
        self.active = True
        self.has_save = self.check_save_exists()
        
    def check_save_exists(self):
        """Verifica se existe um arquivo de save"""
        return os.path.exists('save_game.json')
        
    def draw(self, screen):
        if self.active:
            # Preenche a tela com cinza
            screen.fill(MENU_GRAY)
            
            # Desenha o botão Novo Jogo
            pygame.draw.rect(screen, MENU_LIGHT_GRAY, self.new_game_rect)
            pygame.draw.rect(screen, WHITE, self.new_game_rect, 2)
            screen.blit(self.new_game_text, self.new_game_text_rect)
            
            # Desenha o botão Carregar Jogo
            button_color = MENU_LIGHT_GRAY if self.has_save else (60, 60, 60)
            text_color = WHITE if self.has_save else (150, 150, 150)
            load_text = self.font.render("CARREGAR", True, text_color)
            load_text_rect = load_text.get_rect(center=self.load_game_rect.center)
            
            pygame.draw.rect(screen, button_color, self.load_game_rect)
            pygame.draw.rect(screen, WHITE, self.load_game_rect, 2)
            screen.blit(load_text, load_text_rect)
            
    def handle_click(self, pos):
        if self.active:
            if self.new_game_rect.collidepoint(pos):
                self.active = False
                try:
                    # Remove o arquivo de save ao iniciar um novo jogo
                    if os.path.exists('save_game.json'):
                        os.remove('save_game.json')
                except:
                    pass
                return "new"
            elif self.has_save and self.load_game_rect.collidepoint(pos):
                self.active = False
                return "load"
        return None
