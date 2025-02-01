import random

class WaveManager:
    MAX_WAVES = 60
    BASE_ENEMIES = 5  # Número base de inimigos na primeira onda
    BASE_SPAWN_INTERVAL = 120  # Intervalo base entre spawns (em frames)
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
        
    def update(self):
        if not self.wave_active:
            self.preparation_timer -= 1
            if self.preparation_timer <= 0:
                self.wave_active = True
                
    def skip_preparation(self):
        if not self.wave_active:
            self.preparation_timer = 0
            self.wave_active = True
        
    def calculate_wave_size(self):
        """Calcula o número de inimigos para a onda atual"""
        # Inimigos base + 1 por onda
        enemies = self.BASE_ENEMIES + (self.current_wave - 1)
        
        # +1 inimigo extra a cada 5 ondas
        enemies += (self.current_wave // 5)
        
        # +2 inimigos extras a cada 10 ondas
        enemies += (self.current_wave // 10) * 2
        
        return enemies
        
    def get_spawn_interval(self):
        # Diminui o intervalo entre spawns conforme as ondas avançam
        # Mínimo de 45 frames entre spawns
        return max(45, self.BASE_SPAWN_INTERVAL - (self.current_wave * 1.5))
        
    def get_health_increase(self):
        """Retorna o multiplicador de vida baseado na onda atual"""
        # Retorna o multiplicador de vida (8% de aumento por onda)
        return 1 + ((self.current_wave - 1) * 0.08)
        
    def get_spawn_chances(self):
        # Retorna as chances de spawn para cada tipo de inimigo baseado na onda atual
        if self.current_wave % 5 == 0:  # Ondas múltiplas de 5
            return {
                'normal': 72,  # Aumentado para compensar a remoção do split
                'tank': 10,
                'speed': 5,
                'armored': 8,
                'healer': 5
            }
        elif self.current_wave % 2 == 0:  # Ondas pares
            return {
                'normal': 82,  # Aumentado para compensar a remoção do split
                'tank': 2.5,
                'speed': 8,
                'armored': 2.5,
                'healer': 5
            }
        else:  # Ondas normais
            return {
                'normal': 85,  # Aumentado para compensar a remoção do split
                'tank': 3,
                'speed': 3,
                'armored': 4,
                'healer': 5
            }
        
    def get_gold_multiplier(self):
        # Aumenta o ouro dropado pelos inimigos em 5% por onda
        return 1 + (self.current_wave - 1) * 0.05
        
    def should_spawn_enemy(self):
        if not self.wave_active or self.enemies_spawned >= self.enemies_in_wave:
            return False
            
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_timer = self.get_spawn_interval()
            self.enemies_spawned += 1
            return True
        return False
        
    def enemy_defeated(self, enemy_type):
        # Recompensas base ajustadas por tipo de inimigo
        base_rewards = {
            'normal': 3,    # 3 de ouro
            'speed': 5,     # 5 de ouro
            'tank': 12,     # 12 de ouro
            'armored': 10,  # 10 de ouro
            'healer': 8     # 8 de ouro
        }
        
        # Aplica multiplicador de onda e retorna o valor final
        gold = base_rewards[enemy_type] * self.get_gold_multiplier()
        return int(gold)  # Arredonda para número inteiro
        
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
        return True
        
    def get_wave_status(self):
        if not self.wave_active:
            return f"Preparação para Onda {self.current_wave}/{self.MAX_WAVES} - {self.preparation_timer // 60}s"
        return f"Onda {self.current_wave}/{self.MAX_WAVES}" 