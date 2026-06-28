from flask import Flask, render_template
from threading import Thread
import os
import time
import json
import ccxt
from dotenv import load_dotenv
from upstash_redis import Redis

# ============================================================
# ESTADO GLOBAL  (compartilhado entre o robô e a tela/dashboard)
# ============================================================
SYMBOL = 'SOL/USDT'
preco_atual = 0.0
lucro_total = 0.0
ultima_atualizacao = "iniciando..."
status_robo = "Conectando..."
redis_db = None  # conexão com o banco (Upstash), criada na inicialização

# Seu Grid de 5 Níveis
niveis_grid = [
    {"compra": 68.0, "venda": 72.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 65.0, "venda": 70.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 62.0, "venda": 67.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 60.0, "venda": 65.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 58.0, "venda": 63.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
]

# ============================================================
# MEMÓRIA PERSISTENTE (Upstash Redis) — sobrevive a reinícios
# ============================================================
def salvar_estado():
    """Salva o estado atual no banco. Chamado após cada compra/venda."""
    if redis_db is None:
        return
    try:
        estado = {"niveis": niveis_grid, "lucro_total": lucro_total}
        redis_db.set("estado_robo", json.dumps(estado))
    except Exception as e:
        print(f"⚠️ Falha ao salvar estado: {e}")

def carregar_estado():
    """Recupera o estado salvo na inicialização (se existir)."""
    global lucro_total
    if redis_db is None:
        return
    try:
        dados = redis_db.get("estado_robo")
        if dados:
            estado = json.loads(dados)
            salvos = estado.get("niveis", [])
            for i in range(min(len(niveis_grid), len(salvos))):
                niveis_grid[i]["status"] = salvos[i]["status"]
                niveis_grid[i]["qtd_sol"] = salvos[i]["qtd_sol"]
            lucro_total = estado.get("lucro_total", 0.0)
            print("✅ Estado anterior recuperado do banco. Continuando de onde parou.\n")
        else:
            print("ℹ️ Nenhum estado salvo ainda (primeira execução).\n")
    except Exception as e:
        print(f"⚠️ Não foi possível carregar o estado: {e}\n")

# ============================================================
# TELA / DASHBOARD (Flask)
# O HTML fica em templates/index.html — aqui só passamos os dados.
# ============================================================
app = Flask(__name__)

@app.route('/')
def home():
    return render_template(
        'index.html',
        symbol=SYMBOL,
        preco=preco_atual,
        lucro=lucro_total,
        status=status_robo,
        atualizacao=ultima_atualizacao,
        niveis=niveis_grid,
    )

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ============================================================
# ROBÔ (loop principal)
# ============================================================
def rodar_robo():
    global preco_atual, lucro_total, ultima_atualizacao, status_robo, redis_db

    load_dotenv()

    # Conecta no banco (memória persistente)
    if not os.environ.get("UPSTASH_REDIS_REST_URL"):
        print("⚠️ Variáveis do Upstash não configuradas — rodando SEM memória persistente!\n")
    else:
        redis_db = Redis(
            url=os.environ.get("UPSTASH_REDIS_REST_URL"),
            token=os.environ.get("UPSTASH_REDIS_REST_TOKEN"),
        )

    exchange = ccxt.binance({
        'apiKey': os.environ.get('BINANCE_API_KEY'),
        'secret': os.environ.get('BINANCE_SECRET'),
        'enableRateLimit': True,
    })
    exchange.load_markets()  # necessário para arredondar as ordens corretamente

    carregar_estado()  # recupera o que o robô já tinha feito antes de reiniciar

    print(f"=== 🔴 ROBÔ OFICIAL INICIADO PARA {SYMBOL} ===\n")
    status_robo = "🟢 Rodando"

    while True:
        try:
            ticker = exchange.fetch_ticker(SYMBOL)
            preco_atual = ticker['last']
            ultima_atualizacao = time.strftime('%H:%M:%S')
            print(f"[{ultima_atualizacao}] Preço atual da SOL: ${preco_atual:.2f}")

            for i, nivel in enumerate(niveis_grid):
                # ---------- COMPRA ----------
                if nivel["status"] == "AGUARDANDO_COMPRA" and preco_atual <= nivel["compra"]:
                    qtd = float(exchange.amount_to_precision(SYMBOL, nivel["investimento"] / preco_atual))
                    print(f"\n🛒 [Nível {i+1}] ENVIANDO ORDEM DE COMPRA...")

                    ordem = exchange.create_market_buy_order(SYMBOL, qtd)
                    # guarda um pouco menos para cobrir a taxa cobrada em SOL (~0,1%)
                    nivel["qtd_sol"] = float(ordem['filled']) * 0.999
                    nivel["status"] = "AGUARDANDO_VENDA"
                    salvar_estado()  # <- salva imediatamente após a compra
                    print(f"   ✓ Compra executada! {nivel['qtd_sol']:.4f} SOL guardadas.\n")

                # ---------- VENDA ----------
                elif nivel["status"] == "AGUARDANDO_VENDA" and preco_atual >= nivel["venda"]:
                    qtd_vender = float(exchange.amount_to_precision(SYMBOL, nivel["qtd_sol"]))
                    print(f"\n💰 [Nível {i+1}] ENVIANDO ORDEM DE VENDA...")

                    ordem = exchange.create_market_sell_order(SYMBOL, qtd_vender)
                    preco_venda = ordem.get('average') or preco_atual
                    faturamento = float(ordem['filled']) * preco_venda
                    # desconta uma estimativa das taxas (compra + venda, ~0,1% cada)
                    taxa = (nivel["investimento"] + faturamento) * 0.001
                    lucro = faturamento - nivel["investimento"] - taxa
                    lucro_total += lucro

                    nivel["status"] = "AGUARDANDO_COMPRA"
                    nivel["qtd_sol"] = 0.0
                    salvar_estado()  # <- salva imediatamente após a venda
                    print(f"   ✓ Venda executada! Lucro estimado: +${lucro:.2f} USDT")
                    print(f"   Gaveta {i+1} resetada.\n")

            time.sleep(10)

        except ccxt.InsufficientFunds:
            status_robo = "⚠️ Saldo insuficiente"
            print("\n❌ Saldo insuficiente. Aguardando...")
            time.sleep(30)
        except Exception as e:
            status_robo = "⚠️ Erro (tentando de novo)"
            print(f"⚠️ Erro: {e}. Tentando novamente em 15s...")
            time.sleep(15)

# ============================================================
# INICIALIZAÇÃO
# ============================================================
if __name__ == "__main__":
    Thread(target=run_flask).start()   # tela / dashboard
    rodar_robo()                        # robô (loop principal)