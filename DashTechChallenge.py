import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import date, timedelta

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
df['Preço']= pd.to_numeric(df['Preço'], errors='coerce')
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df_media_ano = df.groupby(df['Data'].dt.year)['Preço'].mean().reset_index()

# Adicionando filtro por ano
anos = sorted(df_media_ano['Data'].unique())
ano_inicio_pr = min(anos)
ano_fim_pr = max(anos)

# Dados dos últimos 24 meses
data_atual = df['Data'].max()
data_24_meses_atras = data_atual - pd.DateOffset(months=24)
df_ultimos_24_meses = df[(df['Data'] >= data_24_meses_atras) & (df['Data'] <= data_atual)]
df_ultimos_24_meses['MesAno'] = df_ultimos_24_meses['Data'].dt.to_period('M').dt.strftime('%m-%Y')
df_media_ultimos_24_meses = df_ultimos_24_meses.groupby('MesAno')['Preço'].mean().reset_index()
df_media_ultimos_24_meses['MesAno'] = pd.to_datetime(df_media_ultimos_24_meses['MesAno'], format='%m-%Y')
df_media_ultimos_24_meses = df_media_ultimos_24_meses.sort_values('MesAno')
df_media_ultimos_24_meses['MesAno'] = df_media_ultimos_24_meses['MesAno'].dt.strftime('%m-%Y')

# Adicionando filtro por dat
datas = sorted(df_media_ultimos_24_meses['MesAno'].unique())

def chave_de_ordenacao(item):
    partes = item.split('-')
    return int(partes[1]), int(partes[0])  # Ordena primeiro pelo ano e depois pelo mês

datas = sorted(datas, key=chave_de_ordenacao)
data_inicio_pr = min(datas, key=chave_de_ordenacao)
data_fim_pr = max(datas, key=chave_de_ordenacao)

# Visualização no Streamlit em abas
aba1, aba2, aba3, aba4 = st.tabs(['Valores Petróleo', 'Previsão de Valores', 'Insights', 'Dados - IPEA'])
with aba1:
    st.write('''A palavra Brent designa todo o petróleo extraído no Mar do Norte e comercializado na Bolsa de Londres.''')
    st.write('''A cotação Brent é o valor de referência mundial.''')

    st.markdown('O preço do petróleo Brent pode ser influenciado por alguns fatores, como:')
    st.markdown("- Níveis de produção de petróleo bruto;")
    st.markdown("- Balanço de oferta e demanda;")
    st.markdown("- Operações de petróleo bruto no Mar do Norte;")
    st.markdown("- Questões geopolíticas no mercado internacional.")

    st.subheader('Média de preço por ano')
    col1, col2 = st.columns(2)
    with col1:
        ano_inicio = st.selectbox("Ano de início:", anos, index=anos.index(ano_inicio_pr))

    with col2:
        ano_fim = st.selectbox("Ano de término:", anos, index=anos.index(ano_fim_pr))

    df_media_ano_filtrado = df_media_ano[(df_media_ano['Data'] >= ano_inicio) & (df_media_ano['Data'] <= ano_fim)] 

    fig_media_preco_ano = px.line(df_media_ano_filtrado, x='Data', y='Preço', markers=True,
                          title='', labels={'Preço': 'Média de Preço', 'Data': 'Ano'},
                          template='plotly_dark')
        
    st.plotly_chart(fig_media_preco_ano, use_container_width=True)

    st.write('''Os choques geopolíticos podem ter impacto nos preços do petróleo através de uma atividade económica mais baixa ou de riscos mais elevados para a oferta de matérias-primas.''')
    st.markdown('- O preço do petróleo Brent aumentou na época em que a primavera Árabe começou no Egito em fevereiro de 2011, os temores sobre o fechamento do Canal de Suez e a falta de oferta disponível fizeram com que o petróleo bruto ficasse mais caro.')
    st.markdown('- No final de 2011, o governo iraniano ameaçou fechar o Estreito de Ormuz, por onde fluia cerca de 20% do petróleo mundial, aumentando o preço do petróleo.')
    st.markdown('- Em 2014, o preço do barril de petróleo Brent atingiu o valor mais baixo desde Junho de 2012, caindo abaixo dos 92 dólares. A decisão da Arábia Saudita, o maior exportador mundial, de cortar os preços fez aumentar os receios de excesso de oferta numa altura em que os fracos dados da economia mundial deixam antever uma quebra no consumo desta matéria-prima. ')
    st.markdown('- Em 2015 foi firmado um acordo com o Irã, permitindo ao país exportar mais petróleo, o que deveria ter aumentado a quantidade de petróleo bruto que entra no mercado diariamente. Como a Brent é a referência de preço do petróleo iraniano, esse desenvolvimento fez o preço do Brent cair.')
    st.markdown('- Em 2020, em virtude da pandemia da Covid-19, os preços do marcador Brent registraram o menor valor desde 2004. Em maio de 2020, durante a pandemia e o confinamento global, a previsão do preço do petróleo Brent caiu para 28 dólares por barril, uma queda de mais de 5%.')

    st.subheader('Média de preço por mês dos últimos 24 Meses')

    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.selectbox("Mes-Ano de início:", datas, index=datas.index(data_inicio_pr))

    with col2:
        data_fim = st.selectbox("Mes-Ano de término:", datas, index=datas.index(data_fim_pr))

    df_media_ultimos_24_meses['MesAno'] = pd.to_datetime(df_media_ultimos_24_meses['MesAno'], format='%m-%Y')

    df_media_ultimos_24_meses_filtrado = df_media_ultimos_24_meses[(df_media_ultimos_24_meses['MesAno'] >= data_inicio) & (df_media_ultimos_24_meses['MesAno'] <= data_fim)] 

    fig_media_ultimos_24_meses = px.line(df_media_ultimos_24_meses_filtrado, x='MesAno', y='Preço', markers=True,
                                    title='', labels={'Preço': 'Média de Preço', 'MesAno': 'Mês-Ano'},
                                    template='plotly_dark')

    st.plotly_chart(fig_media_ultimos_24_meses, use_container_width=True)

    st.markdown('- Em junho de 2022, com o alívio das restrições contra a Covid-19 nas maiores cidades da China, o preço do petróleo Brent subiu para o nível mais alto dos últimos meses - período em que Xangai ficou em lockdown.')
    st.markdown('- Em setembro de 2022, a queda se deve ao temor dos investidores com o desaquecimento da economia global, principalmente da China, o que freia a demanda pela commodity. Os dados de exportações do país asiático mostraram que o crescimento das vendas foi mais impactado em agosto do que o mercado financeiro esperava. As importações, por sua vez, estagnaram. A China adotou medidas para restringir o fluxo de pessoas por causa da pandemia de covid-19.')
    st.markdown('- No final de 2023, dois principais fatores externos contribuíram para que os preços dos combustíveis tivessem uma tendência de queda no cenário internacional, segundo o superintendente de pesquisa da FGV Energia, Márcio Couto. Um deles é a conjuntura econômica, com os Estados Unidos subindo taxas de juros para conter a inflação americana por meio da desaceleração da economia. Soma-se a isso desconfianças sobre a força do crescimento da China, segunda maior economia global.  Outro elemento externo é um reflexo da guerra na Ucrânia. Como forma de pressionar a Rússia a parar o conflito, a União Europeia e o G7 (grupo dos sete países mais desenvolvidos do mundo) aplicaram embargos à compra do petróleo russo.  Com isso, a Rússia ficou com muito petróleo e derivados sobrando e está colocando esses produtos no mercado por um preço muito baixo. Você passou a ter um combustível barato.')

with aba2:
    st.write('''Utilizando as técnicas de Machine Learning e adotando o período de treinamento dos últimos 90 dias da base do Ipea, foi possível realizar uma predição do preço do petróleo para os próximos 10 dias. O modelo que apresentou os melhores índices para o estudo foi o Sarima e está representado em vermelho no gráfico abaixo, onde está sendo comparado os valores dos úlimos 30 dias e a predição dos próximos 10 dias.''')
    st.write('''O modelo prevê uma constância no valor do petróleo, entretanto, vale ressaltar que fatores geopolíticos globais influenciam fortemente no preço do Brent e estes são, muitas vezes, imprevisíveis.''')
    data_final=df.reset_index().iloc[0].Data
    data_inicial=data_final - timedelta(days=90)
    treino_3meses = df.loc[(df['Data'] >= data_inicial)]
    treino_3meses = treino_3meses.set_index('Data').asfreq('D')

    model_sarimax = SARIMAX(treino_3meses['Preço'], freq='D', order=(7,1,2), seasonal_order=(0,1,1,7))
    model_fit = model_sarimax.fit()
    predict_sarimax = model_fit.predict(start=91,end=100,dynamic=True)
    predict_sarimax_new = predict_sarimax.reset_index().rename(columns={'index': 'Data', 'predicted_mean': 'Preço predição'})
    
    ultimo_mes=df.loc[(df['Data'] >= data_final - timedelta(days=30))]
    
    glue = pd.DataFrame(data=[{'Data': data_final, 'Preço predição': ultimo_mes.iloc[0]['Preço']}])

    base_predicao_mais_3_meses = pd.concat([ultimo_mes, glue, predict_sarimax_new])

    fig_previsao = px.line(base_predicao_mais_3_meses, x='Data', y=['Preço', 'Preço predição'], markers=True,
                                    title='Previsão do preço do petróleo Brent', labels={'Preço': 'Média de Preço', 'Data': 'Data'},
                                    template='plotly_dark')
    fig_previsao.update_layout(title='Previsão do preço do petróleo Brent', xaxis_title="Data", yaxis_title="Preço", legend_title="Legenda")
    st.plotly_chart(fig_previsao, use_container_width=True)

with aba3:
    st.write(":bulb: **Guerras ou instabilidade política em uma parte sensível do mundo podem afertar o trabalho dos produtores de petróleo na área. Além disto, o aumento ou redução de petróleo pela OPEP pode afetar o preço.**")
    st.divider()
    st.write(":bulb: **O preço do barril pode oscilar de 50 a 100, dependendo das decisões da Arábia Saudita, na qual tem o poder de aumentar ou diminuir a produção de barris.**")
    st.divider()
    st.write(":bulb: **A volatividade no preço do petróleo em 2024 está relacionada aos riscos geopolíticos no oriente médio devido aos bombardeios nas embarcações ao longo do Mar Vermelho. Além disto, operações no campo de petróleo El Shahara, um dos maiores e mais importantes campos petrolíferos da Líbia, foram interrompidas devido aos protestos contra as exigências sociais.**")
    st.divider()
    st.write(":bulb: **Outro fator é a valorização do dólar internacionalmente, fazendo com que o preço do combustível fique encarecido pelo câmbio, o que reduz a demanda.**")

with aba4:

    df_ordenado = df.sort_values('Data')
    ultimo_preco = df_ordenado['Preço'].iloc[-1]
    preco_medio = round(df_ordenado['Preço'].mean(), 2)
    preco_minimo = df_ordenado['Preço'].min()
    preco_maximo = df_ordenado['Preço'].max()
    anos_disponiveis = sorted(df['Data'].dt.year.unique())
    ano_inicio_padrao = min(anos_disponiveis)
    ano_fim_padrao = max(anos_disponiveis)
    
    # Dividindo a tela em duas colunas
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Último Preço Informado:", value=ultimo_preco)
        st.metric(label="Preço Médio:", value=preco_medio)
        ano_inicio = st.selectbox("Selecione o ano de início:", anos_disponiveis, index=anos_disponiveis.index(ano_inicio_padrao))

    with col2:
        st.metric(label="Preço Mínimo:", value=preco_minimo)
        st.metric(label="Preço Máximo:", value=preco_maximo)
        ano_fim = st.selectbox("Selecione o ano de término:", anos_disponiveis, index=anos_disponiveis.index(ano_fim_padrao))
        
    df_filtrado = df[(df['Data'].dt.year >= ano_inicio) & (df['Data'].dt.year <= ano_fim)]
    
    # DataFrame IPEA
    st.dataframe(df_filtrado)
    st.write('Fonte: http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650971490&oper=view')