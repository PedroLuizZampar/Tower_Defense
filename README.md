# Tower Defense - Documentação

## 🎮 Visão Geral
Um jogo de Tower Defense onde você deve defender sua base contra ondas de inimigos usando diferentes tipos de torres defensivas. Cada defensor possui habilidades únicas e pode ser melhorado ao longo do jogo.

## 📋 Conteúdo
1. [Interface do Jogo](#interface-do-jogo)
2. [Defensores](#defensores)
3. [Inimigos](#inimigos)
4. [Sistema de Ondas](#sistema-de-ondas)
5. [Economia](#economia)
6. [Mecânicas de Jogo](#mecânicas-de-jogo)

## 🖥️ Interface do Jogo
### Layout da Tela
- **Dimensões**: 1200x800 pixels
- **Áreas**:
  - Menu de Inimigos (Esquerda): 300px
  - Área de Jogo (Centro): 1000px
  - Menu de Ondas (Superior): 100px
  - Loja de Defensores (Inferior): 200px

### Menus
#### Menu de Inimigos
- Exibe informações detalhadas sobre cada tipo de inimigo
- Mostra estatísticas atualizadas baseadas na onda atual
- Inclui:
  - Nome do inimigo
  - Vida atual
  - Velocidade
  - Habilidades especiais

#### Menu de Ondas
- Mostra a onda atual e máxima (X/60)
- Timer de preparação entre ondas
- Botão para pular tempo de preparação

#### Loja de Defensores
- Exibe defensores disponíveis para compra
- Mostra custo em ouro
- Prévia de estatísticas ao passar o mouse
- Indicador visual de disponibilidade baseado no ouro

## 🛡️ Defensores
### Defensor Azul (Congelante)
- **Custo**: 100 ouro
- **Dano Base**: 10
- **Velocidade de Ataque**: 30 frames
- **Habilidade Especial**: A cada 8 ataques, aplica lentidão em todos os inimigos no alcance

### Defensor Vermelho (Flamejante)
- **Custo**: 125 ouro
- **Dano Base**: 12
- **Velocidade de Ataque**: 25 frames
- **Multiplicador de Dano**: 1.2x
- **Habilidade Especial**: A cada 5 ataques, aplica dano ao longo do tempo (50% do dano normal)

### Defensor Amarelo (Luminoso)
- **Custo**: 150 ouro
- **Dano Base**: 15
- **Velocidade de Ataque**: 35 frames
- **Alcance**: 200 (maior que os outros)
- **Multiplicador de Dano**: 1.5x
- **Habilidade Especial**: A cada 10 ataques, aumenta o dano dos defensores próximos

### Sistema de Melhorias
- Custo de melhoria: 15 × nível atual
- Cada melhoria:
  - Aumenta o dano em 5
  - Reduz o tempo de recarga em 1%
  - Aumenta o valor de venda

### Sistema de Venda
- **Mesma Onda**: 100% do valor investido
- **Ondas Diferentes**:
  - 50% do custo base
  - +5 de ouro por melhoria realizada

## 👾 Inimigos
### Inimigo Normal
- Estatísticas balanceadas
- Sem resistências especiais
- Recompensa: 2 ouro

### Inimigo Tanque
- Vida muito alta
- Velocidade reduzida
- Resistente a efeitos de lentidão
- Recompensa: 5 ouro

### Inimigo Veloz
- Vida baixa
- Velocidade muito alta
- Resistente a dano ao longo do tempo
- Recompensa: 1 ouro

### Inimigo Blindado
- Vida alta
- Velocidade moderada
- Recebe 30% menos dano
- Recompensa: 3 ouro

## 🌊 Sistema de Ondas
### Progressão
- Total de 60 ondas
- Número de inimigos aumenta:
  - +1 inimigo por onda
  - +1 inimigo extra a cada 5 ondas
  - +2 inimigos extras a cada 10 ondas

### Tempo de Preparação
- Primeira Onda: 60 segundos
- Demais Ondas: 10 segundos
- Possibilidade de pular preparação

### Dificuldade Progressiva
- Vida dos inimigos aumenta em 15 por onda
- Intervalo entre spawns diminui
- Ouro por inimigo aumenta 5% por onda

### Chances de Spawn
#### Ondas Normais
- Normal: 90%
- Tanque: 3.33%
- Veloz: 3.33%
- Blindado: 3.34%

#### Ondas Pares
- Normal: 85%
- Tanque: 2.5%
- Veloz: 10%
- Blindado: 2.5%

#### Ondas Múltiplas de 5
- Normal: 75%
- Tanque: 10%
- Veloz: 5%
- Blindado: 10%

## 💰 Economia
### Ouro Inicial
- 300 ouro para começar

### Recompensas
- Baseadas no tipo de inimigo
- Multiplicador aumenta com as ondas
- Bônus por venda de defensores

### Custos
- Defensores: 100-150 ouro
- Melhorias: 15 × nível atual
- Sem custo de manutenção

## 🎯 Mecânicas de Jogo
### Posicionamento de Defensores
- Não podem ser colocados:
  - Sobre o caminho dos inimigos
  - No menu lateral
  - Na área da loja
  - Muito próximos uns dos outros (40 pixels)
- Indicador visual de posicionamento válido/inválido

### Sistema de Alcance
- Visualização ao selecionar defensor
- Cor cinza para posições válidas
- Cor vermelha para posições inválidas

### Sistema de Dano
- Dano base + bônus de melhorias
- Multiplicadores específicos por tipo
- Buffs temporários do Defensor Amarelo

### Condições de Vitória/Derrota
- **Vitória**: Sobreviver às 60 ondas
- **Derrota**: Base destruída por inimigos 