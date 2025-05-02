import pygame

class Base:
    def __init__(self):
        self.max_health = 100
        self.health = self.max_health
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
        
    def draw(self, screen):
        # Desenha a barra de vida da base no canto inferior direito
        bar_width = 150
        bar_height = 20
        screen_width = pygame.display.get_surface().get_width()
        x = screen_width - bar_width - 10
        y = 75
        
        # Fundo da barra (vermelho)
        pygame.draw.rect(screen, (255, 0, 0),
                        (x, y, bar_width, bar_height))
        
        # Frente da barra (verde)
        health_width = (self.health / self.max_health) * bar_width
        pygame.draw.rect(screen, (0, 255, 0),
                        (x, y, health_width, bar_height))
        
        # Borda da barra
        pygame.draw.rect(screen, (255, 255, 255),
                        (x, y, bar_width, bar_height), 2)
        
        # Texto da vida
        font = pygame.font.Font(None, 18)
        text = font.render(f"Base: {int(self.health)}/{self.max_health}", True, (255, 255, 255))
        text_rect = text.get_rect(midright=(x - 5, y + bar_height//2))
        screen.blit(text, text_rect)

class SkipButton:
    def __init__(self):
        self.width = 150
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)  # Posição será definida no draw_wave_menu
        
    def draw(self, screen, wave_active):
        if not wave_active:
            color = (50, 200, 50)  # Verde quando pode pular
            text_color = (255, 255, 255)  # Texto branco
        else:
            color = (60, 60, 60)  # Cinza escuro quando não pode
            text_color = (150, 150, 150)  # Texto cinza claro
            
        # Desenha o botão com borda
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # Borda branca
        
        # Texto do botão
        font = pygame.font.Font(None, 28)
        text = font.render("Próxima Onda", True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def handle_click(self, pos, wave_active):
        if not wave_active and self.rect.collidepoint(pos):
            return True
        return False

class GameSpeed:
    _instance = None
    
    def __init__(self):
        self.current_speed = 1  # Velocidade atual (1, 2 ou 4)
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GameSpeed()
        return cls._instance
    
    @property
    def current_multiplier(self):
        return self.current_speed
        
    def set_speed(self, speed):
        """Define a velocidade do jogo (1x, 2x, 5x ou 10x)"""
        if speed in [1, 2, 5, 10]:
            self.current_speed = speed

class PauseButton:
    def __init__(self):
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(screen_width - self.width, screen_height - self.height, self.width, self.height)
        
    def draw(self, screen):
        # Desenha o botão com borda
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Desenha o símbolo de pausa (duas barras verticais)
        bar_width = 5
        bar_height = 20
        spacing = 8
        pygame.draw.rect(screen, (255, 255, 255),
                        (self.rect.centerx - spacing - bar_width//2,
                         self.rect.centery - bar_height//2,
                         bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255),
                        (self.rect.centerx + spacing - bar_width//2,
                         self.rect.centery - bar_height//2,
                         bar_width, bar_height))
        
    def handle_click(self, pos):
        return self.rect.collidepoint(pos)

class PauseMenu:
    def __init__(self):
        self.screen_width = pygame.display.get_surface().get_width()
        self.screen_height = pygame.display.get_surface().get_height()
        
        # Configurações da janela de pausa
        self.window_width = 300
        self.window_height = 200
        self.window_rect = pygame.Rect(
            (self.screen_width - self.window_width) // 2,
            (self.screen_height - self.window_height) // 2,
            self.window_width,
            self.window_height
        )
        
        # Configurações dos botões
        button_width = 200
        button_height = 40
        button_spacing = 75
        
        # Botão Retomar
        self.resume_button = pygame.Rect(
            self.window_rect.centerx - button_width//2,
            self.window_rect.centery - button_height//2,
            button_width,
            button_height
        )
        
        # Botão Abandonar
        self.quit_button = pygame.Rect(
            self.window_rect.centerx - button_width//2,
            self.window_rect.centery + button_spacing//2,
            button_width,
            button_height
        )

    def save_game_state(self, game_state):
        """Salva o estado do jogo quando o jogador abandona"""
        import json
        import os
        
        # Prepara os dados das missões
        missions_data = []
        for mission in game_state['mission_manager'].missions:
            mission_data = {
                'current_value': mission.current_value,
                'completed': mission.completed,
                'claimed': mission.claimed,
                'base_value': mission.base_value
            }
            missions_data.append(mission_data)
            
        save_data = {
            'wave': game_state['wave'],
            'gold': game_state['gold'],
            'base_health': game_state['base'].health,
            'orbs': game_state['mission_manager'].orbes,
            'spell_levels': {spell.spell_class.__name__: spell.level for spell in game_state['spell_buttons']},
            'defenders': [(d.x, d.y, d.__class__.__name__, d.level) for d in game_state['defenders']],
            'unlocked_defenders': [d.defender_class.__name__ for d in game_state['defender_shop'].defender_buttons if d.unlocked],
            'mission_progress': {
                'total_kills': game_state['mission_manager'].total_kills,
                'total_waves': game_state['mission_manager'].total_waves,
                'total_spells': game_state['mission_manager'].total_spells,
                'total_upgrades': game_state['mission_manager'].total_upgrades,
                'missions': missions_data
            }
        }
        
        save_file = 'save_game.json'
        with open(save_file, 'w') as f:
            json.dump(save_data, f)
        
    def draw(self, screen):
        # Escurece a tela de fundo
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Desenha a janela de pausa
        pygame.draw.rect(screen, (40, 40, 40), self.window_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.window_rect, 2)
        
        # Título "PAUSADO"
        font_title = pygame.font.Font(None, 48)
        title = font_title.render("PAUSADO", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.window_rect.centerx, 
                                  top=self.window_rect.top + 10)
        screen.blit(title, title_rect)
        
        # Desenha os botões
        font = pygame.font.Font(None, 32)
        
        # Botão Retomar
        pygame.draw.rect(screen, (50, 200, 50), self.resume_button)
        pygame.draw.rect(screen, (255, 255, 255), self.resume_button, 2)
        resume_text = font.render("Retomar", True, (255, 255, 255))
        resume_rect = resume_text.get_rect(center=self.resume_button.center)
        screen.blit(resume_text, resume_rect)
        
        # Botão Abandonar
        pygame.draw.rect(screen, (200, 50, 50), self.quit_button)
        pygame.draw.rect(screen, (255, 255, 255), self.quit_button, 2)
        quit_text = font.render("Abandonar", True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=self.quit_button.center)
        screen.blit(quit_text, quit_rect)
    
    def handle_click(self, pos):
        if self.resume_button.collidepoint(pos):
            return "resume"
        elif self.quit_button.collidepoint(pos):
            return "quit"
        return None

class SpeedButton:
    def __init__(self):
        self.button_width = 50
        self.button_height = 40
        self.spacing = 5  # Espaço entre os botões
        self.y = 10  # Posição Y dos botões
        
        # Cria os três botões
        self.buttons = [
            {
                'rect': pygame.Rect(10, self.y, self.button_width, self.button_height),
                'speed': 1,
                'text': "1x"
            },
            {
                'rect': pygame.Rect(10 + self.button_width + self.spacing, self.y, 
                                  self.button_width, self.button_height),
                'speed': 2,
                'text': "2x"
            },
            {
                'rect': pygame.Rect(10 + (self.button_width + self.spacing) * 2, self.y, 
                                  self.button_width, self.button_height),
                'speed': 5,
                'text': "5x"
            },
            {
                'rect': pygame.Rect(10 + (self.button_width + self.spacing) * 3, self.y, 
                                  self.button_width, self.button_height),
                'speed': 10,
                'text': "10x"
            }
        ]
        self.game_speed = GameSpeed.get_instance()
        
    def draw(self, screen):
        font = pygame.font.Font(None, 28)
        
        for button in self.buttons:
            # Define a cor baseada se está selecionado
            if self.game_speed.current_speed == button['speed']:
                color = (50, 200, 50)  # Verde quando selecionado
            else:
                color = (60, 60, 60)  # Cinza quando não selecionado
                
            # Desenha o botão com borda
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, (255, 255, 255), button['rect'], 2)
            
            # Texto do botão
            text_surface = font.render(button['text'], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button['rect'].center)
            screen.blit(text_surface, text_rect)
        
    def handle_click(self, pos):
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                self.game_speed.set_speed(button['speed'])
                return True
        return False