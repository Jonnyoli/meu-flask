from flask import Flask, jsonify, render_template, request
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os
import asyncio
import re


app = Flask(__name__)

# Usa o mesmo arquivo para todos os registos (bot e Flask)
ARQUIVO_REGISTOS = "registos.json"

# Garante que o arquivo de registos existe
if not os.path.exists(ARQUIVO_REGISTOS):
    with open(ARQUIVO_REGISTOS, "w") as f:
        json.dump([], f)

def parse_duracao(dur_str):
    match = re.match(r'(?:(\d+) days?, )?(\d+):(\d+):(\d+)', dur_str)
    if not match:
        raise ValueError(f"Formato de duração inválido: {dur_str}")
    dias = int(match.group(1)) if match.group(1) else 0
    horas = int(match.group(2))
    minutos = int(match.group(3))
    segundos = int(match.group(4))
    return timedelta(days=dias, hours=horas, minutes=minutos, seconds=segundos)
    
    
# Função para buscar membros do bot de forma segura (executa a coroutine no loop do bot)
def get_members_sync():
    future = asyncio.run_coroutine_threadsafe(bot.get_members(), bot.bot.loop)
    return future.result()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/utilizadores")
def utilizadores():
    membros = get_members_sync()  # Retorna um dicionário {cargo: [usuarios]}
    for cargo in membros:
        membros[cargo].sort()
    return render_template("utilizadores.html", usuarios=membros)

@app.route("/api/utilizadores")
def api_utilizadores():
    usuarios = get_members_sync()
    return jsonify(usuarios)

@app.route('/ranking')
def ranking():
    with open('registos.json') as f:
        registos = json.load(f)

    ranking_dict = {}

    for r in registos:
        usuario = r['usuario']
        duracao_raw = r['duracao_servico']

        try:
            # Caso novo: valor em segundos (float)
            segundos = int(float(duracao_raw))
        except (ValueError, TypeError):
            # Caso antigo: string tipo "4 days, 23:24:31"
            duracao = parse_duracao(duracao_raw)
            segundos = int(duracao.total_seconds())

        if usuario not in ranking_dict:
            ranking_dict[usuario] = 0
        ranking_dict[usuario] += segundos

    ranking_ordenado = sorted(ranking_dict.items(), key=lambda x: x[1], reverse=True)

    return render_template('ranking.html', ranking=ranking_ordenado)



@app.route("/registrar_servico", methods=["POST"])
def registrar_servico():
    dados = request.json
    if not dados:
        return jsonify({"error": "Sem dados recebidos"}), 400

    # Lê os registos atuais
    if os.path.exists(ARQUIVO_REGISTOS):
        with open(ARQUIVO_REGISTOS, "r") as f:
            registos = json.load(f)
    else:
        registos = []

    novo_registo = {
        "usuario": dados.get("usuario"),
        "entrada": dados.get("entrada"),
        "saida": dados.get("saida"),
        "duracao_servico": dados.get("duracao_servico")
    }

    registos.append(novo_registo)

    with open(ARQUIVO_REGISTOS, "w") as f:
        json.dump(registos, f, indent=4)

    print(f"[{datetime.now()}] Registo recebido e guardado: {novo_registo}")

    return jsonify({"status": "Registo guardado com sucesso"}), 200

# Função para iniciar o bot Discord numa thread separada
def start_bot():
    bot.run_bot()

