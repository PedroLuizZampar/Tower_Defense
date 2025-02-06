import pygame
import math
import os
import sys
import random
from enemy import spawn_random_enemy, Enemy, SpeedEnemy, TankEnemy, ArmoredEnemy, HealerEnemy
from defender import Defender, BlueDefender, RedDefender, YellowDefender, DefenderButton, BasicDefender
from wave_manager import WaveManager
from base import Base, SkipButton
from upgrade_menu import UpgradeMenu
from enemy_status import EnemyStatusMenu
from spell import DamageSpell, FreezeSpell, DotSpell, SpellButton
from mission_manager import MissionManager  # Importa o gerenciador de missões

# Inicialização do Pygame
pygame.init()

# Configurações da tela
ENEMY_MENU_WIDTH = 300  # Largura do menu lateral
SCREEN_WIDTH = 1000 + ENEMY_MENU_WIDTH  # 1000 para o jogo + menu lateral
WAVE_MENU_HEIGHT = 100  # Altura do menu superior
SCREEN_HEIGHT = 850  # Diminuído para reduzir altura da loja
GAME_HEIGHT = 600
SHOP_HEIGHT = 100  # Altura da loja reduzida
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)

# Carrega o background
background = pygame.image.load(os.path.join('assets', 'background.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH - ENEMY_MENU_WIDTH, GAME_HEIGHT))

# Definição do caminho (waypoints)
PATH = [
    (ENEMY_MENU_WIDTH, 430),      # Início (ajustado para começar após o menu)
    (ENEMY_MENU_WIDTH + 160, 430),    # Primeiro ponto
    (ENEMY_MENU_WIDTH + 160, 250),    # Subida 1
    (ENEMY_MENU_WIDTH + 365, 250),    # Caminho reto superior
    (ENEMY_MENU_WIDTH + 365, 480),    # Descida
    (ENEMY_MENU_WIDTH + 630, 480),    # Caminho reto inferior
    (ENEMY_MENU_WIDTH + 630, 365),    # Subida 2
    (SCREEN_WIDTH, 365)  # Final
]

def is_point_on_path(x, y, path, margin=30):
    """Verifica se um ponto está próximo do caminho"""
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        
        # Calcula a distância do ponto até o segmento de linha
        line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_length == 0:
            continue
            
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_length**2)))
        
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        distance = math.sqrt((x - proj_x)**2 + (y - proj_y)**2)
        
        if distance < margin:
            return True
            
    return False

def draw_shop_menu(screen, gold):
    # Desenha o fundo do menu da loja
    menu_rect = pygame.Rect(ENEMY_MENU_WIDTH, GAME_HEIGHT, SCREEN_WIDTH - ENEMY_MENU_WIDTH, SHOP_HEIGHT)
    pygame.draw.rect(screen, MENU_GRAY, menu_rect)
    
    # Desenha uma linha separadora horizontal entre o jogo e a loja
    pygame.draw.line(screen, WHITE, (ENEMY_MENU_WIDTH, GAME_HEIGHT), (SCREEN_WIDTH, GAME_HEIGHT), 2)
    
    # Desenha uma linha separadora vertical entre o menu de inimigos e a loja
    pygame.draw.line(screen, WHITE, (ENEMY_MENU_WIDTH, GAME_HEIGHT), (ENEMY_MENU_WIDTH, SCREEN_HEIGHT), 2)
    
    # Desenha o título da loja
    font = pygame.font.Font(None, 36)
    title = font.render("LOJA DE DEFENSORES", True, WHITE)
    title_rect = title.get_rect(midtop=(SCREEN_WIDTH // 2 - 180, GAME_HEIGHT + 50))
    screen.blit(title, title_rect)
    
    # Desenha o ouro
    gold_text = font.render(f"Ouro: {gold}", True, (255, 215, 0))
    gold_rect = gold_text.get_rect(topright=(SCREEN_WIDTH - 20, GAME_HEIGHT + 10))
    screen.blit(gold_text, gold_rect)

def draw_wave_menu(screen, wave_manager, skip_button):
    """Desenha o menu superior com informações da onda"""
    # Desenha o fundo do menu
    menu_rect = pygame.Rect(0, 0, SCREEN_WIDTH, WAVE_MENU_HEIGHT)
    pygame.draw.rect(screen, MENU_GRAY, menu_rect)
    
    # Desenha uma linha separadora
    pygame.draw.line(screen, WHITE, (0, WAVE_MENU_HEIGHT), (SCREEN_WIDTH, WAVE_MENU_HEIGHT), 2)
    
    # Título "ONDAS"
    font = pygame.font.Font(None, 36)
    title = font.render("ONDAS", True, WHITE)
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2 + 100, y=20)
    screen.blit(title, title_rect)
    
    # Status da onda atual
    wave_text = font.render(wave_manager.get_wave_status(), True, WHITE)
    wave_rect = wave_text.get_rect(centerx=SCREEN_WIDTH//2 + 100, y=60)
    screen.blit(wave_text, wave_rect)
    
    # Desenha o botão de pular
    skip_button.rect.x = SCREEN_WIDTH - skip_button.width - 50
    skip_button.rect.y = WAVE_MENU_HEIGHT//2 - skip_button.height//2
    skip_button.draw(screen, wave_manager.wave_active)

def is_valid_placement(x, y, path, game_height, defenders, is_spell=False):
    """Verifica se é uma posição válida para colocar um defensor ou feitiço"""
    # Não pode colocar no menu lateral
    if x <= ENEMY_MENU_WIDTH:
        return False
    
    # Não pode colocar no menu superior
    if y <= WAVE_MENU_HEIGHT:
        return False
    
    # Não pode colocar na área da loja
    if y >= GAME_HEIGHT:
        return False
    
    # Se for um defensor, verifica regras específicas
    if not is_spell:
        # Verifica pontos em um raio de 20px ao redor do mouse
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            check_x = x + 25 * math.cos(rad)
            check_y = y + 25 * math.sin(rad)
            
            # Não pode colocar no caminho
            if is_point_on_path(check_x, check_y, path):
                return False
        
        # Não pode colocar muito próximo de outros defensores
        if Defender.is_too_close(x, y, defenders):
            return False
    
    return True

def draw_enemy_path(screen, path):
    """Desenha o caminho dos inimigos com uma cor semi-transparente"""
    pass  # Removida a visualização do caminho

def main():
    # Lista de inimigos, defensores e feitiços
    enemies = []
    defenders = []
    spells = []  # Nova lista para feitiços ativos

    # Sistema de ondas e recursos
    wave_manager = WaveManager()
    gold = 200  # Ouro inicial
    
    # Sistema de missões
    mission_manager = MissionManager()

    # Calcula as posições dos botões para centralizá-los
    button_spacing = 120
    total_width = button_spacing * 2
    start_x = ENEMY_MENU_WIDTH + 30  # Ajustado para começar após o menu lateral

    # Interface
    defender_buttons = [
        DefenderButton(BasicDefender, start_x, mission_manager),
        DefenderButton(BlueDefender, start_x + button_spacing, mission_manager),
        DefenderButton(RedDefender, start_x + button_spacing * 2, mission_manager),
        DefenderButton(YellowDefender, start_x + button_spacing * 3, mission_manager)
    ]
    selected_button = None
    skip_button = SkipButton()
    base = Base()
    upgrade_menu = UpgradeMenu()
    enemy_menu = EnemyStatusMenu(ENEMY_MENU_WIDTH)

    # Calcula as posições dos botões de feitiço
    spell_spacing = 50
    spell_start_x = ENEMY_MENU_WIDTH + 400  # Posição inicial dos botões de feitiço
    
    # Interface
    spell_buttons = [
        SpellButton(FreezeSpell, spell_start_x),
        SpellButton(DotSpell, spell_start_x + spell_spacing),
        SpellButton(DamageSpell, spell_start_x + spell_spacing * 2),
    ]
    selected_spell = None

    # Fonte para textos
    font = pygame.font.Font(None, 36)

    # Controle de seleção
    selected_defender = None

    # Game loop
    running = True
    clock = pygame.time.Clock()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_wave = wave_manager.current_wave
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            enemy_menu.handle_scroll(event)  # Adiciona tratamento do scroll do menu de inimigos
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Verifica clique no botão de pular
                if skip_button.handle_click(mouse_pos, wave_manager.wave_active):
                    wave_manager.skip_preparation()
                    continue
                    
                # Verifica clique nas missões
                if mission_manager.handle_click(mouse_pos):
                    continue
                    
                # Verifica clique nos botões de feitiço
                clicked_spell = False
                for button in spell_buttons:
                    if button.handle_click(mouse_pos, gold):
                        # Desseleciona outros botões
                        for other_button in spell_buttons:
                            if other_button != button:
                                other_button.selected = False
                        selected_spell = button if button.selected else None
                        clicked_spell = True
                        # Desseleciona defensor e botão de defensor
                        if selected_defender:
                            selected_defender.selected = False
                            selected_defender = None
                        if selected_button:
                            selected_button.selected = False
                            selected_button = None
                        break
                        
                if clicked_spell:
                    continue
                    
                # Verifica clique nos botões de defensor
                clicked_button = False
                for button in defender_buttons:
                    if button.handle_click(mouse_pos, gold):
                        # Desseleciona outros botões
                        for other_button in defender_buttons:
                            if other_button != button:
                                other_button.selected = False
                        selected_button = button if button.selected else None
                        clicked_button = True
                        # Desseleciona defensor atual
                        if selected_defender:
                            selected_defender.selected = False
                            selected_defender = None
                        break
                        
                if clicked_button:
                    continue
                    
                # Verifica clique nos botões de upgrade/venda
                action, value = upgrade_menu.handle_click(mouse_pos, selected_defender, gold, current_wave)
                if action == "upgrade":
                    gold -= value
                    selected_defender.upgrade()
                    continue
                elif action == "sell":
                    gold += value
                    defenders.remove(selected_defender)
                    selected_defender = None
                    continue
                    
                # Se um botão estiver selecionado e tem ouro suficiente, adiciona defensor
                if selected_button and selected_button.selected and gold >= selected_button.cost:
                    # Verifica se o ponto é válido para colocação
                    if is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders):
                        defenders.append(selected_button.defender_class(mouse_pos[0], mouse_pos[1], current_wave))
                        gold -= selected_button.cost
                        selected_button.selected = False
                        selected_button = None
                else:
                    # Verifica clique em defensores existentes
                    clicked_defender = None
                    for defender in defenders:
                        if defender.handle_click(mouse_pos):
                            clicked_defender = defender
                            break
                            
                    # Desseleciona o defensor anterior
                    if selected_defender and selected_defender != clicked_defender:
                        selected_defender.selected = False
                        
                    selected_defender = clicked_defender
                
                # Se um feitiço estiver selecionado e tem ouro suficiente
                if selected_spell and selected_spell.selected:
                    # Verifica se o ponto é válido para colocação
                    if is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders, is_spell=True):
                        if isinstance(selected_spell.spell_class, DamageSpell):
                            spells.append(selected_spell.spell_class(mouse_pos[0], mouse_pos[1], wave_manager))
                        else:
                            spells.append(selected_spell.spell_class(mouse_pos[0], mouse_pos[1]))
                        selected_spell.start_cooldown()  # Inicia o cooldown do feitiço
                        selected_spell = None
                    continue

        # Atualização da onda
        wave_manager.update()
        
        # Atualização dos feitiços
        for spell in spells[:]:  # Usa uma cópia da lista para poder modificá-la durante a iteração
            spell_result = spell.update(enemies)
            
            # Se o feitiço matou um inimigo
            if spell_result == "died":
                # Identifica o tipo do inimigo e adiciona o ouro
                for enemy in enemies[:]:  # Verifica todos os inimigos
                    if enemy.health <= 0 and not enemy.reward_given:  # Se morreu e não deu recompensa
                        # Identifica o tipo do inimigo
                        if isinstance(enemy, SpeedEnemy):
                            enemy_type = 'speed'
                        elif isinstance(enemy, TankEnemy):
                            enemy_type = 'tank'
                        elif isinstance(enemy, ArmoredEnemy):
                            enemy_type = 'armored'
                        elif isinstance(enemy, HealerEnemy):
                            enemy_type = 'healer'
                        else:
                            enemy_type = 'normal'
                        
                        # Adiciona o ouro
                        gold += wave_manager.enemy_defeated(enemy_type)
                        enemy.reward_given = True
                        enemies.remove(enemy)
                        mission_manager.update_kills()  # Atualiza contagem de kills
            elif not spell_result:  # Se o feitiço terminou
                spells.remove(spell)
        
        # Atualiza os cooldowns dos botões de feitiço
        for button in spell_buttons:
            button.update()
        
        # Spawn de inimigos
        if wave_manager.should_spawn_enemy():
            enemy, is_special = spawn_random_enemy(PATH, wave_manager)
            enemies.append(enemy)
            
        # Atualização dos inimigos
        for enemy in enemies[:]:
            move_result = enemy.move()  # Agora pode retornar True, False, "died" ou "heal"
            
            # Primeiro verifica se chegou ao final do caminho
            if move_result is True:  # True significa que chegou ao final do caminho
                enemies.remove(enemy)
                if base.take_damage(10):  # Inimigo atingiu a base
                    running = False  # Game over se a base for destruída
                continue
            
            # Depois verifica cura
            if isinstance(enemy, HealerEnemy) and move_result == "heal":
                # Cria efeito visual de cura
                heal_effect = pygame.Surface((enemy.heal_radius * 2, enemy.heal_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(heal_effect, (*enemy.COLOR, 100), 
                                (enemy.heal_radius, enemy.heal_radius), enemy.heal_radius)
                screen.blit(heal_effect, (int(enemy.x - enemy.heal_radius), 
                                        int(enemy.y - enemy.heal_radius)))
                # Cura todos os inimigos próximos
                for other_enemy in enemies:
                    if other_enemy != enemy:
                        dx = other_enemy.x - enemy.x
                        dy = other_enemy.y - enemy.y
                        distance = math.sqrt(dx ** 2 + dy ** 2)
                        if distance <= enemy.heal_radius:
                            other_enemy.health = min(other_enemy.max_health, 
                                                   other_enemy.health + enemy.heal_amount)
            
            # Verifica morte por DoT
            elif move_result == "died":  # Morreu por dano ao longo do tempo
                # Identifica o tipo do inimigo e adiciona o ouro
                if isinstance(enemy, SpeedEnemy):
                    enemy_type = 'speed'
                elif isinstance(enemy, TankEnemy):
                    enemy_type = 'tank'
                elif isinstance(enemy, ArmoredEnemy):
                    enemy_type = 'armored'
                elif isinstance(enemy, HealerEnemy):
                    enemy_type = 'healer'
                else:
                    enemy_type = 'normal'
                
                if not enemy.reward_given:
                    gold += wave_manager.enemy_defeated(enemy_type)
                    enemy.reward_given = True
                    mission_manager.update_kills()
                enemies.remove(enemy)
        
        # Atualização dos defensores
        for defender in defenders:
            if isinstance(defender, YellowDefender):
                defender.update(enemies, defenders)
            else:
                defender.update(enemies)
                
            # Verifica os projéteis que atingiram inimigos
            for projectile in defender.projectiles[:]:
                if projectile.move():
                    if projectile.target and hasattr(projectile.target, 'take_damage'):
                        # Se o inimigo morreu com este projétil
                        damage_result = projectile.target.take_damage(projectile.damage)
                        
                        if damage_result:  # Se morreu normalmente
                            # Identifica o tipo do inimigo
                            if isinstance(projectile.target, SpeedEnemy):
                                enemy_type = 'speed'
                            elif isinstance(projectile.target, TankEnemy):
                                enemy_type = 'tank'
                            elif isinstance(projectile.target, ArmoredEnemy):
                                enemy_type = 'armored'
                            elif isinstance(projectile.target, HealerEnemy):
                                enemy_type = 'healer'
                            else:
                                enemy_type = 'normal'
                            
                            # Adiciona o ouro e remove o inimigo
                            if not projectile.target.reward_given:  # Verifica se já deu recompensa
                                gold += wave_manager.enemy_defeated(enemy_type)
                                projectile.target.reward_given = True  # Marca que já deu recompensa
                                mission_manager.update_kills()  # Atualiza contagem de kills quando inimigo morre por projétil
                            if projectile.target in enemies:  # Verifica se o inimigo ainda está na lista
                                enemies.remove(projectile.target)
                            if projectile.target == defender.current_target:
                                defender.current_target = None
                    
                    defender.projectiles.remove(projectile)
            
        # Verifica se a onda terminou
        if wave_manager.check_wave_complete(enemies):
            if not wave_manager.start_next_wave():
                # Jogador venceu o jogo
                running = False
                print("Parabéns! Você completou todas as ondas!")
            else:
                mission_manager.update_wave(wave_manager.current_wave - 1)  # Atualiza contagem de ondas
        
        # Desenho
        screen.fill(MENU_GRAY)
        
        # Desenha o menu superior de ondas
        draw_wave_menu(screen, wave_manager, skip_button)
        
        # Desenha o menu lateral de inimigos
        enemy_menu.draw(screen, wave_manager)
        
        # Desenha uma linha separadora vertical
        pygame.draw.line(screen, WHITE, (ENEMY_MENU_WIDTH, WAVE_MENU_HEIGHT), (ENEMY_MENU_WIDTH, SCREEN_HEIGHT), 2)
        
        # Desenha o background após o menu lateral e superior
        screen.blit(background, (ENEMY_MENU_WIDTH, WAVE_MENU_HEIGHT))
        
        # Desenha todos os inimigos
        for enemy in enemies:
            enemy.draw(screen)
            
        # Desenha todos os feitiços ativos
        for spell in spells:
            spell.draw(screen)
        
        # Desenha todos os defensores
        for defender in defenders:
            defender.draw(screen)
            
        # Desenha o menu da loja
        draw_shop_menu(screen, gold)
        
        # Desenha os botões de feitiço primeiro (camada inferior)
        for button in spell_buttons:
            button.draw(screen, gold)
        
        # Desenha a interface dos defensores por último (camada superior)
        for button in defender_buttons:
            button.draw(screen, gold)
            # Se o mouse estiver sobre o botão, mostra as estatísticas
            if button.rect.collidepoint(mouse_pos):
                # Posiciona o menu de estatísticas acima do botão
                stats_x = button.rect.x
                stats_y = button.rect.y - 130  # Altura do menu de stats + margem
                upgrade_menu.draw_preview(screen, button.defender_class, stats_x, stats_y)
        
        # Se um feitiço estiver selecionado, mostra a prévia
        if selected_spell and selected_spell.selected:
            # Verifica se a posição é válida
            is_valid = is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders, is_spell=True)
            if is_valid:
                # Desenha o raio do feitiço
                color = (*selected_spell.spell_class.COLOR, 128)
                spell_surface = pygame.Surface((selected_spell.radius * 2, selected_spell.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(spell_surface, color, (selected_spell.radius, selected_spell.radius), selected_spell.radius)
                screen.blit(spell_surface, (mouse_pos[0] - selected_spell.radius, mouse_pos[1] - selected_spell.radius))
        
        # Se um botão de defensor estiver selecionado, mostra a prévia
        if selected_button and selected_button.selected:
            # Verifica se a posição é válida
            is_valid = is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders)
            
            # Desenha o range (vermelho se inválido, cinza se válido)
            color = (255, 0, 0, 128) if not is_valid else (200, 200, 200, 128)
            range_surface = pygame.Surface((selected_button.defender_class.RANGE * 2, selected_button.defender_class.RANGE * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, color, (selected_button.defender_class.RANGE, selected_button.defender_class.RANGE), selected_button.defender_class.RANGE)
            screen.blit(range_surface, (mouse_pos[0] - selected_button.defender_class.RANGE, mouse_pos[1] - selected_button.defender_class.RANGE))
            
            # Desenha o círculo menor com a mesma cor do range
            small_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(small_surface, color, (25, 25), 25)
            screen.blit(small_surface, (mouse_pos[0] - 25, mouse_pos[1] - 25))
            
            # Desenha a prévia do defensor
            selected_button.defender_class.draw_preview(screen, mouse_pos[0], mouse_pos[1], is_valid)
        
        # Desenha o menu de upgrade se houver um defensor selecionado
        if selected_defender:
            upgrade_menu.draw(screen, selected_defender, gold, current_wave)
            
        # Desenha a barra de vida da base
        base.draw(screen)
        
        # Desenha o menu de missões por último para ficar sempre visível
        mission_manager.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 