import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Título do Dashboard
st.markdown("<h1 style='color:#67ba61; text-align:center;'>DASHBOARD COVID-19</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#67ba61; text-align:center;'>Jan 2020 - Jun 2022</h2>", unsafe_allow_html=True)

# Upload dos datasets
st.markdown("<h4 style='color:#67ba61;'>Faça upload de pelo menos dois arquivos CSV:</h4>", unsafe_allow_html=True)
uploaded_files = st.file_uploader("Selecione os arquivos (mínimo 2)", type="csv", accept_multiple_files=True)

# Verificar se pelo menos dois arquivos foram carregados
if len(uploaded_files) < 2:
    st.warning("Por favor, carregue pelo menos dois arquivos CSV para continuar.")
else:
    # Carregar os dados
    full_grouped = pd.read_csv(uploaded_files[0])
    worldometer_data = pd.read_csv(uploaded_files[1])

    # Conversão da coluna de data
    full_grouped['Date'] = pd.to_datetime(full_grouped['Date'])

    # Selecionar colunas numéricas para análise
    numeric_columns = full_grouped.select_dtypes(include='number').columns

    # Seletor de datas
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Selecione a data de início", value=full_grouped['Date'].min())
    with col2:
        data_fim = st.date_input("Selecione a data de fim", value=full_grouped['Date'].max())

    # Filtragem dos dados
    dados_filtrados = full_grouped[(full_grouped['Date'] >= pd.to_datetime(data_inicio)) & 
                                   (full_grouped['Date'] <= pd.to_datetime(data_fim))]

    # Filtro por país
    st.markdown("<h4 style='color:#67ba61;'>Filtrar por país:</h4>", unsafe_allow_html=True)
    pais_opcoes = ["Todos os Países"] + sorted(full_grouped['Country/Region'].unique())
    pais_selecionado = st.selectbox("País", options=pais_opcoes, index=0)

    # Filtrando dados com base no país selecionado
    if pais_selecionado != "Todos os Países":
        dados_filtrados = dados_filtrados[dados_filtrados['Country/Region'] == pais_selecionado]

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        casos_confirmados_filtrados = dados_filtrados['Confirmed'].sum()
        st.metric(label="Casos Confirmados", value=f"{casos_confirmados_filtrados:,}")
    with col2:
        mortes_filtradas = dados_filtrados['Deaths'].sum()
        st.metric(label="Mortes", value=f"{mortes_filtradas:,}")
    with col3:
        recuperados_filtrados = dados_filtrados['Recovered'].sum()
        st.metric(label="Recuperados", value=f"{recuperados_filtrados:,}")
    with col4:
        taxa_mortalidade_filtrada = mortes_filtradas / casos_confirmados_filtrados * 100 if casos_confirmados_filtrados > 0 else 0
        st.metric(label="Taxa de Mortalidade", value=f"{taxa_mortalidade_filtrada:.2f}%")

    # Gráfico de Pizza
    st.markdown("<h4 style='color:#67ba61;'>Distribuição de Casos Confirmados, Mortes e Recuperações</h4>", unsafe_allow_html=True)
    if pais_selecionado == "Todos os Países":
        dados_pizza = dados_filtrados.groupby('Country/Region')[['Confirmed', 'Deaths', 'Recovered']].sum().reset_index()
        labels_pizza = dados_pizza['Country/Region'].tolist()
        values_pizza = dados_pizza['Confirmed'].tolist()
    else:
        if not dados_filtrados.empty:
            dados_pizza = dados_filtrados.iloc[0]
            labels_pizza = ['Casos Confirmados', 'Mortes', 'Recuperações']
            values_pizza = [dados_pizza['Confirmed'], dados_pizza['Deaths'], dados_pizza['Recovered']]
        else:
            labels_pizza = ['Sem Dados']
            values_pizza = [1]

    # Criar o gráfico de pizza
    fig_pizza = px.pie(
        names=labels_pizza,
        values=values_pizza,
        title=f'Distribuição de Casos em {pais_selecionado}',
        color_discrete_sequence=['#67ba61', '#d9534f', '#5bc0de']
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

    # Gráfico de barras: Top 5 Países com mais casos confirmados
    st.markdown("<h4 style='color:#67ba61; text-align:center;'>Top 5 Países com Maior Prevalência de COVID-19 (Filtrado)</h4>", unsafe_allow_html=True)
    casos_por_pais_filtrados = dados_filtrados.groupby('Country/Region')[numeric_columns].sum().reset_index()
    top_paises_filtrados = casos_por_pais_filtrados.nlargest(5, 'Confirmed')
    fig_top_paises_filtrados = px.bar(top_paises_filtrados, 
                                      x='Country/Region', 
                                      y='Confirmed', 
                                      labels={'Confirmed': 'Casos Confirmados', 'Country/Region': 'País'}, 
                                      color_discrete_sequence=['#67ba61'])
    st.plotly_chart(fig_top_paises_filtrados, use_container_width=True)

    # Agrupar dados para gráfico de barras empilhadas
    casos_por_pais = dados_filtrados.groupby('Country/Region')['Confirmed'].sum().reset_index()
    mortes_por_pais = dados_filtrados.groupby('Country/Region')['Deaths'].sum().reset_index()
    recuperados_por_pais = dados_filtrados.groupby('Country/Region')['Recovered'].sum().reset_index()
    mortes_por_pais['Taxa de Mortalidade (%)'] = (mortes_por_pais['Deaths'] / casos_por_pais['Confirmed'] * 100).fillna(0)

    # Combinar os dados em um DataFrame único para o gráfico
    dados_grafico = pd.merge(casos_por_pais, mortes_por_pais, on='Country/Region')
    dados_grafico = pd.merge(dados_grafico, recuperados_por_pais, on='Country/Region')
    dados_grafico = dados_grafico.rename(columns={'Confirmed': 'Casos Confirmados', 'Taxa de Mortalidade (%)': 'Taxa de Mortalidade (%)', 'Recovered': 'Recuperados'})

    # Criar o gráfico de barras empilhadas
    fig_barras_empilhadas = go.Figure(data=[
        go.Bar(
            name='Casos Confirmados',
            x=dados_grafico['Country/Region'],
            y=dados_grafico['Casos Confirmados'],
            marker_color='#a8e6a3',
            text=dados_grafico['Casos Confirmados'],
            textposition='inside',
            hovertemplate='<b>País:</b> %{x}<br>' +
                          '<b>Casos Confirmados:</b> %{y}<br>' +
                          '<b>Mortes:</b> %{customdata[0]}<br>' +
                          '<b>Recuperados:</b> %{customdata[1]}<br>' +
                          '<extra></extra>',
            customdata=dados_grafico[['Deaths', 'Recuperados']].values,
            width=5
        ),
        go.Bar(
            name='Mortes',
            x=dados_grafico['Country/Region'],
            y=dados_grafico['Deaths'],
            marker_color='#d9534f',
            text=dados_grafico['Deaths'],
            textposition='inside',
            hovertemplate='<b>País:</b> %{x}<br>' +
                          '<b>Mortes:</b> %{y}<br>' +
                          '<extra></extra>',
            width=5
        ),
        go.Bar(
            name='Recuperados',
            x=dados_grafico['Country/Region'],
            y=dados_grafico['Recuperados'],
            marker_color='#5bc0de',
            text=dados_grafico['Recuperados'],
            textposition='inside',
            hovertemplate='<b>País:</b> %{x}<br>' +
                          '<b>Recuperados:</b> %{y}<br>' +
                          '<extra></extra>',
            width=5
        )
    ])

    fig_barras_empilhadas.update_layout(
        title='Casos Confirmados, Mortes e Recuperações por País',
        xaxis_title='País',
        yaxis_title='Quantidade',
        barmode='stack',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        legend=dict(title='Métrica')
    )

    # Exibir o gráfico de barras empilhadas
    st.plotly_chart(fig_barras_empilhadas, use_container_width=True)

    # Gráfico de Casos Confirmados Cumulativos ao Longo do Tempo
    st.markdown("<h4 style='color:#67ba61; text-align:center;'>Casos Confirmados Cumulativos ao Longo do Tempo (Filtrado)</h4>", unsafe_allow_html=True)
    casos_cumulativos = dados_filtrados.groupby('Date')['Confirmed'].sum().reset_index()
    fig_cumulativo_filtrado = px.line(casos_cumulativos, 
                                      x='Date', 
                                      y='Confirmed', 
                                      labels={'Confirmed': 'Casos Confirmados', 'Date': 'Data'},
                                      color_discrete_sequence=['#67ba61'])
    st.plotly_chart(fig_cumulativo_filtrado)

    # Mapa de Casos de COVID-19 por País
    st.markdown("<h4 style='color:#67ba61; text-align:center;'>Casos de COVID-19 por País (Filtrado)</h4>", unsafe_allow_html=True)
    fig_mapa_filtrado = px.scatter_geo(
        dados_filtrados, 
        locations="Country/Region", 
        locationmode="country names", 
        size="Confirmed",
        hover_name="Country/Region", 
        color_discrete_sequence=["#67ba61"],
        labels={'Confirmed': 'Casos Confirmados'}
    )
    fig_mapa_filtrado.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='natural earth',
            bgcolor='black'
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_mapa_filtrado, use_container_width=True)

    st.markdown("<p style='color:#67ba61; text-align:center;'>Dashboard de COVID-19 gerado com base no intervalo de datas e país filtrados.</p>", unsafe_allow_html=True)
