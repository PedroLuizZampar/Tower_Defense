import pygame

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
