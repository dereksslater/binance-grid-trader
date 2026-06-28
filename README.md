🤖 Grid Trading Bot — Binance


Robô de automação para compra e venda de criptomoedas com a estratégia de Grid Trading, desenhado para mercados em lateralização (sem tendência definida), em que o preço oscila entre regiões de suporte e resistência.



Construído em Python, usando ccxt para conexão com a Binance e Flask para rodar 24/7 na nuvem (Render).


🧩 O que é Grid Trading?

Grid Trading ("negociação em grade") consiste em dividir uma faixa de preço em vários níveis e posicionar ordens automáticas de compra na baixa e venda na alta em cada nível. Em vez de tentar adivinhar o topo ou o fundo, o robô lucra com a oscilação natural do preço: cada vez que a moeda sobe e desce dentro da grade, um ciclo de compra/venda é fechado e o lucro é registrado.

A estratégia rende mais quando o mercado está "andando de lado" — sem uma tendência forte de alta ou de baixa.


🎯 Estratégia

O robô combina três ideias:


Grid em N níveis — Cada nível tem seu próprio preço de compra, preço de venda e valor de investimento. O código percorre a lista de níveis em loop, então funciona igual com 5 ou 50 níveis.
Acumulação gradual — Em vez de entrar com todo o capital de uma vez, o robô distribui o investimento entre os níveis, comprando aos poucos conforme o preço recua.
Preço médio em quedas — Se o preço cair abaixo dos níveis configurados, você pode adicionar novos níveis mais baixos para continuar comprando e reduzir o seu preço médio.

⚠️ Importante: essa tática só reduz o prejuízo se o preço se recuperar depois. Em uma queda prolongada, comprar mais a cada baixa aumenta sua exposição e o prejuízo não realizado. Use níveis e capital compatíveis com o seu perfil de risco (veja a seção Limitações importantes).




Cálculo de lucro real — A cada venda concluída, o robô calcula o lucro líquido (valor da venda − investimento da compra) e exibe o ganho em USDT nos logs.



🧠 Filosofia / Princípios

A lógica do robô — lucrar com a oscilação em vez de tentar prever o mercado — ecoa o que alguns dos maiores nomes de mercado já defenderam:


"Look at market fluctuations as your friend rather than your enemy; profit from folly rather than participate in it."
"Encare as flutuações do mercado como sua amiga, não sua inimiga; lucre com a irracionalidade em vez de participar dela."
— Warren Buffett




"Some things benefit from shocks; they thrive and grow when exposed to volatility, randomness, disorder, and stressors."
"Algumas coisas se beneficiam de choques; elas prosperam e crescem quando expostas à volatilidade, à aleatoriedade, à desordem e ao estresse."
— Nassim Nicholas Taleb, Antifrágil




"Risk comes from not knowing what you're doing."
"O risco vem de não saber o que você está fazendo."
— Warren Buffett



E a regra que nenhum robô substitui:


"Regra nº 1: nunca perca dinheiro. Regra nº 2: nunca esqueça a regra nº 1." — Warren Buffett




⚙️ Dependências

Requisito: Python 3.9+.

O projeto usa:


ccxt — conexão com a Binance
python-dotenv — leitura das chaves em ambiente local
flask — mantém um endpoint web ativo para o robô rodar 24/7 na nuvem (keep-alive)


Crie um arquivo requirements.txt na raiz do projeto com:

txtccxt
python-dotenv
flask

E instale tudo de uma vez:

bashpip install -r requirements.txt


Esse requirements.txt é o que o Render usa para instalar as dependências durante o deploy.




🔑 Configuração das chaves (API Binance)

As chaves nunca ficam no código. Onde você as coloca depende de onde o robô roda:

Localmente (testes): crie um arquivo .env na raiz:

envAPI_KEY=sua_chave_aqui
SECRET=sua_chave_secreta_aqui

Na nuvem (Render): configure as mesmas variáveis no painel do Render, em Environment → Environment Variables (e não suba o .env).


✏️ Confirme os nomes das variáveis no seu código. Aqui usei API_KEY e SECRET (os nomes configurados no seu Render). Se o seu código lê outros nomes — por exemplo BINANCE_API_KEY e BINANCE_SECRET — ajuste para bater exatamente, senão o robô não conecta.




🔒 Garanta que o .env está no .gitignore para as chaves nunca irem para o GitHub.




▶️ Rodando localmente (testes)

Com o .env criado e as dependências instaladas:

bashpython Robo_solana.py

Se o preço da moeda aparecer no terminal, está tudo certo. 🎉


Em Linux/Mac os nomes de arquivo diferenciam maiúsculas de minúsculas. Se aparecer "file not found", confira o nome exato com ls.




☁️ Deploy na nuvem (Render)

Para o robô operar 24/7 sem depender do seu computador ligado, ele roda como um Web Service no Render.

Por que Flask? Um Web Service do Render precisa responder em uma porta HTTP, ou a plataforma derruba o serviço por inatividade. O Flask mantém um endpoint simples vivo (keep-alive) enquanto o robô opera em segundo plano.

Primeira configuração:


No Render, clique em New → Web Service e conecte o seu repositório do GitHub.
Build Command: pip install -r requirements.txt
Start Command: python Robo_solana.py

✏️ Use o comando que de fato inicia o seu robô + Flask. Se você separou o servidor em outro arquivo (ex.: app.py com gunicorn), ajuste aqui.




Em Environment, adicione as variáveis API_KEY e SECRET com as suas chaves.
Clique em Create Web Service. O Render instala as dependências e sobe o robô.


A cada git push para o GitHub, o Render faz o deploy da nova versão automaticamente.


🔄 Atualizando o robô (nova versão)

Quando você corrigir ou melhorar o código, não precisa criar um serviço novo — você mantém o mesmo endereço e as variáveis de ambiente já configuradas.


Suba as mudanças para o GitHub (git push).
No painel do seu Web Service no Render:

Se ele estiver suspenso, clique em Resume para reativar.
Clique em Manual Deploy → Deploy latest commit.



Acompanhe os Logs: o Render roda o pip install e sobe o robô. Se aparecer a mensagem de inicialização do seu código, deu tudo certo. 🎉



💤 Mantendo o robô acordado (UptimeRobot)

No plano gratuito do Render, um Web Service pode entrar em modo de espera após um tempo sem receber acessos. O endpoint Flask já ajuda a manter o serviço ativo, mas se você notar que o robô para sozinho (por exemplo, de madrugada), dá pra reforçar com um serviço gratuito de monitoramento:


Crie uma conta no UptimeRobot.
Adicione um monitor do tipo HTTP(s) apontando para a URL do seu serviço (ex.: https://SEU-SERVICO.onrender.com).
Configure o intervalo para 5 minutos.


Assim o UptimeRobot "dá um tapinha" no robô a cada 5 minutos e o Render não o coloca para dormir.


Não é obrigatório — só vale a pena se você perceber que o serviço está hibernando. Comece sem ele e adicione apenas se precisar.




🛠️ Personalização

Todo o ajuste da estratégia é feito no arquivo Robo_solana.py.

Trocar a moeda

Altere a variável SYMBOL para o par desejado:

pythonSYMBOL = 'SOL/USDT'   # padrão
# SYMBOL = 'BTC/USDT' # Bitcoin
# SYMBOL = 'ETH/USDT' # Ethereum


💡 Ao trocar a moeda, atualize também os preços em niveis_grid — os valores de SOL não fazem sentido para BTC ou ETH.



Adicionar mais níveis (mais de 5)

A grade é uma lista de dicionários. Você pode adicionar quantos níveis quiser — o robô percorre a lista inteira em loop, não importa se ela tem 5 ou 50 itens:

pythonniveis_grid = [
    {"compra": 68.0, "venda": 72.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 60.0, "venda": 64.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    {"compra": 55.0, "venda": 60.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
    # Para acumular em quedas mais fortes, adicione níveis mais baixos:
    {"compra": 50.0, "venda": 55.0, "investimento": 29.0, "status": "AGUARDANDO_COMPRA", "qtd_sol": 0.0},
]

Cada nível precisa destes campos:

CampoSignificadocompraPreço-alvo para comprarvendaPreço-alvo para venderinvestimentoValor (em USDT) aplicado nesse nívelstatusEstado inicial — sempre "AGUARDANDO_COMPRA"qtd_solQuantidade comprada — começa em 0.0


📊 Cálculo de lucro

A cada ciclo concluído (uma compra seguida da venda correspondente), o robô calcula:

lucro = (preço de venda × quantidade) − investimento da compra

e exibe o resultado em USDT nos logs, para você acompanhar o ganho real de cada operação.


💡 Operações manuais e saldo da carteira

O robô opera na sua carteira Spot da Binance, usando o saldo de USDT (para comprar) e da moeda (para vender). Por isso, mexer manualmente nessa mesma carteira pode atrapalhar o robô e distorcer o cálculo de lucro.

Pontos de atenção:


Comprar/vender por fora interfere. Se você fizer operações manuais na mesma conta, o robô pode encontrar um saldo diferente do que esperava, e o lucro que ele calcula deixa de refletir só as operações dele.
Saldo insuficiente. Se você gastar o USDT da carteira Spot comprando algo manualmente, o robô vai tentar comprar em um nível, não vai encontrar saldo, e vai retornar erro de "saldo insuficiente" (insufficient balance).
Não deixe a Spot zerada. Sempre mantenha uma reserva de USDT na carteira Spot para o robô conseguir operar os níveis configurados.


Como evitar conflito (do mais seguro para o mais simples):


Conta ou subconta dedicada (recomendado). Use uma conta — ou uma subconta da Binance — só para o robô. Assim, suas operações manuais e de longo prazo ficam totalmente separadas do saldo que o robô usa, e um nunca atrapalha o outro.
Pause o robô antes de operar. Antes de uma operação manual grande, suspenda o serviço no Render (ou pare o robô). Depois é só dar Resume / Deploy novamente.
Guarde o que é seu na carteira Earn. Se quiser manter moedas paradas (longo prazo) sem que o robô as use, mova-as para a Binance Earn, que fica separada da Spot. Mas atenção: isso não resolve sozinho — se você esvaziar o USDT da Spot, o robô ainda vai dar erro de saldo insuficiente. A reserva de operação precisa continuar na Spot.



Em resumo: decida se a conta é "do robô" ou "sua, para trade manual". Misturar as duas coisas na mesma carteira Spot é o que mais causa erro.




⚠️ Limitações importantes


Funciona melhor em mercado lateral. Em uma alta forte, o robô vende cedo demais e fica de fora da subida. Em uma queda forte e prolongada, ele continua comprando e acumula prejuízo não realizado.
Preço médio pressupõe recuperação. Comprar mais na baixa só ajuda se o ativo voltar a subir. Se a moeda cair e não se recuperar, a estratégia amplia a perda.
Teste antes com pouco. Valide o comportamento com valores pequenos (ou em conta de teste) antes de aplicar capital de verdade.



🔒 Segurança


As chaves de API ficam apenas no .env local (protegido pelo .gitignore) ou nas variáveis de ambiente do Render — nunca no repositório.
Nunca compartilhe o seu .env nem cole suas chaves em prints ou no código.
Na Binance, considere restringir as permissões da chave de API (por exemplo, sem permissão de saque).



⚠️ Aviso de Responsabilidade (Disclaimer)

Este software é fornecido apenas para fins educacionais e de estudo. Operar ativos financeiros com robôs envolve risco real de perda de capital.


Decisão própria. A estratégia, os níveis de preço e o gerenciamento de risco são de inteira responsabilidade de quem usa.
Não é recomendação. Este projeto não constitui recomendação de investimento nem aconselhamento financeiro.
Mercado volátil. O mercado de criptomoedas é altamente volátil. Use apenas valores que você pode perder sem comprometer suas finanças.
