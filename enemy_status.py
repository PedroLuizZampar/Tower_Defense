import pygame

class EnemyStatusMenu:
    def __init__(self, width=300):
        self.width = width
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.background_color = (40, 40, 40)
        self.text_color = (255, 255, 255)
        self.health_color = (0, 255, 0)
        self.spacing = 140  # Espaçamento entre cards
        self.scroll_y = 0  # Posição do scroll
        self.scroll_speed = 20  # Velocidade do scroll
        self.max_visible_height = 800  # Altura máxima visível
        
    def handle_scroll(self, event):
        if event.type == pygame.MOUSEWHEEL:
            # Scroll para cima (negativo) ou para baixo (positivo)
            self.scroll_y = max(min(self.scroll_y + event.y * self.scroll_speed, 0), 
                              -self.get_total_height() + self.max_visible_height)
                              
    def get_total_height(self):
        """Calcula a altura total necessária para todos os cards"""
        from enemy import Enemy, TankEnemy, SpeedEnemy, ArmoredEnemy, HealerEnemy
        return 120 + len([Enemy, TankEnemy, SpeedEnemy, ArmoredEnemy, HealerEnemy]) * self.spacing
        
    def get_enemy_stats(self, enemy_class, wave_manager):
        """Retorna as estatísticas do inimigo sem criar uma instância"""
        base_health = enemy_class.BASE_HEALTH
        total_health = round(base_health * wave_manager.get_health_increase(), 1)
        base_speed = enemy_class.BASE_SPEED
        radius = 12 if not hasattr(enemy_class, 'RADIUS') else enemy_class.RADIUS
        return total_health, base_speed, radius
        
    def draw_enemy_card(self, screen, enemy_class, y_pos, wave_manager):
        # Pega as estatísticas do inimigo
        total_health, speed, radius = self.get_enemy_stats(enemy_class, wave_manager)
        
        # Card background
        card_height = 120  # Aumentado a altura do card
        pygame.draw.rect(screen, self.background_color, (10, y_pos, self.width - 20, card_height))
        pygame.draw.rect(screen, self.text_color, (10, y_pos, self.width - 20, card_height), 1)
        
        # Nome do inimigo
        name_text = self.title_font.render(enemy_class.NAME, True, self.text_color)
        name_rect = name_text.get_rect(x=20, y=y_pos + 10)
        screen.blit(name_text, name_rect)
        
        # Ícone do inimigo (círculo com a cor do inimigo)
        pygame.draw.circle(screen, enemy_class.COLOR, 
                         (45, y_pos + 60), 
                         radius)
        
        # Estatísticas
        stats_x = 80
        # Vida
        health_text = self.font.render(f"Vida: {int(total_health)}", True, self.text_color)
        screen.blit(health_text, (stats_x, y_pos + 35))
        
        # Velocidade
        speed_text = self.font.render(f"Velocidade: {speed}", True, self.text_color)
        screen.blit(speed_text, (stats_x, y_pos + 60))
        
        # Características especiais
        special_text = None
        if enemy_class.NAME == "Tanque":
            special_text = "Resistente a Congelamento"
        elif enemy_class.NAME == "Célere":
            special_text = "Resistente a Queimaduras"
        elif enemy_class.NAME == "Blindado":
            special_text = "-30% Dano Recebido"
        elif enemy_class.NAME == "Dividido":
            special_text = "Divide-se ao Morrer"
        elif enemy_class.NAME == "Curador":
            special_text = "Cura Aliados Próximos"
            
        if special_text:
            spec_text = self.font.render(special_text, True, self.health_color)
            screen.blit(spec_text, (stats_x, y_pos + 85))  # Ajustado a posição do texto especial
        
    def draw(self, screen, wave_manager):
        # Cria uma superfície para o conteúdo scrollável
        content_height = self.get_total_height()
        content_surface = pygame.Surface((self.width, content_height), pygame.SRCALPHA)
        
        # Desenha os cards dos inimigos na superfície de conteúdo
        from enemy import Enemy, TankEnemy, SpeedEnemy, ArmoredEnemy, HealerEnemy
        enemy_classes = [Enemy, TankEnemy, SpeedEnemy, ArmoredEnemy, HealerEnemy]
        
        # Título do menu (fixo, não rola)
        title = self.title_font.render("INIMIGOS", True, self.text_color)
        title_rect = title.get_rect(centerx=self.width//2, y=40)
        screen.blit(title, title_rect)
        
        # Desenha cada card na superfície de conteúdo
        for i, enemy_class in enumerate(enemy_classes):
            self.draw_enemy_card(content_surface, enemy_class, 10 + i * self.spacing, wave_manager)
        
        # Cria uma superfície de visualização com clipping
        view_rect = pygame.Rect(0, 100, self.width, self.max_visible_height - 100)
        screen.blit(content_surface, (0, 100), area=pygame.Rect(0, -self.scroll_y, self.width, view_rect.height))
        
        # Desenha a linha divisória vertical
        pygame.draw.line(screen, self.text_color, (self.width, 0), (self.width, 800), 2)