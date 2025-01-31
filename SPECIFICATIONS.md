# Tower Defense - Especificações do Projeto

## Visão Geral
Este é um jogo de Tower Defense desenvolvido em Python usando Pygame. O jogador deve defender uma base contra ondas de inimigos usando diferentes tipos de torres defensivas.

## Estrutura do Projeto
O projeto é dividido em vários módulos:
- `base.py`: Gerencia a base do jogador e o botão de pular onda
- `defender.py`: Implementa as torres defensivas e seus botões
- `enemy.py`: Define os diferentes tipos de inimigos
- `enemy_status.py`: Interface do menu de status dos inimigos
- `main.py`: Loop principal do jogo e gerenciamento geral
- `projectile.py`: Sistema de projéteis
- `upgrade_menu.py`: Interface de melhorias das torres
- `wave_manager.py`: Sistema de gerenciamento de ondas

## Interface do Jogo

### Layout da Tela
- Largura total: 1300px (1000px jogo + 300px menu lateral)
- Altura total: 800px
- Menu superior: 100px altura
- Área de jogo: 600px altura
- Menu da loja: 100px altura
- Menu lateral: 300px largura

### Menus
1. **Menu Superior**
   - Exibe informações da onda atual
   - Mostra tempo de preparação
   - Botão de pular onda

2. **Menu Lateral**
   - Mostra status dos inimigos
   - Informações detalhadas de cada tipo
   - Estatísticas atualizadas por onda
   - Sistema de scroll vertical
   - Navegação com roda do mouse

3. **Menu da Loja**
   - Exibe defensores disponíveis
   - Mostra custo de cada defensor
   - Indica se há ouro suficiente para compra

## Sistema de Base

### Características da Base
- Vida máxima: 100
- Barra de vida visual
- Localização: Canto inferior direito
- Game over quando vida chega a 0

### Visualização
- Barra vermelha (fundo)
- Barra verde (vida atual)
- Borda branca
- Texto indicando vida atual/máxima

## Sistema de Defensores

### Tipos de Defensores

#### 1. Defensor Azul (Congelante)
- **Custo**: 75 ouro
- **Dano Base**: 10
- **Velocidade de Ataque**: 2/s
- **Habilidade Especial**: Congela inimigos após 8 ataques
- **Projétil**: Azul claro

#### 2. Defensor Vermelho (Flamejante)
- **Custo**: 100 ouro
- **Dano Base**: 12
- **Velocidade de Ataque**: 2.4/s
- **Multiplicador de Dano**: 1.2x
- **Habilidade Especial**: Dano ao longo do tempo após 5 ataques
- **Projétil**: Vermelho claro

#### 3. Defensor Amarelo (Luminoso)
- **Custo**: 125 ouro
- **Dano Base**: 15
- **Velocidade de Ataque**: 1.7/s
- **Alcance**: 200 (maior que outros)
- **Multiplicador de Dano**: 1.5x
- **Habilidade Especial**: Buff de dano para outros defensores após 10 ataques
- **Projétil**: Amarelo claro

### Sistema de Melhorias
- Custo base: 15 ouro × nível atual
- Aumenta dano em 10% por nível
- Reduz tempo entre ataques em 1% por nível
- Valor de venda aumenta com melhorias

### Mecânicas de Posicionamento
- Distância mínima entre defensores: 40px
- Não pode ser colocado no caminho dos inimigos
- Não pode ser colocado nos menus
- Visualização de alcance ao posicionar
- Indicador visual de posição válida/inválida

## Sistema de Inimigos

### Tipos de Inimigos

#### 1. Inimigo Básico (Roxo)
- **Vida**: 100 + bônus por onda
- **Velocidade**: 2
- **Chance de Spawn**: 60%
- **Recompensa**: 5 ouro
- **Vulnerável a**: Todos os efeitos

#### 2. Inimigo Tanque (Marrom)
- **Vida**: 200 + bônus por onda
- **Velocidade**: 1.2
- **Chance de Spawn**: 20%
- **Recompensa**: 10 ouro
- **Imune a**: Efeito de lentidão
- **Tamanho**: Maior que normal

#### 3. Inimigo Veloz (Verde)
- **Vida**: 60 + bônus por onda
- **Velocidade**: 3
- **Chance de Spawn**: 30%
- **Recompensa**: 3 ouro
- **Imune a**: Dano ao longo do tempo
- **Tamanho**: Menor que normal

#### 4. Inimigo Blindado (Cinza)
- **Vida**: 150 + bônus por onda
- **Velocidade**: 1.5
- **Chance de Spawn**: 25%
- **Recompensa**: 8 ouro
- **Habilidade**: Reduz dano recebido em 30%

#### 5. Inimigo Dividido (Laranja)
- **Vida**: 120 + bônus por onda
- **Velocidade**: 1.8
- **Chance de Spawn**: 15%
- **Recompensa**: 7 ouro
- **Habilidade**: Ao morrer, divide-se em dois inimigos menores
- **Inimigos Divididos**:
  - 40% da vida original
  - 70% do tamanho original
  - 20% mais rápidos
- **Tamanho**: Maior que normal

#### 6. Inimigo Curador (Verde Claro)
- **Vida**: 80 + bônus por onda
- **Velocidade**: 1.5
- **Chance de Spawn**: 20%
- **Recompensa**: 6 ouro
- **Habilidade**: Cura aliados próximos
- **Cura**:
  - 5 HP a cada 2 segundos
  - Raio de 100 pixels
  - Efeito visual de cura
- **Tamanho**: Menor que normal

### Efeitos de Status
1. **Lentidão**
   - Reduz velocidade em 50%
   - Duração: 120 frames
   - Efeito visual azul

2. **Queimadura (DoT)**
   - Dano a cada 30 frames
   - Duração: 120 frames
   - Efeito visual laranja

## Sistema de Ondas

### Características
- **Máximo de Ondas**: 60
- **Inimigos Base**: 5 + 1 por onda
- **Bônus de Inimigos**:
  - +1 a cada 5 ondas
  - +2 a cada 10 ondas

### Tempos de Preparação
- **Primeira Onda**: 60 segundos
- **Demais Ondas**: 10 segundos
- Opção de pular preparação

### Escalamento
- **Vida dos Inimigos**: +15 por onda
- **Ouro por Inimigo**: +5% por onda
- **Intervalo de Spawn**: Reduz 1.5 frames por onda (mínimo 45)

### Distribuição de Inimigos

#### Ondas Múltiplas de 5
- Normal: 65%
- Tanque: 10%
- Veloz: 5%
- Blindado: 8%
- Dividido: 7%
- Curador: 5%

#### Ondas Pares
- Normal: 75%
- Tanque: 2.5%
- Veloz: 8%
- Blindado: 2.5%
- Dividido: 7%
- Curador: 5%

#### Ondas Normais
- Normal: 80%
- Tanque: 3%
- Veloz: 3%
- Blindado: 4%
- Dividido: 5%
- Curador: 5%

## Sistema de Recursos

### Ouro
- **Inicial**: 200
- **Recompensas Base**:
  - Inimigo Normal: 5
  - Inimigo Veloz: 3
  - Inimigo Tanque: 10
  - Inimigo Blindado: 8

### Sistema de Venda
- **Mesma Onda**: 100% do valor investido
- **Ondas Diferentes**:
  - 50% do custo base
  - +5 por melhoria realizada

## Sistema de Projéteis

### Características
- **Raio**: 5px
- **Velocidade**: 7
- **Dano**: Definido pelo defensor
- **Seguimento**: Persegue alvo até atingir

## Condições de Vitória/Derrota
- **Vitória**: Completar 60 ondas
- **Derrota**: Base chegar a 0 de vida 