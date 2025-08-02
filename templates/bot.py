import discord
from discord.ext import commands
import datetime
import json
import os
from dotenv import load_dotenv
import requests

# Carrega o .env
dotenv_path = r'C:\Users\jo429\Desktop\GNR\.env'
load_dotenv(dotenv_path)

# Obtém o token do .env
TOKEN = os.getenv("MTM5NjEzMTc4NjE3NzkwODgwNw.Gf7BkV.NXflaNhlifEbnPoWJHNmFpxcUWTx1kqhGYG40M")

if TOKEN is None:
    print("❌ Não foi possível carregar o TOKEN.")
else:
    print("✅ TOKEN carregado com sucesso")

# Configuração do bot e intents
intents = discord.Intents.default()
intents.message_content = True  # Necessário para acessar o conteúdo das mensagens

bot = commands.Bot(command_prefix="!", intents=intents)

# Caminho do ficheiro de registos
FICHEIRO_REGISTOS = "registos.json"

# Carrega registos existentes
if os.path.exists(FICHEIRO_REGISTOS):
    with open(FICHEIRO_REGISTOS, "r") as f:
        registos = json.load(f)
else:
    registos = {}

@bot.event
async def on_ready():
    print(f"✅ Bot está online como {bot.user}")

# Comando !entrar - Registra a entrada com um Embed
@bot.command()
async def entrar(ctx):
    user_id = str(ctx.author.id)
    nome = str(ctx.author)
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Garantir que a chave 'dias' e 'pausas' estão presentes para cada usuário
    if user_id not in registos:
        registos[user_id] = {"nome": nome, "dias": [], "pausas": []}

    dias = registos[user_id]["dias"]

    # Verifica se já há entrada sem saída
    if dias and "saida" not in dias[-1]:
        await ctx.send(f"{nome}, você já registrou sua entrada hoje! 🚫")
        return

    dias.append({"entrada": agora})

    with open(FICHEIRO_REGISTOS, "w") as f:
        json.dump(registos, f, indent=4)

    # Criando o Embed para a mensagem de entrada
    embed = discord.Embed(
        title=f"🕓 **Entrada Registrada**",
        description=f"**{nome}**, sua entrada foi registrada com sucesso! ✅",
        color=discord.Color.green()  # Cor do embed
    )
    embed.add_field(name="Hora de Entrada:", value=f"**{agora}**", inline=False)
    embed.add_field(name="Usuário:", value=f"{nome}", inline=False)

    # Enviando o Embed como resposta
    await ctx.send(embed=embed)

# Comando !sair - Registra a saída com um Embed
@bot.command()
async def sair(ctx):
    user_id = str(ctx.author.id)
    nome = str(ctx.author)
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in registos or not registos[user_id]["dias"]:
        await ctx.send(f"{nome}, ainda não tens nenhuma entrada registrada. ⏳")
        return

    dias = registos[user_id]["dias"]

    if "saida" in dias[-1]:
        await ctx.send(f"{nome}, você já registrou sua saída hoje! ⛔")
        return

    dias[-1]["saida"] = agora

    with open(FICHEIRO_REGISTOS, "w") as f:
        json.dump(registos, f, indent=4)

    # Criando o Embed para a mensagem de saída
    embed = discord.Embed(
        title=f"⏹️ **Saída Registrada**",
        description=f"**{nome}**, sua saída foi registrada com sucesso! ✅",
        color=discord.Color.red()  # Cor do embed
    )
    embed.add_field(name="Hora de Saída:", value=f"**{agora}**", inline=False)
    embed.add_field(name="Usuário:", value=f"{nome}", inline=False)

    # Enviando o Embed como resposta
    await ctx.send(embed=embed)

# Comando !pausa - Registra o início ou retoma a pausa com um Embed
@bot.command()
async def pausa(ctx):
    user_id = str(ctx.author.id)
    nome = str(ctx.author)
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Garantir que a chave 'pausas' está presente para cada usuário
    if user_id not in registos:
        registos[user_id] = {"nome": nome, "dias": [], "pausas": []}  # Inicializa 'pausas' corretamente

    # Garantir que a chave 'pausas' exista e inicializar como lista vazia, caso contrário
    pausas = registos[user_id].get("pausas", [])

    # Se o usuário tem uma pausa em andamento (sem "fim" registrado), registrar o fim da pausa
    if pausas and "fim" not in pausas[-1]:
        # Registra o fim da pausa
        pausas[-1]["fim"] = agora

        with open(FICHEIRO_REGISTOS, "w") as f:
            json.dump(registos, f, indent=4)

        # Calculando o tempo da pausa
        inicio = datetime.datetime.strptime(pausas[-1]["inicio"], "%Y-%m-%d %H:%M:%S")
        fim = datetime.datetime.strptime(pausas[-1]["fim"], "%Y-%m-%d %H:%M:%S")
        duracao_pausa = fim - inicio

        # Criando o Embed para a mensagem de retomada da pausa
        embed = discord.Embed(
            title=f"☕ **Pausa Retomada**",
            description=f"**{nome}**, sua pausa foi retomada com sucesso! ⏸️",
            color=discord.Color.orange()  # Cor do embed
        )
        embed.add_field(name="Hora de Pausa Iniciada:", value=f"**{pausas[-1]['inicio']}**", inline=False)
        embed.add_field(name="Hora de Pausa Retomada:", value=f"**{agora}**", inline=False)
        embed.add_field(name="Duração da Pausa:", value=f"**{str(duracao_pausa)}**", inline=False)
        embed.add_field(name="Usuário:", value=f"{nome}", inline=False)

        # Enviando o Embed como resposta
        await ctx.send(embed=embed)

    else:
        # Se o usuário não tiver uma pausa em andamento, iniciar uma nova pausa
        pausas.append({"inicio": agora})  # Registra o início da pausa

        with open(FICHEIRO_REGISTOS, "w") as f:
            json.dump(registos, f, indent=4)

        # Criando o Embed para a mensagem de nova pausa
        embed = discord.Embed(
            title=f"☕ **Pausa Registrada**",
            description=f"**{nome}**, sua pausa foi registrada com sucesso! ⏸️",
            color=discord.Color.orange()  # Cor do embed
        )
        embed.add_field(name="Hora de Início da Pausa:", value=f"**{agora}**", inline=False)
        embed.add_field(name="Usuário:", value=f"{nome}", inline=False)

        # Enviando o Embed como resposta
        await ctx.send(embed=embed)

# Comando !minhas_horas - Envia os dados diretamente para o site (sem embed no Discord)
@bot.command()
async def minhas_horas(ctx):
    user_id = str(ctx.author.id)
    nome = str(ctx.author)

    # Garantir que o usuário tenha a chave 'pausas' inicializada corretamente
    if user_id not in registos:
        registos[user_id] = {"nome": nome, "dias": [], "pausas": []}  # Inicializa 'pausas' corretamente
    if "pausas" not in registos[user_id]:
        registos[user_id]["pausas"] = []  # Garante que 'pausas' está sempre presente

    if not registos[user_id]["dias"]:
        await ctx.send(f"**{nome}**, você ainda não registrou nenhum tempo. ⏳")
        return

    dias = registos[user_id]["dias"]
    pausas = registos[user_id]["pausas"]
    formato = "%Y-%m-%d %H:%M:%S"
    total = datetime.timedelta()
    total_pausa = datetime.timedelta()

    # Processando os dias de trabalho
    for i, dia in enumerate(dias, 1):
        entrada = dia.get("entrada", "—")
        saida = dia.get("saida", "—")

        duracao = "—"
        if entrada != "—" and saida != "—":
            t1 = datetime.datetime.strptime(entrada, formato)
            t2 = datetime.datetime.strptime(saida, formato)
            tempo = t2 - t1
            total += tempo
            duracao = str(tempo)

    # Processando as pausas
    for i, pausa in enumerate(pausas, 1):
        inicio = pausa.get("inicio", "—")
        fim = pausa.get("fim", "—")

        duracao_pausa = "—"
        if inicio != "—" and fim != "—":
            t1 = datetime.datetime.strptime(inicio, formato)
            t2 = datetime.datetime.strptime(fim, formato)
            tempo_pausa = t2 - t1
            total_pausa += tempo_pausa
            duracao_pausa = str(tempo_pausa)

    # Enviar os dados para o servidor (site)
    api_url = "http://127.0.0.1:5000/registrar_horas"  # URL do seu servidor Flask
    payload = {
        "usuario": nome,
        "dias": [{"entrada": dia["entrada"], "saida": dia["saida"]} for dia in dias],
        "pausas": [{"inicio": pausa["inicio"], "fim": pausa["fim"]} for pausa in pausas],
        "total_trabalhado": str(total),
        "total_pausas": str(total_pausa)
    }

    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            await ctx.send(f"✅ **{nome}**, seus dados de horas e pausas foram enviados para o site com sucesso!")
        else:
            await ctx.send(f"❌ **{nome}**, ocorreu um erro ao enviar os dados: {response.status_code}")
    except Exception as e:
        await ctx.send(f"❌ **{nome}**, ocorreu um erro ao tentar enviar os dados para o site: {str(e)}")

# Iniciar o bot com o token carregado do .env
bot.run("MTM5NjEzMTc4NjE3NzkwODgwNw.Gf7BkV.NXflaNhlifEbnPoWJHNmFpxcUWTx1kqhGYG40M")
