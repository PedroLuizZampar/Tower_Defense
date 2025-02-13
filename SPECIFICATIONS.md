# Tower Defense - Documentação Completa

## Visão Geral
Um jogo de Tower Defense desenvolvido em Pygame onde o jogador defende uma base contra ondas de inimigos usando torres defensivas, feitiços e completando missões. O objetivo é sobreviver a 60 ondas de inimigos cada vez mais fortes.

## Interface do Jogo

### Layout
- Tela total: 1000x650px
- Área de jogo: 1000x550px
- Menu superior: 100px altura (informações da onda)
- Quatro menus laterais retráteis:
  1. Menu de Inimigos
  2. Menu de Missões
  3. Menu de Defensores
  4. Menu de Chefões

### Menus
1. **Menu Superior**
   - Status da onda atual e próxima
   - Tempo de preparação
   - Botão de pular preparação
   - Barra de vida da base

2. **Menu de Inimigos (Retrátil)**
   - Lista paginada de inimigos (5 por página)
   - Para cada inimigo:
     - Nome e ícone
     - Vida e velocidade
     - Habilidades especiais
     - Chances de aparecimento

3. **Menu de Defensores (Retrátil)**
   - Lista paginada de defensores (5 por página)
   - Para cada defensor:
     - Nome e ícone
     - Custo em ouro
     - Dano e DPS
     - Alcance
     - Habilidade especial
     - Status de desbloqueio (custo em orbes)

4. **Menu de Chefões (Retrátil)**
   - Lista de chefões disponíveis
   - Para cada chefão:
     - Nome e ícone
     - Vida e velocidade
     - Descrição da habilidade especial
     - Condições de aparecimento

### Chefões

#### 1. Boss de Imunidade (Protetor)
- **Estatísticas**:
  - Vida: 1250 + bônus/onda
  - Velocidade: 0.8
  - Recompensa: 50 ouro
  - Aparece: Onda 10
- **Habilidade: Aura de Imunidade**
  - Raio: 150px
  - Duração: 2 segundos
  - Intervalo: 3 segundos
  - Efeito: Protege aliados próximos de todo dano
- **Características**:
  - Primeiro inimigo da onda 10
  - Intervalo especial antes dos próximos inimigos
  - Aura visual branca quando ativa
  - Imunidade cíclica (2s ativo, 3s inativo)

4. **Menu de Missões (Retrátil)**
   - Lista de missões ativas
   - Barra de progresso para cada missão
   - Recompensas em orbes
   - Botão de resgate de recompensa
   - Notificação visual quando missão completa

## Mecânicas Principais

### Base
- 100 pontos de vida
- Barra de vida visual com texto
- Game over ao chegar a 0
- Localizada no canto direito do mapa

### Sistema de Recursos
- Ouro: Usado para comprar e melhorar defensores
  - 250 ouro inicial
  - Ganho por eliminar inimigos
  - Bônus de 5% por onda
  - Valor varia por tipo de inimigo

- Orbes: Moeda premium para desbloquear defensores
  - Ganho através de missões
  - Usado para desbloquear defensores especiais
  - Não é consumido em outras ações

### Sistema de Missões
1. **Missões de Eliminação**
   - Eliminar 25 inimigos (1 orbe)
   - Eliminar 100 inimigos (3 orbes)
   - Progresso mantido entre ondas
   - Missões se repetem após completar

2. **Missões de Sobrevivência**
   - Sobreviver 5 ondas (1 orbe)
   - Sobreviver 10 ondas (2 orbes)
   - Progresso mantido entre sessões
   - Missões se repetem após completar

### Defensores

#### 1. Defensor Básico
- **Custo**: 50 ouro
- **Estatísticas Base**:
  - Dano: 8
  - Velocidade de Ataque: 2/s
  - Alcance: 130px
- **Características**:
  - Disponível desde o início
  - Sem habilidades especiais
  - Melhor custo-benefício inicial

#### 2. Defensor Congelante (Azul)
- **Custo**: 75 ouro + 2 orbes para desbloquear
- **Estatísticas Base**:
  - Dano: 10
  - Velocidade de Ataque: 1.71/s
  - Alcance: 140px
- **Habilidade Especial**:
  - A cada 5 ataques, congela todos os inimigos no alcance
  - Congelamento dura 1.5 segundos
  - Inimigos congelados ficam completamente imóveis

#### 3. Defensor Flamejante (Vermelho)
- **Custo**: 100 ouro + 3 orbes para desbloquear
- **Estatísticas Base**:
  - Dano: 10
  - Velocidade de Ataque: 2.14/s
  - Alcance: 140px
- **Habilidade Especial**:
  - A cada 6 ataques, aplica queimadura em área
  - Queimadura causa 50% do dano normal por 3 segundos
  - Afeta todos os inimigos no alcance

#### 4. Defensor Luminoso (Amarelo)
- **Custo**: 125 ouro + 3 orbes para desbloquear
- **Estatísticas Base**:
  - Dano: 18
  - Velocidade de Ataque: 1.33/s
  - Alcance: 200px
- **Habilidade Especial**:
  - A cada 8 ataques, buffa todos os defensores próximos
  - Buff aumenta o dano em 50% por um ataque
  - Maior alcance entre os defensores

#### 5. Defensor Retardante (Verde)
- **Custo**: 150 ouro + 4 orbes para desbloquear
- **Estatísticas Base**:
  - Dano: 13
  - Velocidade de Ataque: 1.33/s
  - Alcance: 130px
- **Habilidade Especial**:
  - A cada 4 ataques, reduz a velocidade dos inimigos
  - Desaceleração dura 3 segundos
  - Reduz a velocidade em 50%

#### 6. Defensor Duplo (Laranja)
- **Custo**: 175 ouro + 5 orbes para desbloquear
- **Estatísticas Base**:
  - Dano: 12
  - Velocidade de Ataque: 1.71/s
  - Alcance: 160px
- **Habilidade Especial**:
  - Ataca sempre os dois inimigos mais próximos
  - Sem limite de ataques para ativar
  - Excelente para controle de grupos

#### 7. Defensor Enfraquecedor (Roxo)
- **Custo**: 200 ouro + 5 orbes para desbloquear
- **Estatísticas Base**:
  - Dano: 20
  - Velocidade de Ataque: 1.33/s
  - Alcance: 135px
- **Habilidade Especial**:
  - A cada 8 ataques, aplica fraqueza nos inimigos
  - Inimigos fracos recebem 30% mais dano
  - Efeito dura 4 segundos

### Sistema de Melhorias
- **Custo**: 15 ouro × nível atual
- **Benefícios por Melhoria**:
  - +10% dano base
  - -1% tempo entre ataques
  - Aumenta valor de venda
- **Sistema de Venda**:
  - 100% do valor investido se vender na mesma onda
  - 50% do custo base + 8 ouro por melhoria em outras ondas

### Inimigos

#### 1. Inimigo Básico
- **Estatísticas**:
  - Vida: 80 + bônus/onda
  - Velocidade: 1.8
  - Recompensa: 3 ouro
  - Chance de Spawn: 65%
- **Características**:
  - Sem resistências especiais
  - Vulnerável a todos os efeitos
  - Mais comum em todas as ondas

#### 2. Inimigo Tanque
- **Estatísticas**:
  - Vida: 250 + bônus/onda
  - Velocidade: 1.0
  - Recompensa: 12 ouro
  - Chance de Spawn: 15%
- **Características**:
  - Imune a congelamento e lentidão
  - Maior vida entre todos os inimigos
  - Movimento muito lento

#### 3. Inimigo Veloz
- **Estatísticas**:
  - Vida: 50 + bônus/onda
  - Velocidade: 3.2
  - Recompensa: 5 ouro
  - Chance de Spawn: 25%
- **Características**:
  - Imune a dano ao longo do tempo
  - Movimento muito rápido
  - Baixa vida

#### 4. Inimigo Blindado
- **Estatísticas**:
  - Vida: 180 + bônus/onda
  - Velocidade: 1.4
  - Recompensa: 10 ouro
  - Chance de Spawn: 20%
- **Características**:
  - Reduz todo dano recebido em 35%
  - Resistente a explosões
  - Alta vida efetiva

#### 5. Inimigo Curador
- **Estatísticas**:
  - Vida: 120 + bônus/onda
  - Velocidade: 1.6
  - Recompensa: 8 ouro
  - Chance de Spawn: 15%
- **Características**:
  - Cura 8 de vida a cada segundo
  - Afeta inimigos num raio de 150px
  - Prioridade de eliminação

#### 6. Inimigo Gelado
- **Estatísticas**:
  - Vida: 100 + bônus/onda
  - Velocidade: 2.0
  - Recompensa: Especial
  - Chance de Spawn: 15%
- **Características**:
  - Ao morrer, congela todas as torres próximas
  - Raio de congelamento de 100px
  - Congelamento dura 1.5 segundos

#### 7. Inimigo Furioso
- **Estatísticas**:
  - Vida: 140 + bônus/onda
  - Velocidade: 1.6
  - Recompensa: Especial
  - Chance de Spawn: 20%
- **Características**:
  - Aumenta velocidade conforme perde vida
  - Velocidade máxima de 2.5x
  - Afetado por slow e freeze

#### 8. Inimigo Furtivo
- **Estatísticas**:
  - Vida: 40 + bônus/onda
  - Velocidade: 2.0
  - Recompensa: Especial
  - Chance de Spawn: 15%
- **Características**:
  - Alterna entre visível e invisível
  - 2 segundos visível, 1 segundo invisível
  - Não pode ser alvo quando invisível

### Feitiços

#### 1. Feitiço de Gelo
- **Características**:
  - Raio: 150px
  - Cooldown: 20 segundos
  - Congela por 1.5 segundos
- **Efeitos**:
  - Paralisa completamente os inimigos
  - Inimigos Tanque são imunes
  - Visual de aura azul

#### 2. Feitiço de Fogo
- **Características**:
  - Raio: 200px
  - Cooldown: 30 segundos
  - Dano: 15 por tick
- **Efeitos**:
  - Causa dano ao longo de 5 segundos
  - Inimigos Velozes são imunes
  - Visual de aura laranja

#### 3. Feitiço de Explosão
- **Características**:
  - Raio: 100px
  - Cooldown: 45 segundos
  - Dano: 200
- **Efeitos**:
  - Dano instantâneo em área
  - 30% menos dano em Blindados
  - Visual de explosão vermelha

### Sistema de Ondas
- Total de 60 ondas
- **Composição Base**:
  - 5 inimigos + 1 por onda
  - +1 inimigo a cada 5 ondas
  - +2 inimigos a cada 10 ondas

- **Escalamento**:
  - Vida: +8% por onda
  - Ouro: +5% por onda
  - Spawn mais rápido progressivamente

- **Tempo de Preparação**:
  - 60 segundos na primeira onda
  - 10 segundos nas demais ondas
  - Pode ser pulado com botão

### Como Jogar

1. **Início do Jogo**
   - Comece com 250 ouro
   - Posicione defensores básicos estrategicamente
   - Use o tempo de preparação para planejar

2. **Gerenciamento de Recursos**
   - Gaste ouro com sabedoria
   - Complete missões para ganhar orbes
   - Desbloqueie novos defensores

3. **Estratégias de Defesa**
   - Combine diferentes tipos de defensores
   - Posicione torres de slow/freeze em pontos chave
   - Use feitiços para emergências

4. **Prioridades de Alvo**
   - Elimine Curadores primeiro
   - Controle inimigos Velozes
   - Prepare-se para inimigos Furtivos

5. **Dicas Avançadas**
   - Melhore torres existentes vs comprar novas
   - Use o menu de inimigos para estudar a onda
   - Mantenha ouro para emergências
   - Posicione defensores para maximizar alcance

### Controles
- **Mouse Esquerdo**:
  - Selecionar/Colocar defensores
  - Ativar feitiços
  - Interagir com menus
  - Melhorar/Vender defensores

- **Interface**:
  - Menus laterais retráteis
  - Informações detalhadas ao passar mouse
  - Indicadores visuais de alcance/efeitos
  - Sistema de notificações para missões