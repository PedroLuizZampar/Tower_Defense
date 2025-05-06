import pygame

class UpgradeMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 28)
        self.background_color = (40, 40, 40)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.red_color = (255, 0, 0)
        
    def get_defender_stats(self, defender):
        if not defender:
            return None
            
        # Calcula o DPS (Dano por Segundo)
        frames_per_attack = defender.attack_cooldown
        attacks_per_second = 60 / frames_per_attack  # 60 frames = 1 segundo
        dps = defender.get_total_damage() * attacks_per_second
        
        return {
            "Dano": f"{defender.get_total_damage()}",
            "Vel. Ataque": f"{attacks_per_second:.2f}/s",
            "DPS": f"{dps:.1f}"
        }
        
    def draw_stats(self, screen, stats, x, y, width):
        spacing = 25
        for i, (stat_name, value) in enumerate(stats.items()):
            # Nome da estatística
            text = self.font.render(f"{stat_name}: {value}", True, self.text_color)
            text_rect = text.get_rect(x=x + 10, y=y + spacing * i)
            screen.blit(text, text_rect)
        
    def draw_preview(self, screen, defender_class, x, y):
        """Desenha uma prévia das estatísticas do defensor"""
        # Fundo do menu
        menu_width = 200
        menu_height = 120
        pygame.draw.rect(screen, self.background_color, (x, y, menu_width, menu_height))
        pygame.draw.rect(screen, self.text_color, (x, y, menu_width, menu_height), 1)
        
        # Nome do defensor
        name_text = self.title_font.render(defender_class.NAME, True, self.text_color)
        name_rect = name_text.get_rect(x=x + 10, y=y + 10)
        screen.blit(name_text, name_rect)
        
        # Estatísticas base
        stats_x = x + 10
        stats_y = y + 40
        
        # Dano base
        damage_text = self.font.render(f"Dano: {defender_class.BASE_DAMAGE}", True, self.text_color)
        screen.blit(damage_text, (stats_x, stats_y))
        
        # Velocidade de ataque
        attack_speed = 60 / defender_class.BASE_ATTACK_COOLDOWN
        speed_text = self.font.render(f"Vel. Ataque: {attack_speed:.1f}/s", True, self.text_color)
        screen.blit(speed_text, (stats_x, stats_y + 25))
        
        # DPS
        dps = defender_class.BASE_DAMAGE * attack_speed
        dps_text = self.font.render(f"DPS: {dps:.1f}", True, self.text_color)
        screen.blit(dps_text, (stats_x, stats_y + 50))

    def draw(self, screen, defender, gold, current_wave):
        """Desenha o menu de upgrade para um defensor selecionado"""
        # Fundo do menu
        menu_width = 200
        menu_height = 180
        menu_x = defender.x + 40
        menu_y = defender.y - menu_height - 20
        
        # Ajusta a posição se estiver muito perto da borda
        if menu_x + menu_width > screen.get_width():
            menu_x = defender.x - menu_width - 40
        if menu_y < 0:
            menu_y = defender.y + 40
            
        pygame.draw.rect(screen, self.background_color, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, self.text_color, (menu_x, menu_y, menu_width, menu_height), 1)
        
        # Nome do defensor e nível
        name_text = self.title_font.render(f"{defender.NAME} Nv.{defender.level}", True, self.text_color)
        name_rect = name_text.get_rect(x=menu_x + 10, y=menu_y + 10)
        screen.blit(name_text, name_rect)
        
        # Estatísticas atuais
        stats_x = menu_x + 10
        stats_y = menu_y + 40
        
        # Dano atual (já com buffs)
        damage = defender.get_total_damage()
        damage_text = self.font.render(f"Dano: {round(damage, 2)}", True, self.text_color)
        screen.blit(damage_text, (stats_x, stats_y))
        
        # Velocidade de ataque (já com buffs)
        current_attack_speed = 60 / defender.get_attack_cooldown()
        speed_text = self.font.render(f"Vel. Ataque: {current_attack_speed:.1f}/s", True, self.text_color)
        screen.blit(speed_text, (stats_x, stats_y + 25))
        
        # DPS (calculado com os valores atuais)
        dps = damage * current_attack_speed
        dps_text = self.font.render(f"DPS: {dps:.1f}", True, self.text_color)
        screen.blit(dps_text, (stats_x, stats_y + 50))
        
        # Botão de upgrade
        upgrade_cost = defender.get_upgrade_cost()
        can_upgrade = gold >= upgrade_cost
        
        upgrade_color = (50, 200, 50) if can_upgrade else (100, 100, 100)
        upgrade_text_color = self.text_color if can_upgrade else (150, 150, 150)
        
        self.upgrade_button = pygame.Rect(menu_x + 10, menu_y + menu_height - 70, 180, 30)
        pygame.draw.rect(screen, upgrade_color, self.upgrade_button)
        
        upgrade_text = self.font.render(f"Melhorar ({upgrade_cost})", True, upgrade_text_color)
        text_rect = upgrade_text.get_rect(center=self.upgrade_button.center)
        screen.blit(upgrade_text, text_rect)
        
        # Botão de venda
        sell_value = defender.get_sell_value(current_wave)
        self.sell_button = pygame.Rect(menu_x + 10, menu_y + menu_height - 35, 180, 30)
        pygame.draw.rect(screen, (200, 50, 50), self.sell_button)
        
        sell_text = self.font.render(f"Vender ({sell_value})", True, self.text_color)
        text_rect = sell_text.get_rect(center=self.sell_button.center)
        screen.blit(sell_text, text_rect)

    def handle_click(self, pos, defender, gold, current_wave):
        if not defender:
            return None, 0
            
        if hasattr(defender, 'get_upgrade_cost') and hasattr(self, 'upgrade_button'):
            upgrade_cost = defender.get_upgrade_cost()
            if self.upgrade_button.collidepoint(pos) and gold >= upgrade_cost:
                return "upgrade", upgrade_cost
                
        if hasattr(defender, 'get_sell_value') and hasattr(self, 'sell_button'):
            if self.sell_button.collidepoint(pos):
                return "sell", defender.get_sell_value(current_wave)
                
        return None, 0