import pygame

class Mission:
    def __init__(self, description, target_value, reward=1):
        self.description = description
        self.target_value = target_value
        self.current_value = 0
        self.completed = False
        self.claimed = False
        self.reward = reward  # Quantidade de orbes como recompensa
        self.notification_shown = False  # Controla se a notificação está visível
        self.base_value = 0  # Valor base para controlar o progresso após reset
        
    def update(self, value):
        # Só atualiza se a missão não estiver completa
        if not self.completed:
            # Atualiza o valor atual em relação ao valor base
            self.current_value = min(value - self.base_value, self.target_value)
            
            # Verifica se completou a missão
            if self.current_value >= self.target_value:
                self.completed = True
                self.notification_shown = True
                
    def claim_reward(self):
        if self.completed and not self.claimed:
            self.claimed = True
            self.notification_shown = False
            # Atualiza o valor base para o próximo ciclo
            self.base_value += self.target_value
            # Reseta o estado para poder fazer novamente
            self.completed = False
            self.claimed = False
            # Zera o valor atual
            self.current_value = 0
            return self.reward
        return 0

class MissionManager:    
    def __init__(self):
        self.missions = [
            Mission("Elimine 25 inimigos", 25, 1),  # 1 orbe de recompensa
            Mission("Elimine 50 inimigos", 50, 1),  # 1 orbe de recompensa
            Mission("Elimine 100 inimigos", 100, 1),  # 1 orbe de recompensa
            Mission("Sobreviva 5 ondas", 5, 1),      # 1 orbe de recompensa
            Mission("Sobreviva 10 ondas", 10, 1),     # 1 orbe de recompensa
            Mission("Use feitiços 5 vezes", 5, 1),    # 1 orbe de recompensa
            Mission("Use feitiços 10 vezes", 10, 1),  # 1 orbe de recompensa
            Mission("Melhore torres 10 vezes", 10, 1) # 1 orbe de recompensa
        ]
        self.total_kills = 0
        self.current_wave = 1
        self.orbes = 0
        self.is_expanded = False  # Controla se o menu está expandido
        self.header_rect = None  # Retângulo do cabeçalho para detectar cliques
        self.current_page = 0  # Página atual
        self.missions_per_page = 4  # Número de missões por página
        self.prev_button_rect = None  # Retângulo do botão de página anterior
        self.next_button_rect = None  # Retângulo do botão de próxima página
        self.button_width = 40
        self.button_height = 30
        self.button_spacing = 200
        
    def has_notifications(self):
        """Verifica se há missões completadas não resgatadas"""
        return any(mission.notification_shown for mission in self.missions)
        
    def update_kills(self):
        # Só incrementa se a missão de kills não estiver completa
        if not self.missions[0].completed:
            self.total_kills += 1
            self.missions[0].update(self.total_kills)
        elif not self.missions[1].completed:
            self.total_kills += 1
            self.missions[1].update(self.total_kills)
        elif not self.missions[2].completed:
            self.total_kills += 1
            self.missions[2].update(self.total_kills)
        
    def update_wave(self, wave):
        # Só atualiza se a missão de ondas não estiver completa
        if not self.missions[2].completed:
            self.current_wave = wave
            self.missions[2].update(wave)
            if not self.missions[3].completed:
                self.missions[3].update(wave)
        elif not self.missions[3].completed:
            self.current_wave = wave
            self.missions[3].update(wave)

    def update_spell_use(self):
        """Incrementa o contador de uso de feitiços"""
        # Missão de 5 feitiços
        if not self.missions[5].completed:
            self.missions[5].update(self.missions[5].current_value + 1)
        # Missão de 10 feitiços
        elif not self.missions[6].completed:
            self.missions[6].update(self.missions[6].current_value + 1)
            
    def update_tower_upgrades(self):
        """Incrementa o contador de melhorias de torres"""
        if not self.missions[7].completed:
            self.missions[7].update(self.missions[7].current_value + 1)

    def draw(self, screen):
        # Configurações do quadro de missões
        panel_width = 200  # Aumentado de 180 para 200
        x = 0  # Posiciona no lado esquerdo
        
        # Desenha o cabeçalho (sempre visível)
        header_height = 40
        header_rect = pygame.Rect(x, 100, panel_width, header_height)
        self.header_rect = header_rect  # Salva para detecção de clique
        
        # Desenha o fundo do cabeçalho
        pygame.draw.rect(screen, (40, 40, 40), header_rect)
        pygame.draw.rect(screen, (255, 255, 255), header_rect, 2)
        
        # Título e orbes no cabeçalho
        font_title = pygame.font.Font(None, 24)
        title = font_title.render(f"MISSÕES", True, (255, 255, 255))
        title_rect = title.get_rect(center=header_rect.center)
        screen.blit(title, title_rect)
        
        # Desenha a notificação se houver missões completadas não resgatadas
        if self.has_notifications():
            notification_radius = 6
            pygame.draw.circle(screen, (50, 255, 50),  # Verde
                             (header_rect.right - 12, header_rect.top + 12),
                             notification_radius)
        
        # Se o menu estiver expandido, desenha o resto
        if self.is_expanded:
            panel_height = 370
            panel_rect = pygame.Rect(x, header_rect.bottom, panel_width, panel_height)
            
            # Desenha o fundo do painel
            pygame.draw.rect(screen, (40, 40, 40), panel_rect)
            pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)
            
            # Calcula o início e fim da página atual
            start_index = self.current_page * self.missions_per_page
            end_index = min(start_index + self.missions_per_page, len(self.missions))
            
            # Desenha as missões da página atual
            font = pygame.font.Font(None, 18)
            y_offset = panel_rect.top + 45  # Aumentado para dar espaço aos botões de navegação
            
            # Botões de navegação
            button_y = panel_rect.top + 10
            start_x = x + 10
            
            font_back_next = pygame.font.Font(None, 35)
            
            # Botão de página anterior
            self.prev_button_rect = pygame.Rect(start_x, button_y, self.button_width, self.button_height)
            prev_color = (100, 100, 100) if self.current_page > 0 else (60, 60, 60)
            pygame.draw.rect(screen, prev_color, self.prev_button_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.prev_button_rect, 1)
            
            prev_text = font_back_next.render("<", True, (255, 255, 255) if self.current_page > 0 else (150, 150, 150))
            prev_rect = prev_text.get_rect(center=self.prev_button_rect.center)
            screen.blit(prev_text, prev_rect)
            
            # Botão de próxima página
            self.next_button_rect = pygame.Rect(start_x + self.button_width + self.button_spacing - 100, button_y, 
                                              self.button_width, self.button_height)
            next_color = (100, 100, 100) if end_index < len(self.missions) else (60, 60, 60)
            pygame.draw.rect(screen, next_color, self.next_button_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.next_button_rect, 1)
            
            next_text = font_back_next.render(">", True, (255, 255, 255) if end_index < len(self.missions) else (150, 150, 150))
            next_rect = next_text.get_rect(center=self.next_button_rect.center)
            screen.blit(next_text, next_rect)
            
            # Indicador de página
            total_pages = (len(self.missions) + self.missions_per_page - 1) // self.missions_per_page
            page_text = font.render(f"{self.current_page + 1}/{total_pages}", True, (255, 255, 255))
            page_rect = page_text.get_rect(centerx=panel_rect.centerx, y=button_y + 8)
            screen.blit(page_text, page_rect)
            
            # Desenha as missões da página atual
            for mission in self.missions[start_index:end_index]:
                # Descrição da missão
                text = font.render(mission.description, True, (255, 255, 255))
                screen.blit(text, (x + 10, y_offset))
                
                # Progresso
                progress = f"{mission.current_value}/{mission.target_value}"
                progress_text = font.render(progress, True, (255, 255, 255))
                progress_rect = progress_text.get_rect(right=x + panel_width - 10, y=y_offset)
                screen.blit(progress_text, progress_rect)
                
                # Barra de progresso
                progress_width = 180
                progress_height = 12
                progress_x = x + 10
                progress_y = y_offset + 25
                
                # Fundo da barra
                pygame.draw.rect(screen, (100, 100, 100), 
                               (progress_x, progress_y, progress_width, progress_height))
                
                # Progresso atual
                progress_percent = min(mission.current_value / mission.target_value, 1)
                pygame.draw.rect(screen, (50, 255, 50), 
                               (progress_x, progress_y, 
                                progress_width * progress_percent, progress_height))
                
                # Botão de recompensa
                if mission.completed and not mission.claimed:
                    button_rect = pygame.Rect(x + panel_width - 100, y_offset + 40, 90, 25)
                    pygame.draw.rect(screen, (50, 200, 50), button_rect)
                    pygame.draw.rect(screen, (255, 255, 255), button_rect, 1)
                    
                    claim_text = font.render(f"Resgatar", True, (255, 255, 255))
                    text_rect = claim_text.get_rect(center=button_rect.center)
                    screen.blit(claim_text, text_rect)
                    
                    # Armazena o retângulo do botão para verificar cliques
                    mission.button_rect = button_rect
                else:
                    mission.button_rect = None
                
                y_offset += 80
            
    def handle_click(self, pos):
        """Verifica cliques nos botões de resgate e no cabeçalho"""
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            return True
            
        if self.is_expanded:
            # Verifica cliques nos botões de paginação
            if self.prev_button_rect and self.prev_button_rect.collidepoint(pos) and self.current_page > 0:
                self.current_page -= 1
                return True
                
            if self.next_button_rect and self.next_button_rect.collidepoint(pos):
                next_page_start = (self.current_page + 1) * self.missions_per_page
                if next_page_start < len(self.missions):
                    self.current_page += 1
                    return True
            
            # Verifica cliques nos botões de resgate apenas para missões da página atual
            start_index = self.current_page * self.missions_per_page
            end_index = min(start_index + self.missions_per_page, len(self.missions))
            
            for mission in self.missions[start_index:end_index]:
                if (mission.button_rect and 
                    mission.button_rect.collidepoint(pos) and 
                    mission.completed and 
                    not mission.claimed):
                    self.orbes += mission.claim_reward()
                    return True
                    
        return False