# Totem de Decisões Compartilhadas

Prova de conceito de jogo socioenativo desenvolvida como Projeto Final de Graduação (PFG) no Instituto de Computação da UNICAMP.

O artefato provoca **reflexão e diálogo sobre ética e tecnologia** — privacidade, consentimento, uso de dados e IA — por meio de decisões físicas e compartilhadas que avançam microhistórias narrativas em uma interface web.

---

## Contexto

Este projeto integra hardware tangível, comunicação em rede e narrativa interativa para criar uma experiência socioenativa: a experiência emerge do acoplamento entre o objeto físico, as pessoas e o ambiente social — não de regras rígidas ou condições de vitória.

A interação se dá em grupo: os participantes pressionam botões e ajustam um potenciômetro no Totem para expressar suas decisões coletivas. Cada decisão classifica-se em um **evento nomeado** que avança a microhistória em exibição no PC, sempre chegando a um desfecho em no máximo 2 rodadas.

> Desenvolvido sob orientação do Prof. Dr. Emanuel Felipe Duarte — Grupo de Sistemas Socioenativos / IC-UNICAMP.

---

## Estrutura do repositório

```
├── pico2W/
│   └── totem.py          # Firmware do Raspberry Pi Pico W (MicroPython)
│
├── server_side/
│   ├── historias/
│   │   ├── ia_escolar.py           # Microhistória: A IA na Sala de Aula
│   │   └── brinquedo_inteligente.py # Microhistória: O Brinquedo Inteligente
│   ├── motor.py          # Motor de progressão narrativa
│   └── servidor.py       # Servidor Flask (recebe eventos, serve painel web)
│
├── requirements.txt
└── README.md
```

---

## Como funciona

### 1. Hardware — `pico2W/totem.py`

O Totem é um Raspberry Pi Pico W com:

| Componente | Pino | Função |
|---|---|---|
| Botão **Abrir** | GP2 | Expressa abertura / compartilhamento |
| Botão **Resguardar** | GP3 | Expressa cautela / limitação |
| Potenciômetro | GP26 (ADC0) | Define a **intensidade** da decisão (0–100%) |
| LED vermelho | GP10 | Sinaliza abertura ativa |
| LED verde | GP11 | Sinaliza resguardo ativo |
| LED azul | GP12 | Estado neutro / aguardando |
| Buzzer | GP6 (PWM) | Feedback sonoro por evento |

Cada rodada dura 5 segundos. Ao final, a combinação de botões pressionados e a faixa de intensidade (baixa / média / alta) determina o **evento classificado**:

| Evento | Descrição |
|---|---|
| `abertura_cautelosa` | Só abrir, intensidade baixa |
| `abertura_negociada` | Só abrir, intensidade média |
| `abertura_impulsiva` | Só abrir, intensidade alta |
| `resguardo_leve` | Só resguardar, intensidade baixa |
| `resguardo_moderado` | Só resguardar, intensidade média |
| `resguardo_forte` | Só resguardar, intensidade alta |
| `acordo_resguardado` | Ambos os botões, intensidade baixa |
| `acordo_equilibrado` | Ambos os botões, intensidade média |
| `acordo_aberto` | Ambos os botões, intensidade alta |
| `sem_intervencao` | Nenhum botão pressionado |

O evento é enviado ao servidor via HTTP POST (JSON).

---

### 2. Motor de narrativa — `server_side/motor.py`

O `MicrohistoriaEngine` gerencia a progressão da história ativa:

- Cada microhistória é um dicionário com estágios, transições e textos narrativos
- Transições aceitam **correspondência exata** ou **glob** (`abertura*`, `resguardo*`)
- Estágios marcados com `"terminal": True` encerram a história — nenhum evento posterior altera o desfecho
- Métodos principais: `processar_evento()`, `is_terminal()`, `trocar_historia()`, `reiniciar()`

```python
engine = MicrohistoriaEngine(IA_ESCOLAR)
estagio = engine.processar_evento("resguardo_forte")
print(estagio["narrativa"])
```

---

### 3. Servidor — `server_side/servidor.py`

Servidor Flask com duas rotas:

| Rota | Método | Descrição |
|---|---|---|
| `/evento` | POST | Recebe evento do Totem, avança a microhistória, atualiza estado |
| `/historia` | POST | Troca a microhistória ativa em tempo real |
| `/` | GET | Painel web com narrativa atual, estado do sistema e histórico |

O servidor mantém um **estado acumulado** que evolui ao longo de toda a sessão:

- `confiança` — tendência do grupo a abrir acesso
- `privacidade` — tendência a proteger dados
- `autonomia_ia` — quanto controle foi delegado ao sistema
- `tensão` — acúmulo de decisões conflitantes

O painel se atualiza automaticamente a cada 2 segundos.

---

### 4. Microhistórias — `server_side/historias/`

Cada arquivo define uma microhistória independente. A estrutura é uma árvore de profundidade 2:

```
apresentacao
    ├─[abertura*]──► estágio intermediário A ──► 6 finais possíveis
    ├─[resguardo*]─► estágio intermediário B ──► 6 finais possíveis
    └─[acordo*]────► estágio intermediário C ──► 6 finais possíveis
```

**Histórias disponíveis:**

| Arquivo | Título | Tema central |
|---|---|---|
| `ia_escolar.py` | A IA na Sala de Aula | Dados de alunos, relatórios para pais |
| `brinquedo_inteligente.py` | O Brinquedo Inteligente | IA em brinquedos, manipulação emocional, coleta disfarçada |

Para adicionar uma nova história, basta criar um arquivo em `historias/` seguindo o mesmo esquema de dicionário e registrá-la em `servidor.py`.

---

## Instalação e execução

### Requisitos

- Python 3.10+
- Raspberry Pi Pico W com MicroPython instalado
- PC e Pico W na mesma rede Wi-Fi

### Servidor

```bash
pip install -r requirements.txt
cd server_side
python servidor.py
```

O painel estará disponível em `http://localhost:5000`.

### Totem

No arquivo `pico2W/totem.py`, configure:

```python
WIFI_SSID     = "sua_rede"
WIFI_PASSWORD = "sua_senha"
WEBHOOK_URL   = "http://IP_DO_PC:5000/evento"
```

Transfira o arquivo para o Pico W com [Thonny](https://thonny.org/) ou `mpremote`.

---

## Referências

1. DUARTE, E. F. et al. *"The Magic of Science:" Beyond Action, a Case Study on Learning Through Socioenaction*. WIE 2019. DOI: [10.5753/cbie.wie.2019.501](https://doi.org/10.5753/cbie.wie.2019.501)
2. SOCIOENACTIVE SYSTEMS (UNICAMP). Products. Disponível em: [socioenactive.ic.unicamp.br](https://socioenactive.ic.unicamp.br/en/products/)
3. FAIRPLAY. *AI Toys are NOT Safe for Kids: Advisory*. 2025. Disponível em: [fairplayforkids.org](https://fairplayforkids.org/wp-content/uploads/2025/11/AI-Toys-Advisory.pdf)
4. COLLIER, K. et al. *AI-powered kids' toys talk about sex, geopolitics and how to light a match*. NBC News, dez. 2025.

---

*PFG — Instituto de Computação, UNICAMP. Orientador: Prof. Dr. Emanuel Felipe Duarte.*