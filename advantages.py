class DamageAdvantage:
    def __init__(self):
        self.level = 0
        self.base_cost = 3  # Custo base em orbes
        self.cost_increase = 3
        self.damage_increase_percent = 0.1  # 10% de aumento por nível
        
    def get_upgrade_cost(self):
        """Retorna o custo do próximo upgrade de dano"""
        return self.base_cost + (self.level * self.cost_increase)
    
    def get_current_bonus(self):
        """Retorna o bônus atual de dano em porcentagem"""
        return self.level * 10  # 10% por nível
    
    def upgrade(self, mission_manager):
        """Realiza o upgrade se houver orbes suficientes"""
        cost = self.get_upgrade_cost()
        if mission_manager.orbes >= cost:
            mission_manager.orbes -= cost
            self.level += 1
            return True
        return False

class CooldownAdvantage:
    def __init__(self):
        self.level = 0
        self.base_cost = 5  # Custo base em orbes
        self.max_level = 5  # Máximo de 5 níveis
        
    def get_upgrade_cost(self):
        """Retorna o custo do próximo upgrade de cooldown"""
        if self.level >= self.max_level:
            return float('inf')  # Retorna infinito se já estiver no nível máximo
        return self.base_cost + (self.level * 5)
    
    def get_current_bonus(self):
        """Retorna o bônus atual de redução de cooldown em porcentagem"""
        return self.level * 10  # 10% por nível
    
    def upgrade(self, mission_manager):
        """Realiza o upgrade se houver orbes suficientes"""
        if self.level >= self.max_level:
            return False
            
        cost = self.get_upgrade_cost()
        if mission_manager.orbes >= cost:
            mission_manager.orbes -= cost
            self.level += 1
            return True
        return False

class GoldAdvantage:
    def __init__(self):
        self.orbe_value = 30  # Valor em ouro de cada orbe
        
    def get_gold_value(self):
        """Retorna quanto ouro o jogador receberá por 1 orbe"""
        return self.orbe_value
    
    def exchange(self, mission_manager):
        """Troca 1 orbe por ouro"""
        if mission_manager.orbes >= 1:
            mission_manager.orbes -= 1
            return self.orbe_value
        return 0