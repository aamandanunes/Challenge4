import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px

# Configuração da página Streamlit
st.set_page_config(layout='wide')

# Título do aplicativo
st.title('Análise de Preço do Petróleo Brent :oil_drum:')

# URL da fonte de dados
url = 'http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650971490&oper=view'

# Requisição e extração da tabela HTML
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', {'id': 'grd_DXMainTable'})
df = pd.read_html(str(table), header=0)[0]

# Renomeando colunas
df.columns = df.iloc[0]
df = df.rename(columns={df.columns[0]: 'Data', df.columns[1]: 'Preço'})

# Tratamento dos dados
df['Preço'] = df['Preço'] / 100
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df_media_ano = df.groupby(df['Data'].dt.year)['Preço'].mean().reset_index()

# Gráfico de linha da média de preço por ano
fig_media_preco_ano = px.line(df_media_ano, x='Data', y='Preço', markers=True,
                          title='Média de preço por ano', labels={'Preço': 'Média de Preço', 'Data': 'Ano'},
                          template='plotly_dark')

# Dados dos últimos 24 meses
data_atual = df['Data'].max()
ultimos_24_meses = pd.date_range(end=data_atual, periods=24, freq='M')
df_ultimos_24_meses = df[df['Data'].isin(ultimos_24_meses)]
df_ultimos_24_meses['MesAno'] = df_ultimos_24_meses['Data'].dt.to_period('M').dt.strftime('%m-%Y')
df_ultimos_24_meses['Preço'] = pd.to_numeric(df_ultimos_24_meses['Preço'], errors='coerce')
df_media_ultimos_24_meses = df_ultimos_24_meses.groupby('MesAno')['Preço'].mean().reset_index()
df_media_ultimos_24_meses['MesAno'] = pd.to_datetime(df_media_ultimos_24_meses['MesAno'], format='%m-%Y')
df_media_ultimos_24_meses = df_media_ultimos_24_meses.sort_values('MesAno')
df_media_ultimos_24_meses['MesAno'] = df_media_ultimos_24_meses['MesAno'].dt.strftime('%m-%Y')

# Gráfico de linha da média de preço nos últimos 24 meses
fig_media_ultimos_24_meses = px.line(df_media_ultimos_24_meses, x='MesAno', y='Preço', markers=True,
                                    title='Média de preço por mês dos últimos 24 Meses', labels={'Preço': 'Média de Preço', 'MesAno': 'Mês-Ano'}, 
                                    template='plotly_dark')

# Visualização no Streamlit em abas
aba1, aba2, aba3 = st.tabs(['Valores Petróleo', 'Previsão de Valores', 'Dados'])
with aba1:
    st.plotly_chart(fig_media_preco_ano, use_container_width=True)
    st.plotly_chart(fig_media_ultimos_24_meses, use_container_width=True)
with aba2:
    st.write("**Machine Learning**")
with aba3:
    st.dataframe(df)
