import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

    # Interligar as bases de dados nas colunas de país e região
    dados_combinados = pd.merge(full_grouped, worldometer_data, on="Country/Region", how="inner")

    # Selecionar colunas numéricas para análise
    numeric_columns = dados_combinados.select_dtypes(include='number').columns

    # Seletor de datas
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Selecione a data de início", value=dados_combinados['Date'].min())
    with col2:
        data_fim = st.date_input("Selecione a data de fim", value=dados_combinados['Date'].max())

    # Filtragem dos dados
    dados_filtrados = dados_combinados[(dados_combinados['Date'] >= pd.to_datetime(data_inicio)) & 
                                       (dados_combinados['Date'] <= pd.to_datetime(data_fim))]

    # Filtro por país
    st.markdown("<h4 style='color:#67ba61;'>Filtrar por país:</h4>", unsafe_allow_html=True)
    pais_opcoes = ["Todos os Países"] + sorted(dados_combinados['Country/Region'].unique())
    pais_selecionado = st.selectbox("País", options=pais_opcoes, index=0)

    # Filtrando dados com base no país selecionado
    if pais_selecionado != "Todos os Países":
        dados_filtrados = dados_filtrados[dados_filtrados['Country/Region'] == pais_selecionado]

     # Slider para escolher entre dados diários e anuais
    tipo_agrupamento = st.radio("Escolha o tipo de visualização", ['Diária', 'Anual'])

    if tipo_agrupamento == 'Anual':
        dados_filtrados['Ano'] = dados_filtrados['Date'].dt.year
        dados_agrupados = dados_filtrados.groupby(['Country/Region', 'Ano']).sum(numeric_only=True).reset_index()
        x_axis = 'Ano'
    else:
        dados_agrupados = dados_filtrados
        x_axis = 'Date'

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

    # Gráfico de barras empilhadas: Casos Confirmados, Mortes e Recuperações
    st.markdown("<h4 style='color:#67ba61;'>Casos Confirmados, Mortes e Recuperações por País</h4>", unsafe_allow_html=True)
    fig_barras_empilhadas = go.Figure(data=[
        go.Bar(
            name='Casos Confirmados',
            x=dados_filtrados['Country/Region'],
            y=dados_filtrados['Confirmed'],
            marker_color='#a8e6a3'
        ),
        go.Bar(
            name='Mortes',
            x=dados_filtrados['Country/Region'],
            y=dados_filtrados['Deaths'],
            marker_color='#d9534f'
        ),
        go.Bar(
            name='Recuperados',
            x=dados_filtrados['Country/Region'],
            y=dados_filtrados['Recovered'],
            marker_color='#5bc0de'
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
    st.plotly_chart(fig_barras_empilhadas, use_container_width=True)

     # Filtrar os dados de worldometer_data com base no país selecionado
    if pais_selecionado != "Todos os Países":
        dados_filtrados = worldometer_data[worldometer_data['Country/Region'] == pais_selecionado]
    else:
        dados_filtrados = worldometer_data

    # Calcular a soma da população e dos testes para o país selecionado
    total_populacao = dados_filtrados['Population'].sum()
    total_testes = dados_filtrados['TotalTests'].sum()

    # Criar um DataFrame para o gráfico de pizza
    dados_pizza = pd.DataFrame({
        'Categoria': ['População Total', 'Total de Testes'],
        'Quantidade': [total_populacao, total_testes]
    })

    # Gráfico de Pizza
    fig_pizza = px.pie(
        dados_pizza,
        names='Categoria',
        values='Quantidade',
        title=f'Distribuição da População e Testes Realizados em {pais_selecionado}',
        color_discrete_sequence=['#67ba61', '#d9534f']
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig_pizza, use_container_width=True)

    # Gráfico de Casos Confirmados Cumulativos ao Longo do Tempo
    st.markdown("<h4 style='color:#67ba61; text-align:center;'>Casos Confirmados Cumulativos ao Longo do Tempo (Filtrado)</h4>", unsafe_allow_html=True)

    # Filtrar os dados de full_grouped com base no país selecionado
    if pais_selecionado != "Todos os Países":
        dados_filtrados = full_grouped[full_grouped['Country/Region'] == pais_selecionado]
    else:
        dados_filtrados = full_grouped

    # Verifica se a coluna 'Date' está presente
    if 'Date' in dados_filtrados.columns:
        casos_cumulativos = dados_filtrados.groupby('Date')['Confirmed'].sum().reset_index()

        # Criar o gráfico de linha
        fig_cumulativo_filtrado = px.line(
            casos_cumulativos,
            x='Date',
            y='Confirmed',
            labels={'Confirmed': 'Casos Confirmados', 'Date': 'Data'},
            color_discrete_sequence=['#67ba61']
        )
        
        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig_cumulativo_filtrado, use_container_width=True)
    else:
        st.error("A coluna 'Date' não foi encontrada nos dados filtrados. Verifique se os dados foram carregados corretamente.")

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

