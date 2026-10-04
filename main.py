# Importação das bibliotecas
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

# Criar as funções de carregamento de dados
    # Cotações do Itau - ITUB4 - 2010 a 2024
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    data_inicio = (date.today() - relativedelta(years=2)).strftime("%Y-%m-%d")
    data_hoje = date.today().strftime("%Y-%m-%d")
    cotacao_acao = dados_acao.history(start=data_inicio, end=data_hoje)
    cotacao_acao = cotacao_acao["Close"]
    return cotacao_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("./dataset/IBOV.csv", sep=';')
    tickers = list(base_tickers["Código"])
    tickers = [item + ".SA" for item in tickers]
    return tickers

acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)    

# Criar a interface do streamlit
st.write(""" # App preço de Ações
O gráfico abaixo representa evolução do preço das ações ao longos dos anos""")

# Prepara as visualizações
with st.sidebar:
    st.header("Filtros")
    lista_acoes = st.multiselect("Escolha as ações para visualizar", options=acoes)
    if lista_acoes:
        dados = dados[lista_acoes]
        if len(lista_acoes) == 1:
            acao_unica = lista_acoes[0]
            dados.rename(columns={acao_unica: "Close"})
    
    data_inicial = dados.index.min().to_pydatetime()
    data_final = dados.index.max().to_pydatetime()
    intervalo_data = st.slider(label="Selecione o periodo", 
                               min_value= data_inicial, 
                               max_value=data_final, 
                               value=(data_inicial, data_final),
                               step=timedelta(days=1))
    dados = dados.loc[intervalo_data[0]:intervalo_data[1]]
# Criar o grafico
st.line_chart(data=dados)

# calculo de performace
texto_perfomace_ativos = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados.rename(columns={"Close": acao_unica})
    
carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)
        
for i, acao in enumerate(lista_acoes):
    performace_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1
    performace_ativo = float(performace_ativo)
    
    carteira[i] = carteira[i] * (1+performace_ativo)
    
    if performace_ativo > 0:
        texto_perfomace_ativos = texto_perfomace_ativos + f"  \n{acao}: :green[{performace_ativo:.1%}]"
    elif performace_ativo < 0:
        texto_perfomace_ativos = texto_perfomace_ativos + f"  \n{acao}: :red[{performace_ativo:.1%}]"
    else:
        texto_perfomace_ativos = texto_perfomace_ativos + f"  \n{acao}: {performace_ativo:.1%}"

total_final_carteira = sum(carteira)
performace_carteira = total_final_carteira / total_inicial_carteira - 1
performace_carteira = float(performace_carteira)
if performace_carteira > 0:
    texto_performace_carteira = f"Performace da carteira com todos os ativos:  :green[{performace_carteira:.1%}]"
elif performace_carteira < 0:
    texto_performace_carteira = f"Performace da carteira com todos os ativos:  :red[{performace_carteira:.1%}]"
else:
    texto_performace_carteira = f"Performace da carteira com todos os ativos:  {performace_carteira:.1%}"

st.write(f""" ### Performace dos ativos
Essa foi a performace de cada ativo no periodo selecionado:
{texto_perfomace_ativos}

{texto_performace_carteira}
""")
