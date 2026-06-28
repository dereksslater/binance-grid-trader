# 🤖 Grid Trading Bot — Binance

> Robô de automação para compra e venda de criptomoedas com a estratégia de **Grid Trading**, desenhado para mercados em **lateralização** (sem tendência definida), em que o preço oscila entre regiões de suporte e resistência.

Construído em **Python**, usando [`ccxt`](https://github.com/ccxt/ccxt) para conexão com a Binance e **Flask** para servir um painel web de acompanhamento. Roda no seu computador ou em uma **VPS**.

---

## ✨ Funcionalidades

- **Grid em N níveis** — compra na baixa e venda na alta, em quantos níveis você quiser.
- **Painel web (dashboard)** — acompanhe preço, lucro acumulado e o status de cada nível pelo navegador.
- **Memória persistente** — o estado é salvo (Upstash Redis) e sobrevive a reinícios.
- **Cálculo de lucro** — registra o lucro líquido (já descontando uma estimativa das taxas) a cada venda.

---

## 🧩 O que é Grid Trading?

Grid Trading ("negociação em grade") consiste em dividir uma faixa de preço em vários níveis e posicionar ordens automáticas de **compra na baixa** e **venda na alta** em cada nível. Em vez de tentar adivinhar o topo ou o fundo, o robô lucra com a **oscilação natural** do preço: cada vez que a moeda sobe e desce dentro da grade, um ciclo de compra/venda é fechado e o lucro é registrado.

A estratégia rende mais quando o mercado está "andando de lado" — sem uma tendência forte de alta ou de baixa.

---

## 🎯 Estratégia

O robô combina três ideias:

- **Grid em N níveis** — Cada nível tem seu próprio preço de compra, preço de venda e valor de investimento. O código percorre a lista de níveis em loop, então funciona igual com 5 ou 50 níveis.
- **Acumulação gradual** — Em vez de entrar com todo o capital de uma vez, o robô distribui o investimento entre os níveis, comprando aos poucos conforme o preço recua.
- **Preço médio em quedas** — Se o preço cair abaixo dos níveis configurados, você pode adicionar novos níveis mais baixos para continuar comprando e reduzir o seu preço médio.
  > ⚠️ **Importante:** essa tática só reduz o prejuízo *se o preço se recuperar depois*. Em uma queda prolongada, comprar mais a cada baixa aumenta sua exposição e o prejuízo não realizado. Use níveis e capital compatíveis com o seu perfil de risco (veja **Limitações importantes**).
- **Cálculo de lucro real** — A cada venda concluída, o robô calcula o lucro líquido e exibe o ganho em USDT nos logs e no painel.

---

## 🧠 Filosofia / Princípios

A lógica do robô — lucrar com a oscilação em vez de tentar prever o mercado — ecoa o que alguns dos maiores nomes de mercado já defenderam:

> "Look at market fluctuations as your friend rather than your enemy; profit from folly rather than participate in it."
> *"Encare as flutuações do mercado como sua amiga, não sua inimiga; lucre com a irracionalidade em vez de participar dela."*
> — **Warren Buffett**

> "Some things benefit from shocks; they thrive and grow when exposed to volatility, randomness, disorder, and stressors."
> *"Algumas coisas se beneficiam de choques; elas prosperam e crescem quando expostas à volatilidade, à aleatoriedade, à desordem e ao estresse."*
> — **Nassim Nicholas Taleb**, *Antifrágil*

> "Risk comes from not knowing what you're doing."
> *"O risco vem de não saber o que você está fazendo."*
> — **Warren Buffett**

E a regra que nenhum robô substitui:

> "Regra nº 1: nunca perca dinheiro. Regra nº 2: nunca esqueça a regra nº 1." — **Warren Buffett**

---

## ⚙️ Dependências

Requisito: **Python 3.9+**.

Crie um arquivo `requirements.txt` na raiz do projeto com:

```txt
ccxt
python-dotenv
flask
upstash-redis
```

E instale tudo de uma vez:

```bash
pip install -r requirements.txt
```

O que cada uma faz: `ccxt` (conexão com a Binance), `python-dotenv` (lê as chaves do `.env`), `flask` (serve o painel web) e `upstash-redis` (memória persistente que sobrevive a reinícios).

---

## 🗂️ Estrutura do projeto

```
robo_binance/
├── Robo_solana.py        # o robô + o painel
├── requirements.txt
├── .env                  # suas chaves (NÃO sobe pro GitHub)
├── .gitignore
└── templates/
    └── index.html        # o layout do painel
```

> O `index.html` **precisa** ficar dentro de uma pasta chamada exatamente `templates/`, no mesmo nível do `Robo_solana.py` — é ali que o Flask procura o painel.

---

## 🔑 Configuração das chaves (.env)

As chaves **nunca** ficam no código. Crie um arquivo `.env` na raiz:

```env
BINANCE_API_KEY=sua_chave_aqui
BINANCE_SECRET=sua_chave_secreta_aqui

# Memória persistente (opcional, mas recomendado) — conta grátis em upstash.com
UPSTASH_REDIS_REST_URL=sua_url_aqui
UPSTASH_REDIS_REST_TOKEN=seu_token_aqui
```

> 🔒 Garanta que o `.env` está no `.gitignore` para as chaves nunca irem para o GitHub. Se as variáveis do Upstash não forem configuradas, o robô avisa nos logs e roda sem memória persistente.

---

## ▶️ Rodando localmente

Com o `.env` criado, as dependências instaladas e o `index.html` dentro de `templates/`:

```bash
python Robo_solana.py
```

O robô começa a mostrar o preço no terminal, e o painel fica disponível em **`http://localhost:10000`**.

> Em Linux/Mac os nomes de arquivo diferenciam maiúsculas de minúsculas. Se aparecer "file not found", confira o nome exato com `ls`.

---

## ⚠️ Limitações de Deploy (Render e nuvem pública)

**Este robô não funciona em plataformas de nuvem como o Render.** Ao tentar conectar a API da Binance a partir desses servidores, a conexão retorna o erro:

```
451: Service unavailable from a restricted location
```

Por que isso acontece:

- A Binance **bloqueia chamadas de API vindas de "localizações restritas"** (Estados Unidos, entre outras) e, cada vez mais, de faixas de IP de datacenters de nuvem pública.
- O **Render roda os serviços em datacenters nos EUA** (região padrão), que é uma localização restrita pela Binance. Por isso a API responde com 451 e o robô não consegue operar.
- É por isso que o robô **funciona no seu computador** (IP residencial, em região liberada) **mas falha no Render**.

O mesmo problema atinge outras plataformas de aplicação web (Google Cloud Functions, PythonAnywhere, Heroku etc.) quando o servidor está numa região restrita.

---

## 🖥️ Hospedagem recomendada (VPS)

Para rodar de forma estável **24/7**, use uma **VPS (Virtual Private Server)**, onde você escolhe a região e tem mais controle sobre o IP:

- Escolha uma **região fora da lista de locais restritos** da Binance (evite os EUA).
- Há vários provedores de VPS (por exemplo, DigitalOcean, Hetzner, Contabo, entre outros). O que mais importa é a **região**, não a marca.
- Na VPS, o robô roda continuamente em segundo plano — com ferramentas como `screen`, `tmux` ou um serviço `systemd` — e o painel Flask fica acessível pelo IP da VPS.

> Resumindo: rode **local** para testar e use uma **VPS em região liberada** para deixar o robô no ar 24/7. O Render serve bem para sites/APIs, mas não para conectar na Binance.

---

## 🛠️ Personalização

Todo o ajuste da estratégia é feito no arquivo `Robo_solana.py`.

### Trocar a moeda

Altere a variável `SYMBOL` para o par desejado:

```python
SYMBOL = 'SOL/USDT'   # padrão
# SYMBOL = 'BTC/USDT' # Bitcoin
# SYMBOL = 'ETH/USDT' # Ethereum
```

> 💡 Ao trocar a moeda, **atualize também os preços** em `niveis_grid` — os valores de SOL não fazem sentido para BTC ou ETH.

### Adicionar mais níveis (mais de 5)

A grade é uma lista de dicionários. Você pode adicionar **quantos níveis quiser** — o robô percorre a lista inteira em loop:

```python
niveis_grid = [
    {"compra": 68.0, "venda": 72.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 65.0, "venda": 70.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 62.0, "venda": 67.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    # Para acumular em quedas mais fortes, adicione níveis mais baixos:
    {"compra": 58.0, "venda": 63.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
]
```

Cada nível precisa destes campos:

| Campo | Significado |
|---|---|
| `compra` | Preço-alvo para comprar |
| `venda` | Preço-alvo para vender |
| `investimento` | Valor (em USDT) aplicado nesse nível |
| `status` | Estado inicial — sempre `"AGUARDANDO_COMPRA"` |
| `qtd_sol` | Quantidade comprada — começa em `0.0` |

---

## 📊 Cálculo de lucro

A cada ciclo concluído (uma compra seguida da venda correspondente), o robô calcula:

```
lucro = (preço de venda × quantidade) − investimento − estimativa de taxas
```

e exibe o resultado em **USDT** nos logs e no painel, para você acompanhar o ganho real de cada operação.

---

## 💡 Operações manuais e saldo da carteira

O robô opera na sua **carteira Spot** da Binance, usando o saldo de USDT (para comprar) e da moeda (para vender). Por isso, **mexer manualmente nessa mesma carteira pode atrapalhar o robô** e distorcer o cálculo de lucro.

**Pontos de atenção:**

- **Comprar/vender por fora interfere.** O robô pode encontrar um saldo diferente do esperado, e o lucro calculado deixa de refletir só as operações dele.
- **Saldo insuficiente.** Se você gastar o USDT da Spot comprando algo manualmente, o robô tenta comprar num nível, não acha saldo, e retorna erro de **"saldo insuficiente"**.
- **Não deixe a Spot zerada.** Mantenha sempre uma reserva de USDT na Spot para o robô conseguir operar os níveis.

**Como evitar conflito (do mais seguro para o mais simples):**

1. **Conta ou subconta dedicada (recomendado).** Use uma conta — ou uma *subconta* da Binance — só para o robô.
2. **Pause o robô antes de operar.** Antes de uma operação manual grande, pare o robô; depois é só ligar de novo.
3. **Guarde o que é seu na carteira Earn.** Para manter moedas paradas sem que o robô as use, mova-as para a **Binance Earn** (separada da Spot). Mas atenção: se esvaziar o USDT da Spot, o erro de saldo insuficiente volta — a reserva de operação precisa continuar na Spot.

> Em resumo: decida se a conta é "do robô" ou "sua, para trade manual". Misturar as duas coisas na mesma carteira Spot é o que mais causa erro.

---

## ⚠️ Limitações importantes

- **Funciona melhor em mercado lateral.** Em uma alta forte, o robô vende cedo demais e fica de fora da subida. Em uma queda forte e prolongada, ele continua comprando e acumula **prejuízo não realizado**.
- **Preço médio pressupõe recuperação.** Comprar mais na baixa só ajuda se o ativo voltar a subir.
- **Teste antes com pouco.** Valide o comportamento com valores pequenos (ou em conta de teste) antes de aplicar capital de verdade.

---

## 🔒 Segurança

- As chaves de API ficam apenas no `.env` local (protegido pelo `.gitignore`) — nunca no repositório.
- Nunca compartilhe o seu `.env` nem cole suas chaves em prints ou no código.
- Na Binance, considere restringir as permissões da chave de API (por exemplo, sem permissão de saque).

---

## ⚠️ Aviso de Responsabilidade (Disclaimer)

Este software é fornecido **apenas para fins educacionais e de estudo**. Operar ativos financeiros com robôs envolve **risco real de perda de capital**.

- **Decisão própria.** A estratégia, os níveis de preço e o gerenciamento de risco são de inteira responsabilidade de quem usa.
- **Não é recomendação.** Este projeto **não** constitui recomendação de investimento nem aconselhamento financeiro.
- **Mercado volátil.** O mercado de criptomoedas é altamente volátil. Use apenas valores que você pode perder sem comprometer suas finanças.