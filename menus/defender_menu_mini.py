import pygame

class DefenderMenuMini:
    def __init__(self, SCREEN_WIDTH, WAVE_MENU_HEIGHT):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.width = SCREEN_WIDTH - 600
        self.height = 40  # Altura do mini menu
        self.y = WAVE_MENU_HEIGHT  # Posição Y logo abaixo do menu de ondas
        self.item_size = 30  # Tamanho de cada quadrado de defensor
        self.padding = 10  # Espaçamento entre os itens
        
        # Calcula a posição X para centralizar o menu na tela
        self.x = (SCREEN_WIDTH - self.width) // 2
        
        # Cores
        self.LOCKED_COLOR = (180, 50, 50, 180)  # Vermelho transparente para bloqueados
        self.NO_GOLD_COLOR = (128, 128, 128, 180)  # Cinza transparente para sem ouro
        self.MENU_BACKGROUND = (40, 40, 40)  # Cor de fundo do menu
        
        # Font para os números
        self.font = pygame.font.Font(None, 20)
        
        # Superfície com alpha para os quadrados dos defensores
        self.overlay_surface = pygame.Surface((self.item_size, self.item_size), pygame.SRCALPHA)

    def draw(self, screen, defender_buttons, gold):
        # Desenha o fundo do menu centralizado
        pygame.draw.rect(screen, self.MENU_BACKGROUND, (self.x, self.y, self.width, self.height))
        
        # Calcula a largura total necessária para todos os defensores
        total_width = len(defender_buttons) * (self.item_size + self.padding) - self.padding
        # Calcula o X inicial para centralizar os itens dentro do menu
        start_x = self.x + (self.width - total_width) // 2
        
        # Desenha cada defensor no mini menu
        x = start_x
        for i, button in enumerate(defender_buttons):
            # Número do atalho (1-9)
            shortcut_num = str(i + 1)
            
            # Desenha o quadrado do defensor
            defender_rect = pygame.Rect(x, self.y + 5, self.item_size, self.item_size)
            
            # Reseta a superfície de overlay
            self.overlay_surface.fill((0, 0, 0, 0))
            
            if not button.unlocked:
                # Defensor bloqueado - vermelho transparente
                pygame.draw.rect(self.overlay_surface, self.LOCKED_COLOR, (0, 0, self.item_size, self.item_size))
            elif gold < button.cost:
                # Sem ouro suficiente - cinza transparente
                pygame.draw.rect(self.overlay_surface, self.NO_GOLD_COLOR, (0, 0, self.item_size, self.item_size))
            else:
                # Defensor disponível - cor normal do defensor
                defender_color = button.defender_class.COLOR
                pygame.draw.rect(screen, defender_color, defender_rect)
            
            # Desenha o overlay
            screen.blit(self.overlay_surface, defender_rect)
            
            # Desenha a borda do quadrado
            pygame.draw.rect(screen, (255, 255, 255), defender_rect, 1)
            
            # Só desenha o número se o defensor estiver desbloqueado
            if button.unlocked:
                num_text = self.font.render(shortcut_num, True, (255, 255, 255))
                # Posiciona o número no centro superior do defensor
                num_rect = num_text.get_rect(centerx=x + self.item_size/2, centery=self.y + 20)
                screen.blit(num_text, num_rect)
            
            x += self.item_size + self.padding

    def handle_key(self, key, defender_buttons, gold):
        """Lida com as teclas numéricas pressionadas"""
        # Converte a tecla para índice (1-9 -> 0-8)
        try:
            if key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                      pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                index = key - pygame.K_1  # Converte a tecla para índice
                
                if index < len(defender_buttons):
                    button = defender_buttons[index]
                    
                    # Só seleciona se estiver desbloqueado e tiver ouro suficiente
                    if button.unlocked and gold >= button.cost:
                        # Desseleciona todos os outros botões
                        for other_button in defender_buttons:
                            if other_button != button:
                                other_button.selected = False
                        
                        # Seleciona o botão atual
                        button.selected = True
                        return button
                        
        except:
            pass
        
        return None