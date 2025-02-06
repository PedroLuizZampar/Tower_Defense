# Tower Defense - Especificações do Projeto

## Visão Geral
Um jogo de Tower Defense em Pygame onde o jogador defende uma base contra ondas de inimigos usando torres defensivas e feitiços. O objetivo é sobreviver a 60 ondas de inimigos.

## Interface do Jogo

### Layout
- Tela total: 1300x850px
- Área de jogo: 1000x600px
- Menu lateral: 300px largura (status dos inimigos)
- Menu superior: 100px altura (informações da onda)
- Menu inferior: 100px altura (loja de defensores)

### Menus
1. **Menu Superior**
   - Status da onda atual e próxima
   - Tempo de preparação
   - Botão de pular preparação
   - Missões retráteis

2. **Menu Lateral**
   - Status detalhado dos inimigos
   - Scroll vertical com roda do mouse
   - Estatísticas por tipo de inimigo
   - Informações da onda atual

3. **Loja**
   - Defensores disponíveis para compra
   - Custo e status de desbloqueio
   - Ouro atual do jogador
   - Preview de alcance ao selecionar

## Mecânicas Principais

### Base
- 100 pontos de vida
- Barra de vida visual com texto
- Game over ao chegar a 0

### Defensores

#### Tipos e Custos
1. **Básico**
   - 50 ouro
   - Dano: 8
   - Ataque: 35 frames
   - Disponível inicialmente

2. **Congelante (Azul)**  
   - 75 ouro + 2 orbes
   - Dano: 10
   - Ataque: 30 frames
   - Congela a cada 8 ataques

3. **Flamejante (Vermelho)**
   - 100 ouro + 3 orbes
   - Dano: 12
   - Ataque: 25 frames
   - DoT a cada 5 ataques

4. **Luminoso (Amarelo)**
   - 125 ouro + 5 orbes
   - Dano: 15
   - Ataque: 35 frames
   - Buff de dano em área a cada 10 ataques

#### Melhorias
- Custo: 15 ouro × nível
- +10% dano por nível
- -1% tempo de ataque por nível
- Valor de venda aumenta com melhorias

#### Posicionamento
- 40px mínimo entre torres
- Fora do caminho dos inimigos
- Preview de alcance e validade
- Não pode ser nos menus

### Inimigos

#### Tipos
1. **Básico (Roxo)**
   - 100 vida + bônus/onda
   - Velocidade 2
   - 3 ouro
   - Sem resistências

2. **Tanque (Marrom)**
   - 200 vida + bônus/onda
   - Velocidade 1.2
   - 12 ouro
   - Imune a congelamento

3. **Veloz (Verde)**
   - 60 vida + bônus/onda
   - Velocidade 3
   - 5 ouro
   - Imune a DoT

4. **Blindado (Cinza)**
   - 150 vida + bônus/onda
   - Velocidade 1.5
   - 10 ouro
   - -30% dano recebido

5. **Curador (Verde Claro)**
   - 180 vida + bônus/onda
   - Velocidade 1.4
   - 8 ouro
   - Cura 5 HP/2s em 150px

### Feitiços

#### Tipos
1. **Gelo**
   - 10s cooldown
   - Congela 1.5s
   - Raio: 150px
   - Tanques imunes

2. **Fogo**
   - 12s cooldown
   - 20 dano/tick por 5s
   - Raio: 200px
   - Velozes imunes

3. **Explosão**
   - 15s cooldown
   - 200 dano (-30% em blindados)
   - Raio: 100px

### Sistema de Ondas
- 60 ondas máximo
- 5 inimigos + 1/onda base
- +1 inimigo/5 ondas
- +2 inimigos/10 ondas
- Vida: +8%/onda
- Ouro: +5%/onda
- Spawn mais rápido por onda

### Recursos
- 200 ouro inicial
- Venda: 100% mesmo turno
- Venda: 50% + 5/melhoria outros turnos

### Missões
1. **Eliminação**
   - 100 inimigos
   - 2 orbes

2. **Sobrevivência**
   - 10 ondas
   - 3 orbes

### Projéteis
- Raio: 5px
- Velocidade: 7
- Perseguem alvo
- Dano baseado no defensor

### Status
1. **Congelamento**
   - 1.5s duração
   - Paralisia total
   - Visual azul

2. **Queimadura**
   - 5s duração
   - 20 dano/0.5s
   - Visual laranja