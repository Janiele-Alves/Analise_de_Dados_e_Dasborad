import streamlit as st
import pandas as pd
import plotly.express as px

full_grouped = pd.read_csv('full_grouped.csv')
worldometer_data = pd.read_csv('worldometer_data.csv')

full_grouped['Date'] = pd.to_datetime(full_grouped['Date'])

numeric_columns = full_grouped.select_dtypes(include='number').columns

cases_by_country = full_grouped.groupby('Country/Region')[numeric_columns].sum().reset_index()

st.markdown("<h1 style='color:#67ba61; text-align:center;'>DASHBOARD COVID-19</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#67ba61; text-align:center;'>Jan 2020 - Jun 2022</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    data_inicio = st.date_input("Selecione a data de início", value=full_grouped['Date'].min())
with col2:
    data_fim = st.date_input("Selecione a data de fim", value=full_grouped['Date'].max())

dados_filtrados = full_grouped[(full_grouped['Date'] >= pd.to_datetime(data_inicio)) & 
                               (full_grouped['Date'] <= pd.to_datetime(data_fim))]

st.markdown("<h4 style='color:#67ba61;'>Filtrar por país:</h4>", unsafe_allow_html=True)
pais_opcoes = ["Todos os Países"] + sorted(full_grouped['Country/Region'].unique())
pais_selecionado = st.selectbox("País", options=pais_opcoes, index=0)

if pais_selecionado != "Todos os Países":
    dados_filtrados = dados_filtrados[dados_filtrados['Country/Region'] == pais_selecionado]

col1, col2, col3 = st.columns(3)

with col1:
    casos_confirmados_filtrados = dados_filtrados['Confirmed'].sum()
    st.metric(label="Casos Confirmados", value=f"{casos_confirmados_filtrados:,}")

with col2:
    mortes_filtradas = dados_filtrados['Deaths'].sum()
    st.metric(label="Mortes", value=f"{mortes_filtradas:,}")

with col3:
    taxa_mortalidade_filtrada = mortes_filtradas / casos_confirmados_filtrados * 100 if casos_confirmados_filtrados > 0 else 0
    st.metric(label="Taxa de Mortalidade", value=f"{taxa_mortalidade_filtrada:.2f}%")

st.markdown("<h4 style='color:#67ba61; text-align:center;'>Top 5 Países com Maior Prevalência de COVID-19 (Filtrado)</h4>", unsafe_allow_html=True)
casos_por_pais_filtrados = dados_filtrados.groupby('Country/Region')[numeric_columns].sum().reset_index()
top_paises_filtrados = casos_por_pais_filtrados.nlargest(5, 'Confirmed')

fig_top_paises_filtrados = px.bar(top_paises_filtrados, 
                                  x='Country/Region', 
                                  y='Confirmed', 
                                  labels={'Confirmed': 'Casos Confirmados', 'Country/Region': 'País'}, 
                                  color='Country/Region')

st.plotly_chart(fig_top_paises_filtrados, use_container_width=True)

dados_filtrados['Mortality Rate (%)'] = (dados_filtrados['Deaths'] / dados_filtrados['Confirmed'] * 100).fillna(0)

fig = px.bar(
    dados_filtrados,
    x='Country/Region',
    y='Mortality Rate (%)', 
    color='Mortality Rate (%)',
    color_continuous_scale=['#67ba61', '#0a0a0a'],
    labels={'Country/Region': 'País', 'Mortality Rate (%)': 'Taxa de Mortalidade (%)'},
    title='Taxa de Mortalidade por País',
)


fig.update_layout(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font_color='white',
    xaxis=dict(title='Sigla do País'),
    yaxis=dict(title='Taxa de Mortalidade (%)'),
)

st.plotly_chart(fig)

st.markdown("<h4 style='color:#67ba61; text-align:center;'>Casos Confirmados Cumulativos (Filtrado por Data e País)</h4>", unsafe_allow_html=True)
casos_cumulativos_filtrados = dados_filtrados.groupby('Date')['Confirmed'].sum().cumsum().reset_index()
fig_cumulativo_filtrado = px.line(casos_cumulativos_filtrados, 
                                  x='Date', 
                                  y='Confirmed', 
                                  labels={'Confirmed': 'Casos Confirmados', 'Date': 'Data'})

st.plotly_chart(fig_cumulativo_filtrado, use_container_width=True)

st.markdown("<h4 style='color:#67ba61; text-align:center;'>Casos de COVID-19 por País (Filtrado)</h4>", unsafe_allow_html=True)
fig_mapa_filtrado = px.scatter_geo(casos_por_pais_filtrados, 
                                   locations="Country/Region", 
                                   locationmode="country names", 
                                   size="Confirmed",
                                   hover_name="Country/Region", 
                                   color_discrete_sequence=["#67ba61"],
                                   labels={'Confirmed': 'Casos Confirmados'})

fig_mapa_filtrado.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='natural earth',
        bgcolor='black',
        lataxis_range=[-60, 90],  
        lonaxis_range=[-180, 180]  
    ),
    paper_bgcolor='black',
    plot_bgcolor='black',
    coloraxis_showscale=False
)

st.plotly_chart(fig_mapa_filtrado, use_container_width=True)

st.markdown("<p style='color:#67ba61; text-align:center;'>Dashboard de COVID-19 gerado com base no intervalo de datas e país filtrados.</p>", unsafe_allow_html=True)
