# 🤖 Grid Trading Bot — Binance

> Robô de automação para compra e venda de criptomoedas com a estratégia de **Grid Trading**, desenhado para mercados em **lateralização** (sem tendência definida), em que o preço oscila entre regiões de suporte e resistência.

Construído em **Python**, usando a biblioteca [`ccxt`](https://github.com/ccxt/ccxt) para conexão com a Binance.

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
  > ⚠️ **Importante:** essa tática só reduz o prejuízo *se o preço se recuperar depois*. Em uma queda prolongada, comprar mais a cada baixa aumenta sua exposição e o prejuízo não realizado. Use níveis e capital compatíveis com o seu perfil de risco (veja a seção **Limitações importantes**).
- **Cálculo de lucro real** — A cada venda concluída, o robô calcula o lucro líquido (valor da venda − investimento da compra) e exibe o ganho em USDT no terminal.

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

## ⚙️ Instalação

Requisito: **Python 3.9+**.

Instale as dependências:

```bash
pip install ccxt python-dotenv
```

---

## 🔑 Configuração (.env)

Crie um arquivo chamado `.env` na raiz do projeto com as suas chaves da Binance:

```env
BINANCE_API_KEY=sua_chave_aqui
BINANCE_SECRET=sua_chave_secreta_aqui
```

> 🔒 O `.env` **nunca** deve ser enviado para o GitHub. Confira se ele está listado no seu `.gitignore`.

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

A grade é uma lista de dicionários. Você pode adicionar **quantos níveis quiser** — o robô percorre a lista inteira em loop, não importa se ela tem 5 ou 50 itens:

```python
niveis_grid = [
    {"compra": 68.0, "venda": 72.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 60.0, "venda": 64.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 55.0, "venda": 60.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    # Para acumular em quedas mais fortes, adicione níveis mais baixos:
    {"compra": 50.0, "venda": 55.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
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

## ▶️ Como rodar

Com o `.env` criado e os níveis ajustados, execute:

```bash
python Robo_solana.py
```

Se o preço da moeda aparecer no terminal, está tudo certo. 🎉

> Em Linux/Mac os nomes de arquivo diferenciam maiúsculas de minúsculas. Se aparecer "file not found", confira o nome exato com `ls`.

---

## 📊 Cálculo de lucro

A cada ciclo concluído (uma compra seguida da venda correspondente), o robô calcula:

```
lucro = (preço de venda × quantidade) − investimento da compra
```

e exibe o resultado em **USDT** no terminal, para você acompanhar o ganho real de cada operação.

---

## ⚠️ Limitações importantes

- **Funciona melhor em mercado lateral.** Em uma alta forte, o robô vende cedo demais e fica de fora da subida. Em uma queda forte e prolongada, ele continua comprando e acumula **prejuízo não realizado**.
- **Preço médio pressupõe recuperação.** Comprar mais na baixa só ajuda se o ativo voltar a subir. Se a moeda cair e não se recuperar, a estratégia amplia a perda.
- **Teste antes com pouco.** Valide o comportamento com valores pequenos (ou em conta de teste) antes de aplicar capital de verdade.

---

## 🔒 Segurança

- As chaves de API ficam apenas no arquivo `.env` local, protegido pelo `.gitignore`.
- Nunca compartilhe o seu `.env` nem cole suas chaves em prints ou no código.
- Na Binance, considere restringir as permissões da chave de API (por exemplo, sem permissão de saque).

---

## ⚠️ Aviso de Responsabilidade (Disclaimer)

Este software é fornecido **apenas para fins educacionais e de estudo**. Operar ativos financeiros com robôs envolve **risco real de perda de capital**.

- **Decisão própria.** A estratégia, os níveis de preço e o gerenciamento de risco são de inteira responsabilidade de quem usa.
- **Não é recomendação.** Este projeto **não** constitui recomendação de investimento nem aconselhamento financeiro.
- **Mercado volátil.** O mercado de criptomoedas é altamente volátil. Use apenas valores que você pode perder sem comprometer suas finanças.