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
        bar_width = 200
        bar_height = 20
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        x = screen_width - bar_width - 10
        y = screen_height - bar_height - 10
        
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
        font = pygame.font.Font(None, 24)
        text = font.render(f"Base: {int(self.health)}/{self.max_health}", True, (255, 255, 255))
        text_rect = text.get_rect(midright=(x - 10, y + bar_height//2))
        screen.blit(text, text_rect)

class SkipButton:
    def __init__(self):
        self.width = 120
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
        text = font.render("Pular Onda", True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def handle_click(self, pos, wave_active):
        if not wave_active and self.rect.collidepoint(pos):
            return True
        return False 