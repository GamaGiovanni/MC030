# servidor.py

from flask import Flask, request, jsonify
from motor import MicrohistoriaEngine

from pathlib import Path
import importlib.util

PASTA_HISTORIAS = Path(__file__).parent / "historias"

def validar_historia(historia, arquivo):
    campos_obrigatorios = ["id", "titulo", "estagio_inicial", "estagios"]

    for campo in campos_obrigatorios:
        if campo not in historia:
            raise ValueError(f"{arquivo}: campo obrigatório ausente: {campo}")

    estagio_inicial = historia["estagio_inicial"]
    estagios = historia["estagios"]

    if estagio_inicial not in estagios:
        raise ValueError(
            f"{arquivo}: estagio_inicial '{estagio_inicial}' não existe em estagios"
        )

    return historia


def carregar_historias():
    historias = {}
    erros = {}

    for caminho in PASTA_HISTORIAS.glob("*.py"):
        if caminho.name.startswith("_"):
            continue

        nome_modulo = f"historias.{caminho.stem}"

        try:
            spec = importlib.util.spec_from_file_location(nome_modulo, caminho)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)

            if not hasattr(modulo, "HISTORIA"):
                erros[caminho.name] = "Arquivo não possui variável HISTORIA"
                continue

            historia = validar_historia(modulo.HISTORIA, caminho.name)
            historia_id = historia["id"]

            if historia_id in historias:
                raise ValueError(f"ID de história duplicado: {historia_id}")

            historias[historia_id] = historia

        except Exception as erro:
            erros[caminho.name] = str(erro)

    if not historias:
        raise RuntimeError("Nenhuma história válida foi encontrada em ./historias/")

    return historias, erros

HISTORIAS_DISPONIVEIS, ERROS_HISTORIAS = carregar_historias()

HISTORIA_PADRAO_ID = (next(iter(HISTORIAS_DISPONIVEIS)) if HISTORIAS_DISPONIVEIS else None)

app = Flask(__name__)

engine = MicrohistoriaEngine(HISTORIA_PADRAO_ID)

estado = {
    "confianca":   50,
    "privacidade": 50,
    "autonomia_ia": 50,
    "tensao":      0,
    "historico":   [],
}

def limitar(v, mn=0, mx=100):
    return max(mn, min(mx, v))


def atualizar_estado(evento, intensidade):
    # Lógica que você já tem — sem alteração
    if evento.startswith("abertura"):
        estado["confianca"]   += 8
        estado["privacidade"] -= intensidade // 10
        estado["autonomia_ia"] += 6
        if evento == "abertura_impulsiva":
            estado["tensao"] += 10
    elif evento.startswith("resguardo"):
        estado["privacidade"]  += 8
        estado["autonomia_ia"] -= 5
        if evento == "resguardo_forte":
            estado["tensao"] += 6
    elif evento == "acordo_equilibrado":
        estado["confianca"]   += 5
        estado["privacidade"] += 5
        estado["tensao"]      -= 8
    elif evento == "acordo_resguardado":
        estado["privacidade"]  += 10
        estado["autonomia_ia"] -= 5
        estado["tensao"]       -= 4
    elif evento == "acordo_aberto":
        estado["confianca"]   += 10
        estado["autonomia_ia"] += 8
        estado["privacidade"] -= 8
    elif evento == "sem_intervencao":
        estado["autonomia_ia"] += 5
        estado["tensao"]       += 5

    for chave in ("confianca", "privacidade", "autonomia_ia", "tensao"):
        estado[chave] = limitar(estado[chave])


@app.route("/evento", methods=["POST"])
def receber_evento():
    dados = request.get_json(force=True)
    evento     = dados.get("evento")
    intensidade = int(dados.get("intensidade", 0))

    atualizar_estado(evento, intensidade)

    estagio = engine.processar_evento(evento)

    registro = {
        "rodada":            dados.get("rodada"),
        "evento":            evento,
        "tipo_decisao":      dados.get("tipo_decisao"),
        "intensidade":       intensidade,
        "faixa_intensidade": dados.get("faixa_intensidade"),
        "estagio":           engine.estagio_atual,
        "narrativa":         estagio.get("narrativa", ""),
    }

    estado["historico"].append(registro)
    if len(estado["historico"]) > 10:
        estado["historico"] = estado["historico"][-10:]

    return jsonify({
        "status":    "ok",
        "narrativa": estagio.get("narrativa", ""),
        "estado":    estado,
        "microhistoria": engine.serializar(),
    })


@app.route("/historia", methods=["POST"])
def trocar_historia():
    """Permite trocar a microhistória ativa via POST { "id": "ia_escolar" }"""
    dados = request.get_json(force=True)
    historia_id = dados.get("id")

    if historia_id not in HISTORIAS_DISPONIVEIS:
        return jsonify({"erro": f"História '{historia_id}' não encontrada."}), 404

    engine.trocar_historia(HISTORIAS_DISPONIVEIS[historia_id])
    return jsonify({"status": "ok", "historia": engine.serializar()})

@app.route("/", methods=["GET"])
def painel():
    micro = engine.serializar()
    ultima = estado["historico"][-1] if estado["historico"] else None

    if ultima is None:
        ultima_html = "<p>Nenhuma decisão recebida ainda.</p>"
    else:
        ultima_html = f"""
        <h2>Última decisão</h2>
        <p><strong>Rodada:</strong> {ultima["rodada"]}</p>
        <p><strong>Evento:</strong> {ultima["evento"]}</p>
        <p><strong>Tipo:</strong> {ultima["tipo_decisao"]}</p>
        <p><strong>Intensidade:</strong> {ultima["intensidade"]}%</p>
        <p><strong>Narrativa:</strong> {ultima["narrativa"]}</p>
        """

    historico_html = "".join(
        f"<li>Rodada {item['rodada']}: {item['evento']} ({item['intensidade']}%) — {item['estagio']}</li>"
        for item in reversed(estado["historico"])
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="2">
        <title>Totem de Decisões Compartilhadas</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }}
            .card {{ background: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); }}
            .barra {{ background: #ddd; border-radius: 8px; overflow: hidden; margin-bottom: 12px; }}
            .valor {{ background: #777; color: white; padding: 6px; text-align: right; }}
            .narrativa {{ background: #eef; border-left: 4px solid #669; padding: 12px 16px; border-radius: 6px; margin: 12px 0; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Totem de Decisões Compartilhadas</h1>
            <p><strong>História ativa:</strong> {micro["historia_titulo"]}</p>
            <p><strong>Estágio atual:</strong> {micro["estagio_atual"]}</p>
            <div class="narrativa">{micro["narrativa"]}</div>
            {ultima_html}
        </div>

        <div class="card">
            <h2>Estado do sistema</h2>
            <p>Confiança</p>
            <div class="barra"><div class="valor" style="width:{estado['confianca']}%">{estado['confianca']}</div></div>
            <p>Privacidade</p>
            <div class="barra"><div class="valor" style="width:{estado['privacidade']}%">{estado['privacidade']}</div></div>
            <p>Autonomia da IA</p>
            <div class="barra"><div class="valor" style="width:{estado['autonomia_ia']}%">{estado['autonomia_ia']}</div></div>
            <p>Tensão do grupo</p>
            <div class="barra"><div class="valor" style="width:{estado['tensao']}%">{estado['tensao']}</div></div>
        </div>

        <div class="card">
            <h2>Histórico recente</h2>
            <ul>{historico_html}</ul>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)