import time
import ccxt
import os
from dotenv import load_dotenv  # Importante para carregar as chaves locais

# Carrega as variáveis do arquivo .env (só funciona no seu PC)
load_dotenv()

# =====================================================================
# CONEXÃO COM A BINANCE (DADOS PUXADOS DO SISTEMA)
# =====================================================================
# O código busca no arquivo .env (PC) ou nas variáveis de ambiente (Render)
exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET'),
    'enableRateLimit': True,
})

SYMBOL = 'SOL/USDT'

# O seu Grid Real de 5 Níveis
niveis_grid = [
    {"compra": 68.0, "venda": 72.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 65.0, "venda": 70.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 62.0, "venda": 67.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 60.0, "venda": 65.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 58.0, "venda": 63.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
]

print(f"=== 🔴 ROBÔ OFICIAL INICIADO PARA {SYMBOL} ===\n")

while True:
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        preco_atual = ticker['last']
        
        print(f"[{time.strftime('%H:%M:%S')}] Preço atual da SOL: ${preco_atual:.2f}")

        for i, nivel in enumerate(niveis_grid):
            # Lógica de Compra
            if nivel["status"] == "AGUARDANDO_COMPRA" and preco_atual <= nivel["compra"]:
                qtd_comprar = nivel["investimento"] / preco_atual
                print(f"\n🛒 [Nível {i+1}] ENVIANDO ORDEM DE COMPRA...")
                
                ordem_compra = exchange.create_market_buy_order(SYMBOL, qtd_comprar)
                nivel["qtd_sol"] = ordem_compra['filled']
                nivel["status"] = "AGUARDANDO_VENDA"
                print(f"   ✓ Compra executada! {nivel['qtd_sol']:.4f} SOL guardadas.\n")

            # Lógica de Venda
            elif nivel["status"] == "AGUARDANDO_VENDA" and preco_atual >= nivel["venda"]:
                print(f"\n💰 [Nível {i+1}] ENVIANDO ORDEM DE VENDA...")
                
                ordem_venda = exchange.create_market_sell_order(SYMBOL, nivel["qtd_sol"])
                faturamento = ordem_venda['filled'] * preco_atual
                lucro = faturamento - nivel["investimento"]
                
                print(f"   ✓ Venda executada! Lucro estimado: +${lucro:.2f} USDT")
                nivel["status"] = "AGUARDANDO_COMPRA"
                nivel["qtd_sol"] = 0.0
                print(f"   Gaveta {i+1} resetada.\n")

        time.sleep(10)

    except ccxt.InsufficientFunds:
        print("\n❌ ERRO FATAL: Saldo insuficiente na conta.")
        time.sleep(30)
    except Exception as e:
        print(f"⚠️ Erro: {e}. Tentando novamente em 15s...")
        time.sleep(15)