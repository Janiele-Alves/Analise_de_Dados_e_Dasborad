import streamlit as st
import pandas as pd
import plotly.express as px

full_grouped = pd.read_csv('full_grouped.csv')
worldometer_data = pd.read_csv('worldometer_data.csv')

full_grouped['Date'] = pd.to_datetime(full_grouped['Date'])

numeric_columns = full_grouped.select_dtypes(include='number').columns
cases_by_country = full_grouped.groupby('Country/Region')[numeric_columns].sum().reset_index()

st.title("COVID-19 DASHBOARD")
st.header("Jan 2020 - June 2022")

start_date = st.date_input("Select start date", value=full_grouped['Date'].min())
end_date = st.date_input("Select end date", value=full_grouped['Date'].max())

filtered_data = full_grouped[(full_grouped['Date'] >= pd.to_datetime(start_date)) & 
                             (full_grouped['Date'] <= pd.to_datetime(end_date))]

confirmed_cases_filtered = filtered_data['Confirmed'].sum()
death_cases_filtered = filtered_data['Deaths'].sum()
mortality_rate_filtered = death_cases_filtered / confirmed_cases_filtered * 100

st.metric(label="Confirmed Cases", value=f"{confirmed_cases_filtered:,}")
st.metric(label="Death Cases", value=f"{death_cases_filtered:,}")
st.metric(label="Mortality Rate", value=f"{mortality_rate_filtered:.2f}%")

cases_by_country_filtered = filtered_data.groupby('Country/Region')[numeric_columns].sum().reset_index()
top_countries_filtered = cases_by_country_filtered.nlargest(5, 'Confirmed')
fig_top_countries_filtered = px.bar(top_countries_filtered, x='Country/Region', y='Confirmed', 
                                    title="Top 5 Countries with Highest Prevalence of COVID-19 (Filtered)", 
                                    labels={'Confirmed': 'Confirmed Cases', 'Country/Region': 'Country'})
st.plotly_chart(fig_top_countries_filtered)

cumulative_cases_filtered = filtered_data.groupby('Date')['Confirmed'].sum().cumsum().reset_index()
fig_cumulative_filtered = px.line(cumulative_cases_filtered, x='Date', y='Confirmed', 
                                  title="Cumulative Confirmed Cases (Filtered by Date)", 
                                  labels={'Confirmed': 'Confirmed Cases', 'Date': 'Date'})
st.plotly_chart(fig_cumulative_filtered)

st.markdown("<h3 style='color:#FFFFFF;text-align:center;'>COVID-19 Cases by Country (Filtered)</h3>", unsafe_allow_html=True)
fig_map_filtered = px.choropleth(cases_by_country_filtered,
                                 locations="Country/Region",
                                 locationmode="country names",
                                 color="Confirmed",
                                 hover_name="Country/Region",
                                 color_continuous_scale="Reds",
                                 title="Confirmed COVID-19 Cases by Country (Filtered)",
                                 labels={'Confirmed': 'Confirmed Cases'})


fig_map_filtered.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=False,
    ),
    coloraxis_colorbar=dict(
        title="Confirmed Cases"
    )
)


st.plotly_chart(fig_map_filtered)

st.write("Dashboard de COVID-19 gerado com base no intervalo de datas filtrado.")
