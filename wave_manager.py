import random
from base import GameSpeed

class WaveManager:
    MAX_WAVES = 50
    BASE_ENEMIES = 5  # Número base de inimigos na primeira onda
    BASE_SPAWN_INTERVAL = 110  # Intervalo base entre spawns (em frames)
    PREPARATION_TIME = 10 * 60  # 10 segundos em frames
    INITIAL_PREPARATION_TIME = 60 * 60  # 60 segundos em frames para a primeira onda
    HEALTH_INCREASE_PER_WAVE = 1.05  # Aumento de vida por onda
    
    def __init__(self):
        self.current_wave = 1
        self.enemies_in_wave = self.calculate_wave_size()
        self.enemies_spawned = 0
        self.spawn_timer = 0
        self.wave_completed = False
        self.game_completed = False
        self.preparation_timer = self.INITIAL_PREPARATION_TIME
        self.wave_active = False
        self.boss_spawned = False  # Nova flag para controlar spawn do boss
        self.boss_spawn_cooldown = 0  # Timer para controlar intervalo após spawn do boss
        
    def update(self):
        if not self.wave_active:
            self.preparation_timer -= GameSpeed.get_instance().current_multiplier
            if self.preparation_timer <= 0:
                self.wave_active = True
                
    def skip_preparation(self):
        if not self.wave_active:
            self.preparation_timer = 0
            self.wave_active = True
        
    def calculate_wave_size(self):
        """Calcula o número de inimigos para a onda atual"""
        # Inimigos base + 1 por onda
        enemies = self.BASE_ENEMIES + self.current_wave
        
        # +1 inimigo extra a cada 5 ondas
        enemies += (self.current_wave // 5)
        
        # +2 inimigos extras a cada 10 ondas
        enemies += (self.current_wave // 10) * 2
        
        return enemies
        
    def get_spawn_interval(self):
        # Diminui o intervalo entre spawns conforme as ondas avançam
        return self.BASE_SPAWN_INTERVAL - self.current_wave
        
    def get_health_increase(self):
        """Retorna o multiplicador de vida baseado na onda atual"""
        # Retorna o multiplicador de vida
        if self.current_wave <= 20:
            return 1 + ((self.current_wave - 1) * 0.025)
        else:
            return 1 + ((self.current_wave - 1) * 0.04)
        
    def get_spawn_chances(self):
        # Retorna as chances de spawn para cada tipo de inimigo baseado na onda atual
        if self.current_wave % 5 == 0:  # Ondas múltiplas de 5
            return {
                'normal': 25,
                'tank': 10,
                'speed': 10,
                'armored': 10,
                'healer': 10,
                'freeze_aura': 10,
                'rage': 15,
                'stealth': 10
            }
        elif self.current_wave % 2 == 0:  # Ondas pares
            return {
                'normal': 40,
                'tank': 10,
                'speed': 8,
                'armored': 10,
                'healer': 10,
                'freeze_aura': 8,
                'rage': 8,
                'stealth': 6
            }
        else:  # Ondas normais
            return {
                'normal': 60,
                'tank': 7,
                'speed': 8,
                'armored': 7,
                'healer': 4,
                'freeze_aura': 6,
                'rage': 6,
                'stealth': 2
            }
        
    def get_gold_multiplier(self):
        # Aumenta o ouro dropado pelos inimigos em 5% por onda
        return 1 + (self.current_wave - 1) * 0.05
        
    def should_spawn_enemy(self):
        if not self.wave_active or self.enemies_spawned >= self.enemies_in_wave:
            return False
            
        # Verifica se é a onda 10 e o boss ainda não foi spawnado
        if self.current_wave == 10 and not self.boss_spawned and self.enemies_spawned == 0:
            self.boss_spawned = True
            self.enemies_spawned += 1
            self.boss_spawn_cooldown = self.get_spawn_interval()  # Define o intervalo após o boss
            return "speed_boss"
            
        # Verifica se é a onda 20 e o boss ainda não foi spawnado
        if self.current_wave == 20 and not self.boss_spawned and self.enemies_spawned == 0:
            self.boss_spawned = True
            self.enemies_spawned += 1
            self.boss_spawn_cooldown = self.get_spawn_interval()  # Define o intervalo após o boss
            return "split_boss"
            
        # Verifica se é a onda 30 e o boss ainda não foi spawnado
        if self.current_wave == 30 and not self.boss_spawned and self.enemies_spawned == 0:
            self.boss_spawned = True
            self.enemies_spawned += 1
            self.boss_spawn_cooldown = self.get_spawn_interval()  # Define o intervalo após o boss
            return "magnet_boss"
            
        # Verifica se é a onda 40 e o boss ainda não foi spawnado
        if self.current_wave == 40 and not self.boss_spawned and self.enemies_spawned == 0:
            self.boss_spawned = True
            self.enemies_spawned += 1
            self.boss_spawn_cooldown = self.get_spawn_interval()  # Define o intervalo após o boss
            return "vampiric_boss"

        # Verifica se é a onda 50 e o boss ainda não foi spawnado
        if self.current_wave == 50 and not self.boss_spawned and self.enemies_spawned == 0:
            self.boss_spawned = True
            self.enemies_spawned += 1
            self.boss_spawn_cooldown = self.get_spawn_interval()  # Define o intervalo após o boss
            return "immunity_boss"
            
        # Se o boss acabou de ser spawnado, espera o cooldown
        if self.boss_spawn_cooldown > 0:
            self.boss_spawn_cooldown -= GameSpeed.get_instance().current_multiplier
            return False
            
        self.spawn_timer -= GameSpeed.get_instance().current_multiplier
        if self.spawn_timer <= 0:
            self.spawn_timer = self.get_spawn_interval()
            self.enemies_spawned += 1
            return True
        return False
        
    def check_wave_complete(self, active_enemies):
        if self.enemies_spawned >= self.enemies_in_wave and len(active_enemies) == 0:
            self.wave_completed = True
            self.wave_active = False
            self.preparation_timer = self.PREPARATION_TIME
            return True
        return False
        
    def start_next_wave(self):
        if self.current_wave >= self.MAX_WAVES:
            self.game_completed = True
            return False
            
        self.current_wave += 1
        self.enemies_in_wave = self.calculate_wave_size()
        self.enemies_spawned = 0
        self.spawn_timer = self.get_spawn_interval()
        self.wave_completed = False
        self.boss_spawned = False  # Reseta a flag do boss para a próxima onda
        return True
        
    def get_wave_status(self):
        if not self.wave_active:
            return f"Preparação para Onda {self.current_wave}/{self.MAX_WAVES} - {self.preparation_timer // 60}s"
        return f"Onda {self.current_wave}/{self.MAX_WAVES}" 