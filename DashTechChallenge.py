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
df['Preço']= pd.to_numeric(df['Preço'], errors='coerce')
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df_media_ano = df.groupby(df['Data'].dt.year)['Preço'].mean().reset_index()

# Gráfico de linha da média de preço por ano
fig_media_preco_ano = px.line(df_media_ano, x='Data', y='Preço', markers=True,
                          title='Média de preço por ano', labels={'Preço': 'Média de Preço', 'Data': 'Ano'},
                          template='plotly_dark')

# Dados dos últimos 24 meses
data_atual = df['Data'].max()
data_24_meses_atras = data_atual - pd.DateOffset(months=24)
df_ultimos_24_meses = df[(df['Data'] >= data_24_meses_atras) & (df['Data'] <= data_atual)]
df_ultimos_24_meses['MesAno'] = df_ultimos_24_meses['Data'].dt.to_period('M').dt.strftime('%m-%Y')
df_media_ultimos_24_meses = df_ultimos_24_meses.groupby('MesAno')['Preço'].mean().reset_index()
df_media_ultimos_24_meses['MesAno'] = pd.to_datetime(df_media_ultimos_24_meses['MesAno'], format='%m-%Y')
df_media_ultimos_24_meses = df_media_ultimos_24_meses.sort_values('MesAno')
df_media_ultimos_24_meses['MesAno'] = df_media_ultimos_24_meses['MesAno'].dt.strftime('%m-%Y')

# Gráfico de linha da média de preço nos últimos 24 meses
fig_media_ultimos_24_meses = px.line(df_media_ultimos_24_meses, x='MesAno', y='Preço', markers=True,
                                    title='Média de preço por mês dos últimos 24 Meses', labels={'Preço': 'Média de Preço', 'MesAno': 'Mês-Ano'},
                                    template='plotly_dark')

#
# Visualização no Streamlit em abas
aba1, aba2, aba3, aba4 = st.tabs(['Valores Petróleo', 'Previsão de Valores', 'Insights', 'Dados'])
with aba1:
    st.write('''A palavra Brent designa todo o petróleo extraído no Mar do Norte e comercializado na Bolsa de Londres.''')
    st.write('''A cotação Brent é o valor de referência mundial.''')

    st.markdown('O preço do petróleo Brent pode ser influenciado por alguns fatores, como:')
    st.markdown("- Níveis de produção de petróleo bruto;")
    st.markdown("- Balanço de oferta e demanda;")
    st.markdown("- Operações de petróleo bruto no Mar do Norte;")
    st.markdown("- Questões geopolíticas no mercado internacional.")

    st.plotly_chart(fig_media_preco_ano, use_container_width=True)
    st.write('''Os choques geopolíticos podem ter impacto nos preços do petróleo através de uma atividade económica mais baixa ou de riscos mais elevados para a oferta de matérias-primas.''')
    st.markdown('- O preço do petróleo Brent aumentou na época em que a primavera Árabe começou no Egito em fevereiro de 2011, os temores sobre o fechamento do Canal de Suez e a falta de oferta disponível fizeram com que o petróleo bruto ficasse mais caro.')
    st.markdown('- No final de 2011, o governo iraniano ameaçou fechar o Estreito de Ormuz, por onde fluia cerca de 20% do petróleo mundial, aumentando o preço do petróleo.')
    st.markdown('- Em 2014, o preço do barril de petróleo Brent atingiu o valor mais baixo desde Junho de 2012, caindo abaixo dos 92 dólares. A decisão da Arábia Saudita, o maior exportador mundial, de cortar os preços fez aumentar os receios de excesso de oferta numa altura em que os fracos dados da economia mundial deixam antever uma quebra no consumo desta matéria-prima. ')
    st.markdown('- Em 2015 foi firmado um acordo com o Irã, permitindo ao país exportar mais petróleo, o que deveria ter aumentado a quantidade de petróleo bruto que entra no mercado diariamente. Como a Brent é a referência de preço do petróleo iraniano, esse desenvolvimento fez o preço do Brent cair.')
    st.markdown('- Em 2020, em virtude da pandemia da Covid-19, os preços do marcador Brent registraram o menor valor desde 2004. Em maio de 2020, durante a pandemia e o confinamento global, a previsão do preço do petróleo Brent caiu para 28 dólares por barril, uma queda de mais de 5%.')


    st.plotly_chart(fig_media_ultimos_24_meses, use_container_width=True)
    st.markdown('- Em junho de 2022, com o alívio das restrições contra a Covid-19 nas maiores cidades da China, o preço do petróleo Brent subiu para o nível mais alto dos últimos meses - período em que Xangai ficou em lockdown.')
    st.markdown('- Em setembro de 2022, a queda se deve ao temor dos investidores com o desaquecimento da economia global, principalmente da China, o que freia a demanda pela commodity. Os dados de exportações do país asiático mostraram que o crescimento das vendas foi mais impactado em agosto do que o mercado financeiro esperava. As importações, por sua vez, estagnaram. A China adotou medidas para restringir o fluxo de pessoas por causa da pandemia de covid-19.')
    st.markdown('- No final de 2023, dois principais fatores externos contribuíram para que os preços dos combustíveis tivessem uma tendência de queda no cenário internacional, segundo o superintendente de pesquisa da FGV Energia, Márcio Couto. Um deles é a conjuntura econômica, com os Estados Unidos subindo taxas de juros para conter a inflação americana por meio da desaceleração da economia. Soma-se a isso desconfianças sobre a força do crescimento da China, segunda maior economia global.  Outro elemento externo é um reflexo da guerra na Ucrânia. Como forma de pressionar a Rússia a parar o conflito, a União Europeia e o G7 (grupo dos sete países mais desenvolvidos do mundo) aplicaram embargos à compra do petróleo russo.  Com isso, a Rússia ficou com muito petróleo e derivados sobrando e está colocando esses produtos no mercado por um preço muito baixo. Você passou a ter um combustível barato.')

with aba2:
    st.write("**Machine Learning**")
with aba3:
    st.write(":bulb: **Guerras ou instabilidade política em uma parte sensível do mundo podem afertar o trabalho dos produtores de petróleo na área. Além disto, o aumento ou redução de petróleo pela OPEP pode afetar o preço.**")
    st.divider()
    st.write(":bulb: **O preço do barril pode oscilar de 50 a 100, dependendo das decisões da Arábia Saudita, na qual tem o poder de aumentar ou diminuir a produção de barris.**")
    st.divider()
    st.write(":bulb: **A volatividade no preço do petróleo em 2024 está relacionada aos riscos geopolíticos no oriente médio devido aos bombardeios nas embarcações ao longo do Mar Vermelho. Além disto, operações no campo de petróleo El Shahara, um dos maiores e mais importantes campos petrolíferos da Líbia, foram interrompidas devido aos protestos contra as exigências sociais.**")
    st.divider()
    st.write(":bulb: **Outro fator é a valorização do dólar internacionalmente, fazendo com que o preço do combustível fique encarecido pelo câmbio, o que reduz a demanda.**")


with aba4:
    st.dataframe(df)
