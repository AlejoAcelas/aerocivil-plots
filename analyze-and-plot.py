# %%

import pandas as pd
import plotly.express as px

filename = 'data/vuelos-enero-2023.xlsx'
sheet_name_international_flights = 'CUADRO 5'
sheet_name_national_flights = 'CUADRO 6'
num_rows_header = 7
num_rows_footer = 1 # Aggregates row
relevant_columns = 'A:F, I, K, M' # Airport and passenger info from 2022

column_names = [
    'origin_code',
    'origin_city',
    'origin_state',
    'destination_code',
    'destination_city',
    'destination_state',
    'seats_offered',
    'passengers',
    'occupancy_rate',
]

# %%

national_flights = pd.read_excel(
    filename,
    sheet_name=sheet_name_national_flights,
    skiprows=num_rows_header,
    usecols=relevant_columns,
    names=column_names,
    skipfooter=num_rows_footer,
)

international_flights = pd.read_excel(
    filename,
    sheet_name=sheet_name_international_flights,
    skiprows=num_rows_header,
    usecols=relevant_columns,
    names=column_names,
    skipfooter=num_rows_footer,
)

flights = pd.concat([national_flights, international_flights])

# %%

outgoing_flights_by_airport = (
    flights
    .query("origin_state == 'COLOMBIA'")
    .groupby('origin_code')
    [['passengers', 'seats_offered']]
    .sum()
    .astype(pd.Int64Dtype())
    .reset_index()
    .rename(columns={'origin_code': 'airport_code'})
)
incoming_flights_by_airport = (
    flights
    .query("destination_state == 'COLOMBIA'")
    .groupby('destination_code')
    [['passengers', 'seats_offered']]
    .sum()
    .astype(pd.Int64Dtype())
    .reset_index()
    .rename(columns={'destination_code': 'airport_code'})
)

flights_by_airport = (
    outgoing_flights_by_airport.merge(
        incoming_flights_by_airport,
        on='airport_code',
        how='outer',
        suffixes=('_outgoing', '_incoming')
    )
    .fillna(0)
)

top_airports = (
    flights_by_airport
    .assign(
        total_flights=lambda x: x['passengers_outgoing'] + x['passengers_incoming'],
        total_seats=lambda x: x['seats_offered_outgoing'] + x['seats_offered_incoming'],
        total_occupancy=lambda x: x['total_flights'] / x['total_seats']
    )
    .nlargest(12, 'total_flights')
    .reset_index(drop=True)
)

top_airports

# %%

top_airports_to_plot = top_airports.rename(
    {
        'airport_code': 'Código de Aeropuerto',
        'passengers_outgoing': 'Origen',
        'passengers_incoming': 'Destino',
        'total_flights': 'Pasajeros Servidos en 2022',
        'total_seats': 'Sillas',
        'total_occupancy': 'Tasa de Ocupación',
    },
    axis=1,
)

fig_bars = px.histogram(
    top_airports_to_plot,
    x='Código de Aeropuerto',
    y=['Origen', 'Destino'],
    barmode='stack',
    title='Top 12 Aeropuertos por Pasajeros Servidos en 2022',
    labels={
        'airport_code': 'Código de Aeropuerto',
        'value': 'Pasajeros',
        'variable': 'El Aeropuerto es:',
    },
)

fig_bars.show()
fig_bars.write_image('media/top_airports.png', scale=5)

fig_scatter = px.scatter(
    top_airports_to_plot,
    x='Pasajeros Servidos en 2022',
    y='Tasa de Ocupación',
    text='Código de Aeropuerto',
    title='Tasa de Ocupación vs Pasajeros Servidos en 2022',
    log_x=True,
)

fig_scatter.update_traces(
    textposition='top left',
    textfont=dict(size=12, color='black', family='Arial',),
)

fig_scatter.show()
fig_scatter.write_image('media/occupancy_vs_passengers.png', scale=5)

# %%
