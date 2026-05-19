from machine import Pin, PWM, ADC
from time import sleep_ms, ticks_ms, ticks_diff
import ujson
import network
import urequests

# =========================
# CONFIGURAÇÃO DE REDE
# =========================

WIFI_SSID = ""
WIFI_PASSWORD = ""

# "http://IP:5000/evento"
WEBHOOK_URL = "http://IP:5000/evento"

WEBHOOK_ATIVO = True

wlan = network.WLAN(network.STA_IF)

# =========================
# PINOS
# =========================

btn_abrir = Pin(2, Pin.IN, Pin.PULL_UP)
btn_resguardar = Pin(3, Pin.IN, Pin.PULL_UP)

led_risco = Pin(10, Pin.OUT)       # vermelho
led_cuidado = Pin(11, Pin.OUT)     # verde
led_neutro = Pin(12, Pin.OUT)      # azul

buzzer = PWM(Pin(6))
buzzer.duty_u16(0)

controle_intensidade = ADC(26)     # GP26 / ADC0

# =========================
# CONFIGURAÇÕES DO TOTEM
# =========================

DEBOUNCE_MS = 180
JANELA_DECISAO_MS = 5000
POLL_MS = 20

ultimo_abrir = 0
ultimo_resguardar = 0
contador_rodadas = 0

# =========================
# WI-FI
# =========================

def conectar_wifi(timeout_ms=12000):
    if wlan.isconnected():
        print("Wi-Fi já conectado:", wlan.ifconfig()[0])
        return True

    print("Conectando ao Wi-Fi...")
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    inicio = ticks_ms()

    while not wlan.isconnected():
        if ticks_diff(ticks_ms(), inicio) > timeout_ms:
            print("Falha ao conectar no Wi-Fi.")
            return False
        sleep_ms(500)

    print("Wi-Fi conectado:", wlan.ifconfig()[0])
    return True

# =========================
# FUNÇÕES AUXILIARES
# =========================

def apagar_leds():
    led_risco.off()
    led_cuidado.off()
    led_neutro.off()

def estado_inicial():
    apagar_leds()
    led_neutro.on()

def beep(freq=1000, duracao_ms=120, duty=25000):
    buzzer.freq(freq)
    buzzer.duty_u16(duty)
    sleep_ms(duracao_ms)
    buzzer.duty_u16(0)

def ler_intensidade_percentual(amostras=8):
    total = 0

    for _ in range(amostras):
        total += controle_intensidade.read_u16()
        sleep_ms(2)

    media = total / amostras
    percentual = int((media / 65535) * 100)

    return max(0, min(100, percentual))

def classificar_intensidade(nivel):
    if nivel <= 33:
        return "baixa"
    elif nivel <= 66:
        return "media"
    return "alta"

def classificar_decisao(acao_abrir, acao_resguardar, intensidade):
    faixa = classificar_intensidade(intensidade)

    if acao_abrir and acao_resguardar:
        if faixa == "baixa":
            return "acordo_resguardado"
        elif faixa == "media":
            return "acordo_equilibrado"
        else:
            return "acordo_aberto"

    elif acao_abrir:
        if faixa == "baixa":
            return "abertura_cautelosa"
        elif faixa == "media":
            return "abertura_negociada"
        else:
            return "abertura_impulsiva"

    elif acao_resguardar:
        if faixa == "baixa":
            return "resguardo_leve"
        elif faixa == "media":
            return "resguardo_moderado"
        else:
            return "resguardo_forte"

    return "sem_intervencao"

def tipo_da_decisao(acao_abrir, acao_resguardar):
    if acao_abrir and acao_resguardar:
        return "decisao_compartilhada"
    elif acao_abrir:
        return "decisao_individual_abertura"
    elif acao_resguardar:
        return "decisao_individual_resguardo"
    return "sem_decisao"

def feedback_durante_decisao(acao_abrir, acao_resguardar):
    apagar_leds()

    if acao_abrir and acao_resguardar:
        led_risco.on()
        led_cuidado.on()
    elif acao_abrir:
        led_risco.on()
    elif acao_resguardar:
        led_cuidado.on()
    else:
        led_neutro.on()

def feedback_final(evento):
    apagar_leds()

    if evento == "acordo_resguardado":
        led_cuidado.on()
        beep(800, 180)

    elif evento == "acordo_equilibrado":
        led_neutro.on()
        beep(1100, 120)
        sleep_ms(80)
        beep(1100, 120)

    elif evento == "acordo_aberto":
        led_risco.on()
        beep(1500, 180)

    elif evento.startswith("abertura"):
        led_risco.on()
        beep(1400, 150)

    elif evento.startswith("resguardo"):
        led_cuidado.on()
        beep(900, 150)

    else:
        led_neutro.on()
        beep(700, 100)

# =========================
# ENVIO PARA O PC
# =========================

def montar_payload(evento, intensidade, acao_abrir, acao_resguardar):
    return {
        "origem": "totem_decisoes",
        "rodada": contador_rodadas,
        "evento": evento,
        "tipo_decisao": tipo_da_decisao(acao_abrir, acao_resguardar),
        "intensidade": intensidade,
        "faixa_intensidade": classificar_intensidade(intensidade),
        "acao_abrir": acao_abrir,
        "acao_resguardar": acao_resguardar,
        "timestamp_ms": ticks_ms()
    }

def enviar_evento_pc(payload):
    mensagem = ujson.dumps(payload)

    # Mantém também o envio pela serial para debug
    print(mensagem)

    if not WEBHOOK_ATIVO:
        print("Webhook desativado.")
        return False

    if not wlan.isconnected():
        print("Wi-Fi desconectado. Tentando reconectar...")
        if not conectar_wifi():
            print("Evento não enviado: sem Wi-Fi.")
            return False

    try:
        resposta = urequests.post(
            WEBHOOK_URL,
            data=mensagem,
            headers={"Content-Type": "application/json"}
        )

        print("Webhook enviado. Status:", resposta.status_code)
        resposta.close()
        return True

    except Exception as erro:
        print("Erro ao enviar webhook:", erro)
        return False

# =========================
# RODADA DE DECISÃO
# =========================

def rodar_rodada_decisao(inicio_abrir=False, inicio_resguardar=False):
    global ultimo_abrir, ultimo_resguardar, contador_rodadas

    contador_rodadas += 1

    inicio = ticks_ms()

    acao_abrir = inicio_abrir
    acao_resguardar = inicio_resguardar
    intensidade_final = ler_intensidade_percentual()

    print("Rodada", contador_rodadas, "iniciada")

    if inicio_abrir:
        print("Interação inicial: ABRIR")
        beep(1300, 60)

    if inicio_resguardar:
        print("Interação inicial: RESGUARDAR")
        beep(900, 60)

    while ticks_diff(ticks_ms(), inicio) < JANELA_DECISAO_MS:
        agora = ticks_ms()

        if btn_abrir.value() == 0 and ticks_diff(agora, ultimo_abrir) > DEBOUNCE_MS:
            ultimo_abrir = agora
            acao_abrir = True
            print("Interação: ABRIR")
            beep(1300, 60)

        if btn_resguardar.value() == 0 and ticks_diff(agora, ultimo_resguardar) > DEBOUNCE_MS:
            ultimo_resguardar = agora
            acao_resguardar = True
            print("Interação: RESGUARDAR")
            beep(900, 60)

        intensidade_final = ler_intensidade_percentual()
        feedback_durante_decisao(acao_abrir, acao_resguardar)

        sleep_ms(POLL_MS)

    evento = classificar_decisao(
        acao_abrir,
        acao_resguardar,
        intensidade_final
    )

    payload = montar_payload(
        evento,
        intensidade_final,
        acao_abrir,
        acao_resguardar
    )

    print("Rodada encerrada")
    print("Intensidade final:", intensidade_final)
    print("Evento final:", evento)

    feedback_final(evento)
    enviar_evento_pc(payload)

    sleep_ms(1200)
    estado_inicial()

# =========================
# LOOP PRINCIPAL
# =========================

estado_inicial()

print("Totem de Decisões Compartilhadas iniciado.")
print("GP2 = abrir/compartilhar | GP3 = resguardar/limitar | GP26 = intensidade")

conectar_wifi()

while True:
    agora = ticks_ms()

    iniciar_rodada = False
    inicio_abrir = False
    inicio_resguardar = False

    if btn_abrir.value() == 0 and ticks_diff(agora, ultimo_abrir) > DEBOUNCE_MS:
        ultimo_abrir = agora
        inicio_abrir = True
        iniciar_rodada = True

    if btn_resguardar.value() == 0 and ticks_diff(agora, ultimo_resguardar) > DEBOUNCE_MS:
        ultimo_resguardar = agora
        inicio_resguardar = True
        iniciar_rodada = True

    if iniciar_rodada:
        rodar_rodada_decisao(inicio_abrir, inicio_resguardar)

    sleep_ms(POLL_MS)