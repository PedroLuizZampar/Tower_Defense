import pygame
import math
import os
import sys
import random
import json
from enemy import spawn_random_enemy, Enemy, SpeedEnemy, TankEnemy, ArmoredEnemy, HealerEnemy, FreezeAuraEnemy, RageEnemy, StealthEnemy, ImmunityBoss, SpeedBoss, MagnetBoss, VampiricBoss, SplitBoss
from defender import Defender, BlueDefender, RedDefender, YellowDefender, DefenderButton, BasicDefender, GreenDefender, OrangeDefender, PurpleDefender, PinkDefender
from wave_manager import WaveManager
from base import Base, SkipButton, SpeedButton, PauseButton
from menus.upgrade_menu import UpgradeMenu
from spell import DamageSpell, FreezeSpell, DotSpell, SlowSpell, WeaknessSpell, SpellButton
from mission_manager import MissionManager
from menus.defender_shop_menu import DefenderShopMenu
from menus.enemy_shop_menu import EnemyShopMenu
from menus.boss_shop_menu import BossShopMenu
from menus.spell_shop_menu import SpellShopMenu
from menus.spells_menus import SpellsMenu
from menus.pause_menu import PauseMenu
from menus.main_menu import MainMenu
from menus.defender_menu_mini import DefenderMenuMini
from menus.advantages_menu import AdvantagesMenu
from advantages import DamageAdvantage, CooldownAdvantage

# Inicialização do Pygame com flags otimizadas
pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN])

# Configurações da tela com aceleração de hardware
SCREEN_WIDTH = 1000  # Removido menu lateral
WAVE_MENU_HEIGHT = 100  # Altura do menu superior
SCREEN_HEIGHT = 650  # Altura total reduzida em 100px
GAME_HEIGHT = SCREEN_HEIGHT - WAVE_MENU_HEIGHT  # Altura do jogo ajustada
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Tower Defense")

INITIAL_GOLD = 300

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
MENU_GRAY = (40, 40, 40)
MENU_LIGHT_GRAY = (60, 60, 60)

# Carrega o background otimizado
background = pygame.image.load(os.path.join('assets', 'background.jpg')).convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, GAME_HEIGHT))

# Definição do caminho (waypoints)
PATH = [
    (0, 385),      # Início
    (170, 385),    # Primeiro ponto
    (170, 240),    # Subida 1
    (340, 240),    # Caminho reto superior
    (340, 440),    # Descida
    (645, 440),    # Caminho reto inferior
    (645, 340),    # Subida 2
    (SCREEN_WIDTH, 340)  # Final (ajustado para o novo menu lateral)
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
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, y=20)
    screen.blit(title, title_rect)
    
    # Status da onda atual
    wave_text = font.render(wave_manager.get_wave_status(), True, WHITE)
    wave_rect = wave_text.get_rect(centerx=SCREEN_WIDTH//2, y=60)
    screen.blit(wave_text, wave_rect)
    
    # Desenha o botão de pular no canto superior direito
    skip_button.rect.x = SCREEN_WIDTH - skip_button.width - 10
    skip_button.rect.y = 10
    skip_button.draw(screen, wave_manager.wave_active)

def is_valid_placement(x, y, path, game_height, defenders, is_spell=False):
    """Verifica se é uma posição válida para colocar um defensor ou feitiço"""    
    # Não pode colocar no menu superior
    if y <= WAVE_MENU_HEIGHT:
        return False
    
    # Não pode colocar no menu inferior esquerdo
    if x < 200 and y > SCREEN_HEIGHT - 80:
        return False
    
    # Se for um defensor, verifica regras específicas
    if not is_spell:
        # Verifica pontos em um raio de 20px ao redor do mouse
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            check_x = x + 18 * math.cos(rad)
            check_y = y + 13 * math.sin(rad)
            
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

def reset_game():
    """Reseta todos os elementos do jogo para o estado inicial"""
    enemies = []
    defenders = []
    spells = []
    gold = INITIAL_GOLD  # Ouro inicial
    wave_manager = WaveManager()  # Reinicia na onda 1
    mission_manager = MissionManager()  # Reinicia as missões
    base = Base()  # Base com vida cheia
    
    # Reseta os botões de defensor para estado bloqueado
    defender_buttons = [
        DefenderButton(BasicDefender, 720, mission_manager),
        DefenderButton(RedDefender, 720, mission_manager),
        DefenderButton(YellowDefender, 720, mission_manager),
        DefenderButton(GreenDefender, 720, mission_manager),
        DefenderButton(BlueDefender, 720, mission_manager),
        DefenderButton(PinkDefender, 720, mission_manager),
        DefenderButton(OrangeDefender, 720, mission_manager),
        DefenderButton(PurpleDefender, 720, mission_manager),
    ]
    
    # Reseta os botões de feitiço para nível 1
    spell_buttons = [
        SpellButton(FreezeSpell, 0),
        SpellButton(DotSpell, 0),
        SpellButton(DamageSpell, 0),
        SpellButton(SlowSpell, 0),
        SpellButton(WeaknessSpell, 0),
    ]
    
    # Cria as vantagens
    damage_advantage = DamageAdvantage()
    cooldown_advantage = CooldownAdvantage()
    
    # Cria um novo menu de vantagens com as vantagens instanciadas e configura na classe Defender
    advantages_menu = AdvantagesMenu(SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT)
    Defender.set_advantages_menu(advantages_menu)
    
    return enemies, defenders, spells, gold, wave_manager, mission_manager, base, defender_buttons, spell_buttons, advantages_menu

def close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop, spells_menu, mission_manager, spell_buttons, advantages_menu):
    enemy_shop.is_expanded = False
    defender_shop.is_expanded = False
    boss_shop.is_expanded = False
    spell_shop.is_expanded = False
    spells_menu.is_expanded = False
    mission_manager.is_expanded = False
    advantages_menu.is_expanded = False
    
    # Desseleciona todos os feitiços dos menus quando fecham
    for button in spell_buttons:
        button.selected = False
        button.rect.x = 0  # Reseta a posição dos botões

def main():
    # Lista de inimigos, defensores e feitiços
    enemies = []
    defenders = []
    spells = []

    # Sistema de ondas e recursos
    wave_manager = WaveManager()
    gold = INITIAL_GOLD  # Ouro inicial
    
    # Sistema de missões
    mission_manager = MissionManager()
    
    # Menu principal
    menu_principal = MainMenu()

    # Interface
    enemy_shop = EnemyShopMenu(SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT)
    defender_shop = DefenderShopMenu(mission_manager, SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT)
    boss_shop = BossShopMenu(SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT)
    spell_shop = SpellShopMenu(SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT)
    spells_menu = SpellsMenu()
    defender_menu_mini = DefenderMenuMini(SCREEN_WIDTH, WAVE_MENU_HEIGHT)  # Novo mini menu
    advantages_menu = AdvantagesMenu(SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT)
    Defender.set_advantages_menu(advantages_menu)  # Configura o menu de vantagens na classe Defender
    
    selected_button = None
    skip_button = SkipButton()
    speed_button = SpeedButton()
    pause_button = PauseButton()
    pause_menu = PauseMenu()
    game_paused = False
    base = Base()
    upgrade_menu = UpgradeMenu()
    
    # Interface - Botões de feitiço (removida a definição anterior de posições)
    spell_buttons = [
        SpellButton(FreezeSpell, 0),
        SpellButton(DotSpell, 0),
        SpellButton(DamageSpell, 0),
        SpellButton(SlowSpell, 0),
        SpellButton(WeaknessSpell, 0)
    ]

    selected_spell = None

    # Fonte para textos
    font = pygame.font.Font(None, 36)

    # Controle de seleção
    selected_defender = None
    immunity_boss = None

    # Carrega o jogo salvo se existir
    if menu_principal.has_save:
        try:
            import json
            with open('save_game.json', 'r') as f:
                save_data = json.load(f)
                
            # Restaura recursos
            wave_manager.set_wave(save_data['wave'])  # Usa o novo método
            gold = save_data['gold']
            base.health = save_data['base_health']
            mission_manager.orbes = save_data['orbs']
            
            # Restaura o progresso das missões
            mission_progress = save_data['mission_progress']
            mission_manager.total_kills = mission_progress['total_kills']
            mission_manager.total_waves = mission_progress['total_waves']
            mission_manager.total_spells = mission_progress['total_spells']
            mission_manager.total_upgrades = mission_progress['total_upgrades']
            
            # Restaura o estado de cada missão
            for mission, mission_data in zip(mission_manager.missions, mission_progress['missions']):
                mission.current_value = mission_data['current_value']
                mission.completed = mission_data['completed']
                mission.claimed = mission_data['claimed']
                mission.base_value = mission_data['base_value']
            
            # Restaura níveis dos feitiços
            for spell_button in spell_buttons:
                spell_name = spell_button.spell_class.__name__
                if spell_name in save_data['spell_levels']:
                    spell_button.level = save_data['spell_levels'][spell_name]
            
            # Restaura torres desbloqueadas
            for button in defender_shop.defender_buttons:
                if button.defender_class.__name__ in save_data['unlocked_defenders']:
                    button.unlocked = True
            
            # Restaura os defensores
            for d_data in save_data['defenders']:
                x, y, defender_type, level = d_data
                defender_class = globals()[defender_type]
                defender = defender_class(x, y, wave_manager.current_wave)
                defender.level = level
                defenders.append(defender)

            # Restaura os níveis das vantagens
            if 'advantages_levels' in save_data:
                advantages_menu.damage_advantage.level = save_data['advantages_levels']['damage']
                advantages_menu.cooldown_advantage.level = save_data['advantages_levels']['cooldown']
        except:
            # Se houver algum erro ao carregar, começa um novo jogo
            print("Erro ao carregar jogo salvo. Iniciando novo jogo.")
            wave_manager = WaveManager()
            gold = 250
            mission_manager = MissionManager()
            base = Base()

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
            if event.type == pygame.KEYDOWN:
                # Adiciona suporte para teclas numéricas e atalhos de feitiços
                if not game_paused and not menu_principal.active:
                    # Verifica os atalhos dos feitiços
                    pressed_key = event.unicode.upper()
                    for button in spell_buttons:
                        if pressed_key == spells_menu.spell_shortcuts.get(button.spell_class, ''):
                            # Desseleciona outros botões de feitiço
                            for other_button in spell_buttons:
                                if other_button != button:
                                    other_button.selected = False
                            # Alterna seleção do botão atual
                            button.selected = not button.selected
                            # Desseleciona defensores se houver
                            if selected_defender:
                                selected_defender.selected = False
                                selected_defender = None
                            if selected_button:
                                selected_button.selected = False
                                selected_button = None
                            break
                    
                    # Verifica atalhos dos defensores (código existente)
                    new_button = defender_menu_mini.handle_key(event.key, defender_shop.defender_buttons, gold)
                    # Desseleciona se clicar no mesmo botão
                    if new_button and new_button == selected_button:
                        new_button.selected = False
                        selected_button = None
                    else:
                        selected_button = new_button
                        if selected_button:
                            # Fecha todos os menus quando seleciona por atalho
                            close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop,
                                          spells_menu, mission_manager, spell_buttons, advantages_menu)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Verifica clique no menu principal
                if menu_principal.active:
                    action = menu_principal.handle_click(mouse_pos)
                    if action == "new":
                        # Reseta o jogo completamente
                        (enemies, defenders, spells, gold, wave_manager, 
                         mission_manager, base, defender_buttons, spell_buttons, advantages_menu) = reset_game()
                        
                        # Atualiza os menus com os novos botões
                        defender_shop = DefenderShopMenu(mission_manager, SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_MENU_HEIGHT)
                        defender_shop.defender_buttons = defender_buttons
                        
                        menu_principal.active = False
                        continue
                    elif action == "load":
                        menu_principal.active = False
                        continue

                # Verifica clique no botão de pausa
                if pause_button.handle_click(mouse_pos):
                    if selected_button:
                        selected_button = False
                    game_paused = True
                    continue

                # Se o jogo estiver pausado, verifica apenas cliques no menu de pausa
                if game_paused:
                    action = pause_menu.handle_click(mouse_pos)
                    if action == "resume":
                        game_paused = False
                    elif action == "quit":
                        # Atualiza o menu principal para mostrar que existe um save
                        menu_principal.has_save = True
                        menu_principal.active = True
                        game_paused = False
                    continue

                # Verifica clique no botão de velocidade
                if speed_button.handle_click(mouse_pos):
                    if selected_button:
                        selected_button.selected = False
                    continue
                    
                # Verifica clique no botão de pular
                if skip_button.handle_click(mouse_pos, wave_manager.wave_active):
                    if selected_button:
                        selected_button.selected = False
                    wave_manager.skip_preparation()
                    continue
                    
                # Verifica clique nas missões
                if mission_manager.handle_click(mouse_pos):
                    if selected_button:
                        selected_button.selected = False
                    if mission_manager.is_expanded:
                        close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop, spells_menu, mission_manager, spell_buttons, advantages_menu)
                        mission_manager.is_expanded = True
                    continue
                    
                # Verifica clique no menu de inimigos
                if enemy_shop.handle_click(mouse_pos):
                    if selected_button:
                        selected_button.selected = False
                    if enemy_shop.is_expanded:
                        close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop, spells_menu, mission_manager, spell_buttons, advantages_menu)
                        enemy_shop.is_expanded = True
                    continue
                    
                # Verifica clique no menu de defensores
                button, was_header_click = defender_shop.handle_click(mouse_pos, gold)
                if was_header_click:
                    if selected_button:
                        selected_button.selected = False
                    if defender_shop.is_expanded:
                        close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop, spells_menu, mission_manager, spell_buttons, advantages_menu)
                        defender_shop.is_expanded = True
                    continue
                if button:
                    # Se já tinha um botão selecionado, desseleciona
                    if selected_button and selected_button != button:
                        selected_button.selected = False
                    selected_button = button
                    continue
                    
                # Verifica clique no menu de chefões
                if boss_shop.handle_click(mouse_pos):
                    if selected_button:
                        selected_button.selected = False
                    if boss_shop.is_expanded:
                        close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop, spells_menu, mission_manager, spell_buttons, advantages_menu)
                        boss_shop.is_expanded = True
                    continue
                    
                # Verifica clique no menu de feitiços
                if spell_shop.handle_click(mouse_pos, spell_buttons, mission_manager):
                    if selected_button:
                        selected_button.selected = False
                    if spell_shop.is_expanded:
                        close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop,
                                      spells_menu, mission_manager, spell_buttons, advantages_menu)
                        spell_shop.is_expanded = True
                    continue
                
                # Verifica clique nos botões de feitiço (atualizado)
                if spells_menu.handle_click(mouse_pos, spell_buttons):
                    # Desseleciona defensor e botão de defensor
                    if selected_defender:
                        selected_defender.selected = False
                        selected_defender = None
                    if selected_button:
                        selected_button.selected = False
                        selected_button = None
                    continue
                    
                # Verifica clique nos botões de upgrade/venda
                action, value = upgrade_menu.handle_click(mouse_pos, selected_defender, gold, current_wave)
                if action == "upgrade":
                    gold -= value
                    selected_defender.upgrade()
                    mission_manager.update_tower_upgrades()  # Atualiza missão de melhorias
                    continue
                elif action == "sell":
                    gold += value
                    defenders.remove(selected_defender)
                    selected_defender = None
                    continue
                    
                # Verifica clique no menu de upgrades (antes de checar outros menus)
                gold_gained = advantages_menu.handle_click(mouse_pos, mission_manager)
                if gold_gained > 0:
                    gold += gold_gained
                    continue  # Adiciona continue aqui para evitar processamento duplo
                if advantages_menu.is_expanded:
                    if selected_button:
                        selected_button.selected = False
                    close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop, 
                                  spells_menu, mission_manager, spell_buttons, advantages_menu)
                    advantages_menu.is_expanded = True
                    continue
                    
                # Se um botão estiver selecionado e tem ouro suficiente, adiciona defensor
                if selected_button and selected_button.selected and gold >= selected_button.cost:
                    # Verifica se o ponto é válido para colocação
                    if is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders):
                        defenders.append(selected_button.defender_class(mouse_pos[0], mouse_pos[1], current_wave))
                        gold -= selected_button.cost
                        selected_button.selected = False
                        selected_button = None
                        # Mantém o menu de defensores aberto
                        defender_shop.is_expanded = True
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
                
                # Se um feitiço estiver selecionado e o mouse está numa posição válida
                for button in spell_buttons:
                    if button.selected and button.cooldown_timer <= 0:
                        # Verifica se o mouse está em uma posição válida para usar o feitiço
                        is_valid = is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders, is_spell=True)
                        if is_valid:
                            # Para feitiços, apenas verifica se clicou em uma posição válida
                            spell = button.spell_class(mouse_pos[0], mouse_pos[1])
                            spell.level = button.level
                            spells.append(spell)
                            button.start_cooldown()
                            button.selected = False
                            mission_manager.update_spell_use()

                # Se nenhum elemento foi clicado e não está no menu principal ou pausado,
                # verifica se clicou fora dos menus para fechá-los
                if (not menu_principal.active and not game_paused and
                    mouse_pos[1] > WAVE_MENU_HEIGHT):  # Só considera cliques abaixo do menu de ondas
                    
                    # Área onde os menus são renderizados
                    menus_clicked = False
                    
                    # Verifica se clicou em algum menu
                    if enemy_shop.is_expanded and enemy_shop.rect.collidepoint(mouse_pos):
                        menus_clicked = True
                    if defender_shop.is_expanded and defender_shop.rect.collidepoint(mouse_pos):
                        menus_clicked = True
                    if boss_shop.is_expanded and boss_shop.rect.collidepoint(mouse_pos):
                        menus_clicked = True
                    if spell_shop.is_expanded and spell_shop.rect.collidepoint(mouse_pos):
                        menus_clicked = True
                    if spells_menu.is_expanded and spells_menu.rect.collidepoint(mouse_pos):
                        menus_clicked = True
                    if mission_manager.is_expanded and mission_manager.header_rect and mission_manager.header_rect.collidepoint(mouse_pos):
                        menus_clicked = True
                    if advantages_menu.is_expanded and advantages_menu.rect.collidepoint(mouse_pos):
                        menus_clicked = True
                        
                    # Se não clicou em nenhum menu e algum está aberto, fecha todos
                    if not menus_clicked and (
                        enemy_shop.is_expanded or defender_shop.is_expanded or
                        boss_shop.is_expanded or spell_shop.is_expanded or
                        spells_menu.is_expanded or mission_manager.is_expanded or advantages_menu.is_expanded
                    ):
                        close_all_menus(enemy_shop, defender_shop, boss_shop, spell_shop,
                                      spells_menu, mission_manager, spell_buttons, advantages_menu)

        # Se o jogo estiver pausado, não atualiza a lógica do jogo
        if not game_paused and not menu_principal.active:
            # Atualização da onda
            wave_manager.update()
            
            # Atualização dos feitiços
            for spell in spells[:]:  # Usa uma cópia da lista para poder modificá-la durante a iteração
                update_enemy_result = spell.update(enemies)

                # AQUI É ONDE PASSAMOS OS INIMIGOS PARA OS FEITIÇOS (PASSAR TAMBÉM OS DEFENSORES)
                
                if update_enemy_result == "died":
                    # Se o feitiço matou inimigos, dá a recompensa
                    for enemy in spell.killed_enemies:
                        if not enemy.reward_given:
                            # Usa diretamente a recompensa definida na classe do inimigo
                            gold += enemy.__class__.REWARD
                            enemy.reward_given = True
                            mission_manager.update_kills()
                            
                            # Adiciona orbes para bosses
                            if isinstance(enemy, (ImmunityBoss, SpeedBoss, MagnetBoss, VampiricBoss, SplitBoss)):
                                mission_manager.orbes += 1
                            
                            if enemy in enemies:  # Verifica se o inimigo ainda está na lista
                                enemies.remove(enemy)
                elif not update_enemy_result:  # Se o feitiço terminou
                    spells.remove(spell)
            
            # Atualiza os cooldowns dos botões de feitiço
            for button in spell_buttons:
                button.update()
            
            # Atualização dos defensores e seus projéteis
            for defender in defenders:
                if isinstance(defender, YellowDefender):
                    defender.update(enemies, defenders)  # Passa a lista de defensores para o YellowDefender
                else:
                    defender.update(enemies)
                # Atualiza os projéteis
                for projectile in defender.projectiles[:]:  # Usa uma cópia da lista para poder modificá-la
                    if projectile.move():  # Se o projétil atingiu o alvo
                        if projectile.target in enemies:  # Se o alvo ainda está vivo
                            damage_result = projectile.target.take_damage(projectile.damage)
                            if damage_result:  # Se o inimigo morreu
                                if not projectile.target.reward_given:
                                    gold += projectile.target.REWARD
                                    projectile.target.reward_given = True
                                    mission_manager.update_kills()
                                    if isinstance(projectile.target, (ImmunityBoss, SpeedBoss, MagnetBoss, VampiricBoss, SplitBoss)):
                                        mission_manager.orbes += 3
                                enemies.remove(projectile.target)
                        defender.projectiles.remove(projectile)
            
            # Spawn de inimigos
            spawn_result = wave_manager.should_spawn_enemy()
            if spawn_result:
                if spawn_result == "immunity_boss":
                    immunity_boss = ImmunityBoss(PATH, wave_manager)
                    immunity_boss.set_enemies_list(enemies)
                    enemies.append(immunity_boss)
                elif spawn_result == "speed_boss":
                    speed_boss = SpeedBoss(PATH, wave_manager)
                    speed_boss.set_enemies_list(enemies)
                    enemies.append(speed_boss)
                elif spawn_result == "magnet_boss":
                    magnet_boss = MagnetBoss(PATH, wave_manager)
                    magnet_boss.set_enemies_list(enemies)
                    enemies.append(magnet_boss)
                elif spawn_result == "vampiric_boss":
                    vampiric_boss = VampiricBoss(PATH, wave_manager)
                    vampiric_boss.set_enemies_list(enemies)
                    enemies.append(vampiric_boss)
                elif spawn_result == "split_boss":
                    split_boss = SplitBoss(PATH, wave_manager)
                    split_boss.set_enemies_list(enemies)
                    enemies.append(split_boss)
                else:
                    enemy, is_special = spawn_random_enemy(PATH, wave_manager)
                    enemy.set_enemies_list(enemies)
                    enemies.append(enemy)
                
            # Atualização dos inimigos
            for enemy in enemies[:]:
                if isinstance(enemy, MagnetBoss):
                    enemy._all_defenders = defenders  # Passa a referência dos defensores para o boss
                if isinstance(enemy, FreezeAuraEnemy):
                    enemy._all_defenders = defenders  # Passa a referência dos defensores para o inimigo gelado
                enemy.set_enemies_list(enemies)  # Mantém o código existente
                move_result = enemy.move()
                
                # Primeiro verifica se morreu por DoT
                if move_result == "died":  # Se morreu por DoT
                    if not enemy.reward_given:
                        gold += enemy.__class__.REWARD
                        enemy.reward_given = True
                        mission_manager.update_kills()
                        if isinstance(enemy, (ImmunityBoss, SpeedBoss, MagnetBoss, VampiricBoss, SplitBoss)):
                            mission_manager.orbes += 3
                    enemies.remove(enemy)
                    continue
                
                # Depois verifica se chegou ao final do caminho
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
            
            # Verifica se a onda terminou
            if wave_manager.check_wave_complete(enemies):
                # Salva o estado atual do jogo
                game_state = {
                    'wave': wave_manager.current_wave,
                    'gold': gold,
                    'defenders': defenders,
                    'enemies': enemies,
                    'base': base,
                    'mission_manager': mission_manager,
                    'spell_buttons': spell_buttons,
                    'defender_shop': defender_shop,
                    'advantages_menu': advantages_menu  # Adiciona o menu de vantagens
                }
                wave_manager.save_game_state(game_state)

                if not wave_manager.start_next_wave():
                    # Jogador venceu o jogo
                    running = False
                    print("Parabéns! Você completou todas as ondas!")
                else:
                    mission_manager.update_wave(wave_manager.current_wave - 1)  # Atualiza contagem de ondas
        
        # Desenho
        screen.fill(MENU_GRAY)
        
        # Desenha o menu principal se ativo
        if menu_principal.active:
            menu_principal.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            continue

        # Desenha o menu superior de ondas
        draw_wave_menu(screen, wave_manager, skip_button)
        
        # Desenha o background após o menu lateral e superior
        screen.blit(background, (0, WAVE_MENU_HEIGHT))

        # Desenha o mini menu de defensores logo abaixo do menu de ondas
        defender_menu_mini.draw(screen, defender_shop.defender_buttons, gold)
        
        # Desenha todos os inimigos
        for enemy in enemies:
            enemy.draw(screen)
            
        # Desenha todos os feitiços ativos
        for spell in spells:
            spell.draw(screen)
        
        # Desenha todos os defensores
        for defender in defenders:
            defender.draw(screen)
        
        # Desenha os menus laterais
        enemy_shop.draw(screen, wave_manager)
        defender_shop.draw(screen, gold, selected_button)
        boss_shop.draw(screen, wave_manager)
        spell_shop.draw(screen, spell_buttons, mission_manager)
        spells_menu.draw(screen, spell_buttons)
        
        # Desenha o menu de upgrades (adicione antes de desenhar o menu de missões)
        advantages_menu.draw(screen, mission_manager)
        
        # Desenha os botões de feitiço usando o novo sistema de mini menu
        spells_menu.draw(screen, spell_buttons)
        
        # Desenha a prévia do feitiço selecionado
        for button in spell_buttons:
            if button.selected:
                button.draw_preview(screen, mouse_pos[0], mouse_pos[1], is_valid_placement, PATH, GAME_HEIGHT)
        
        # Se um botão de defensor estiver selecionado, mostra a prévia
        if selected_button and selected_button.selected:
            # Verifica se a posição é válida
            is_valid = is_valid_placement(mouse_pos[0], mouse_pos[1], PATH, GAME_HEIGHT, defenders)
            
            # Desenha o range (vermelho se inválido, cinza se válido)
            color = (255, 0, 0, 128) if not is_valid else (200, 200, 200, 128)
            range_surface = pygame.Surface((selected_button.defender_class.RANGE * 2, selected_button.defender_class.RANGE * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, color, (selected_button.defender_class.RANGE, selected_button.defender_class.RANGE), selected_button.defender_class.RANGE)
            screen.blit(range_surface, (mouse_pos[0] - selected_button.defender_class.RANGE, mouse_pos[1] - selected_button.defender_class.RANGE))
            
            # Desenha o retângulo menor com a mesma cor do range
            preview_size = 30  # Tamanho do retângulo de preview
            preview_surface = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)
            pygame.draw.rect(preview_surface, color, (0, 0, preview_size, preview_size))
            screen.blit(preview_surface, (mouse_pos[0] - preview_size//2, mouse_pos[1] - preview_size//2))
            
            # Desenha a prévia do defensor
            selected_button.defender_class.draw_preview(screen, mouse_pos[0], mouse_pos[1], is_valid)
        
        # Desenha o menu de upgrade se houver um defensor selecionado
        if selected_defender:
            upgrade_menu.draw(screen, selected_defender, gold, current_wave)
            
        # Desenha a barra de vida da base
        base.draw(screen)
        
        # Desenha o menu de missões por último para ficar sempre visível
        mission_manager.draw(screen)
        
        # Desenha o texto de ouro e orbes no canto inferior esquerdo
        font = pygame.font.Font(None, 28)
        info_menu_rect = pygame.Rect(0, SCREEN_HEIGHT - 70, 180, 70)
        pygame.draw.rect(screen, MENU_GRAY, info_menu_rect)
        pygame.draw.rect(screen, WHITE, info_menu_rect, 2)
        
        gold_text = font.render(f"Ouro: {gold}", True, (255, 215, 0))
        screen.blit(gold_text, (20, SCREEN_HEIGHT - 60))
        
        orb_text = font.render(f"Orbes: {mission_manager.orbes}", True, (50, 255, 50))
        screen.blit(orb_text, (20, SCREEN_HEIGHT - 30))
        
        # Desenha o botão de velocidade
        speed_button.draw(screen)
        
        # Desenha o botão de pausa
        pause_button.draw(screen)

        # Se o jogo estiver pausado, desenha o menu de pausa
        if game_paused:
            pause_menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()