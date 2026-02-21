import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go

# Load geospatial data
geo_data = gpd.read_file('final_data.geojson')
geo_data = geo_data.set_index('kecamatan')
# Re-project to a projected CRS
geo_data_projected = geo_data.to_crs(epsg=3857)

# Calculate centroids in the projected CRS
geo_data['centroid'] = geo_data_projected.geometry.centroid

# Optionally, convert centroids back to the original geographic CRS
geo_data['centroid'] = geo_data['centroid'].to_crs(geo_data.crs)

# Extract latitude and longitude for map centering
center_lat = geo_data['centroid'].y.mean()
center_lon = geo_data['centroid'].x.mean()

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    # Title
    html.H1("Dashboard Kondisi Kelas di Kabupaten Karawang",
            style={'text-align': 'center', 'font-family': 'Arial, sans-serif'}),

    # Filters
    html.Div([
        html.Div([
            html.Label("Pilih Indikator:", style={'font-family': 'Arial, sans-serif'}),
            dcc.Dropdown(
                id='filter-indikator',
                options=[
                    {'label': 'Indeks Kerusakan', 'value': 'indeks_kerusakan'},
                    {'label': 'Persentase Perbaikan', 'value': 'persentase_perbaikan'},
                    {'label': 'Jumlah Siswa + Guru', 'value': 'jumlah_siswa_guru'}
                ],
                value='indeks_kerusakan',
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Pilih Tingkat:", style={'font-family': 'Arial, sans-serif'}),
            dcc.Dropdown(
                id='filter-tingkat',
                options=[
                    {'label': 'SD', 'value': 'SD'},
                    {'label': 'SMP', 'value': 'SMP'},
                    {'label': 'Semua Tingkat', 'value': 'all'}
                ],
                value='all',
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Pilih Tahun:", style={'font-family': 'Arial, sans-serif'}),
            dcc.Dropdown(
                id='filter-tahun',
                options=[{'label': tahun, 'value': tahun} for tahun in geo_data['tahun'].unique()],
                value=geo_data['tahun'].unique()[1],
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'margin-bottom': '20px'}),

    # Remaining elements
    html.Div([
        # Geospatial visualization (Map)
        html.Div([
            dcc.Graph(
                id='map',
                figure=px.choropleth_mapbox(
                    geo_data,
                    geojson=geo_data.geometry,
                    locations=geo_data.index,
                    color="indeks_kerusakan",
                    mapbox_style="carto-positron",
                    zoom=9,
                    center={"lat": center_lat, "lon": center_lon},
                    color_continuous_scale="reds",
                    title="Peta Geospasial"
                ),
                style={'height': '650px'}
            ),
            # Add descriptive text
            html.P(
                "Pilih Kecamatan pada peta untuk informasi secara detail.",
                style={'text-align': 'center',
                       'font-family': 'Arial, sans-serif',
                       'font-size': '14px',
                       'color': '#555'}
            ),
        ], style={'width': '55%', 'display': 'inline-block', 'padding': '10px'}),

        # Additional visualizations
        html.Div([
            html.Div([
                html.Div(id='selected-kecamatan',
                         style={'text-align': 'center', 'margin-top': '10px', 'font-family': 'Arial, sans-serif', 'font-weight': 'bold', 'font-size':'20px'}),
                html.Button('Reset Kecamatan', id='reset-kecamatan', n_clicks=0,
                            style={'margin-top': '10px', 'font-family': 'Arial, sans-serif'}),
            ]),
            html.Div([
                html.Div([
                    html.H3("Indeks Kerusakan", style={'font-family': 'Arial, sans-serif','font-size':'98%'}),
                    html.P(id='kerusakan-card', style={'font-family': 'Arial, sans-serif'})
                ], style={'width': '45%', 'display': 'inline-block', 'text-align': 'center'}),
                html.Div([
                    html.H3("Persentase Perbaikan", style={'font-family': 'Arial, sans-serif','font-size':'98%'}),
                    html.P(id='perbaikan-card', style={'font-family': 'Arial, sans-serif'})
                ], style={'width': '45%', 'display': 'inline-block', 'text-align': 'center'}),
                html.Div([
                    html.H3("Jumlah Siswa", style={'font-family': 'Arial, sans-serif','font-size':'98%'}),
                    html.P(id='siswa-card', style={'font-family': 'Arial, sans-serif'})
                ], style={'width': '45%', 'display': 'inline-block', 'text-align': 'center'}),
                html.Div([
                    html.H3("Jumlah Guru", style={'font-family': 'Arial, sans-serif','font-size':'98%'}),
                    html.P(id='guru-card', style={'font-family': 'Arial, sans-serif'})
                ], style={'width': '45%', 'display': 'inline-block', 'text-align': 'center'}),
            ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between',
                      'margin-top': '20px'}),
            dcc.Graph(id='pie-chart'),
        ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px',
                  'vertical-align': 'top', 'flex-direction': 'column'}),
    ], style={'display': 'flex', 'flex-wrap': 'nowrap', 'justify-content': 'space-between'}),

    # Bottom charts
    html.Div([
        dcc.Graph(id='bar-chart', style={'width': '45%'}),
        dcc.Graph(id='barplot-chart', style={'width': '45%'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between',
              'margin-top': '20px', 'width': '100%'})
], style={'font-family': 'Arial, sans-serif'})  # Apply global font style


# Callbacks for interactivity
@app.callback(
    [
        Output('map', 'figure'),
        Output('selected-kecamatan', 'children'),
        Output('kerusakan-card', 'children'),
        Output('perbaikan-card', 'children'),
        Output('siswa-card', 'children'),
        Output('guru-card', 'children'),
        Output('pie-chart', 'figure'),
        Output('bar-chart', 'figure'),
        Output('barplot-chart', 'figure')# Tambahkan bar chart
    ],
    [Input('filter-indikator', 'value'),
     Input('filter-tingkat', 'value'),
     Input('filter-tahun', 'value'),
     Input('map', 'clickData'),
     Input('reset-kecamatan', 'n_clicks')]
)
def update_dashboard(indikator, tingkat, tahun, clickData, reset_clicks):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Filter data based on the selected indikator
    filtered_data = geo_data.copy()

    # Apply tingkat filter
    if tingkat != 'all':
        filtered_data = filtered_data[filtered_data['tingkat'] == tingkat]
    # Filter untuk tahun 2020-2021
    year_filtered_data = filtered_data[(filtered_data['tahun'] >= 2020) & (filtered_data['tahun'] <= 2021)]
    # Apply year filter only for "Indeks Kerusakan"
    if indikator == 'indeks_kerusakan':
        filtered_data = filtered_data[filtered_data['tahun'] == tahun]
        filtered_data['rata_kerusakan'] = filtered_data.groupby(filtered_data.index)['indeks_kerusakan'].transform('mean')
        color_column = 'rata_kerusakan'
        top = 'rata_kerusakan'
        color_scale = 'reds'
        titles= 'Indeks Kerusakan'
    elif indikator == 'persentase_perbaikan':
        filtered_data = filtered_data[filtered_data['tahun'] == tahun]
        filtered_data['rata_perbaikan'] = filtered_data.groupby(filtered_data.index)['persentase_perbaikan'].transform('mean')
        color_column = 'rata_perbaikan'
        top = 'rata_perbaikan'
        color_scale = 'blues'
        titles = 'Persentase Perbaikan'
    elif indikator == 'jumlah_siswa_guru':
        filtered_data = filtered_data[filtered_data['tahun'] == tahun]
        filtered_data['jumlah_siswa_guru'] = filtered_data['jumlah_siswa'] + filtered_data['jumlah_guru']
        filtered_data['jumlah'] = filtered_data.groupby(filtered_data.index)['jumlah_siswa_guru'].transform('sum')
        color_column = 'jumlah'
        top = filtered_data['rata_kerusakan'] = filtered_data.groupby(filtered_data.index)['indeks_kerusakan'].transform('mean')
        titles = 'Indeks Kerusakan'
        color_scale = 'greens'

    # Update map
    map_figure = px.choropleth_mapbox(
        filtered_data,
        geojson=filtered_data.geometry,
        locations=filtered_data.index,
        color=color_column,
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": center_lat, "lon": center_lon},
        color_continuous_scale=color_scale,
        title=f"Peta Geospasial - {indikator.replace('_', ' ').title()} ({tingkat if tingkat != 'all' else 'Semua Tingkat'})"
    )

    # Default values
    if not clickData or triggered_id == 'reset-kecamatan':
        selected_kecamatan = "Kondisi Keseluruhan"
        kerusakan = f"{filtered_data['indeks_kerusakan'].mean():.2f}"
        perbaikan = f"{filtered_data['persentase_perbaikan'].mean():.2f}%"
        siswa = filtered_data['jumlah_siswa'].sum()
        guru = filtered_data['jumlah_guru'].sum()

        # Pie chart
        pie_data = pd.DataFrame({
            'Condition': ['Baik', 'Rusak Ringan/Sedang', 'Rusak Berat'],
            'Count': [
                filtered_data['baik'].sum(),
                filtered_data['rusak_ringan_sedang'].sum(),
                filtered_data['rusak_berat'].sum()
            ]
        })
        pie_chart = px.pie(
            pie_data,
            names='Condition',
            values='Count',
            title="Distribusi Kondisi Kelas Keseluruhan",
            color='Condition',
            color_discrete_map={
                'Baik': '#28a745',
                'Rusak Ringan/Sedang': '#ffc107',
                'Rusak Berat': '#dc3545'
            }
        )

        # Bar chart (using the approach from your provided example)
        kondisi_perbandingan = {
            "Tahun": [2020, 2020, 2020, 2021, 2021, 2021],
            "Kategori": ["Baik", "Rusak Ringan/Sedang", "Rusak Berat"] * 2,
            "Jumlah": [
                year_filtered_data[year_filtered_data['tahun'] == 2020]['baik'].sum(),
                year_filtered_data[year_filtered_data['tahun'] == 2020]['rusak_ringan_sedang'].sum(),
                year_filtered_data[year_filtered_data['tahun'] == 2020]['rusak_berat'].sum(),
                year_filtered_data[year_filtered_data['tahun'] == 2021]['baik'].sum(),
                year_filtered_data[year_filtered_data['tahun'] == 2021]['rusak_ringan_sedang'].sum(),
                year_filtered_data[year_filtered_data['tahun'] == 2021]['rusak_berat'].sum()
            ]
        }

        df_kondisi = pd.DataFrame(kondisi_perbandingan)

        # Pisahkan data berdasarkan tahun
        data_2020 = df_kondisi[df_kondisi['Tahun'] == 2020]
        data_2021 = df_kondisi[df_kondisi['Tahun'] == 2021]

        # Buat bar chart dengan go.Bar
        bar_chart = go.Figure()

        # Tambahkan trace untuk tahun 2020
        bar_chart.add_trace(go.Bar(
            x=data_2020['Kategori'],
            y=data_2020['Jumlah'],
            name='2020'
        ))

        # Tambahkan trace untuk tahun 2021
        bar_chart.add_trace(go.Bar(
            x=data_2021['Kategori'],
            y=data_2021['Jumlah'],
            name='2021'
        ))

        # Update layout dengan barmode 'group'
        bar_chart.update_layout(
            barmode='group',
            title=f'Perbandingan Kondisi Kelas (2020-2021)',
            xaxis_title='Kondisi Kelas',
            yaxis_title='Jumlah Kelas'
        )

        #barplot(scatterplot)
        top_5_siswa = filtered_data.nlargest(5, 'jumlah_siswa')
        barplot_chart = px.scatter(
            top_5_siswa,
            x='jumlah_siswa',
            y=top,
            text=top_5_siswa.index,
            title=f'Scatter Plot: Jumlah Siswa vs. {titles} (5 Kecamatan Teratas)',
            labels={'jumlah_siswa': 'Jumlah Siswa', 'indeks_kerusakan': 'Indeks Kerusakan',
                    'persentase_perbaikan': 'Persentase Perbaikan'}
        )
        barplot_chart.update_layout(xaxis_title="Jumlah Siswa", yaxis_title=titles)

    else:
        kecamatan = clickData['points'][0]['location']
        year_selected_row = year_filtered_data.loc[kecamatan]
        selected_row = filtered_data.loc[kecamatan]
        selected_kecamatan = f"Kecamatan: {kecamatan}"
        kerusakan = f"{selected_row['indeks_kerusakan'].mean():.2f}"
        perbaikan = f"{selected_row['persentase_perbaikan'].mean():.2f}%"
        siswa = selected_row['jumlah_siswa'].sum()
        guru = selected_row['jumlah_guru'].sum()

        pie_data = pd.DataFrame({
            'Condition': ['Baik', 'Rusak Ringan/Sedang', 'Rusak Berat'],
            'Count': [selected_row['baik'].sum(), selected_row['rusak_ringan_sedang'].sum(), selected_row['rusak_berat'].sum()]
        })
        pie_chart = px.pie(
            pie_data,
            names='Condition',
            values='Count',
            title=f"Kondisi Kelas di {kecamatan}",
            color='Condition',
            color_discrete_map={
                'Baik': '#28a745',
                'Rusak Ringan/Sedang': '#ffc107',
                'Rusak Berat': '#dc3545'
            }
        )

        # Bar chart (using the approach from your provided example)
        kondisi_perbandingan = {
            "Tahun": [2020, 2020, 2020, 2021, 2021, 2021],
            "Kategori": ["Baik", "Rusak Ringan/Sedang", "Rusak Berat"] * 2,
            "Jumlah": [
                year_selected_row[year_selected_row['tahun'] == 2020]['baik'].sum(),
                year_selected_row[year_selected_row['tahun'] == 2020]['rusak_ringan_sedang'].sum(),
                year_selected_row[year_selected_row['tahun'] == 2020]['rusak_berat'].sum(),
                year_selected_row[year_selected_row['tahun'] == 2021]['baik'].sum(),
                year_selected_row[year_selected_row['tahun'] == 2021]['rusak_ringan_sedang'].sum(),
                year_selected_row[year_selected_row['tahun'] == 2021]['rusak_berat'].sum()
            ]
        }

        df_kondisi = pd.DataFrame(kondisi_perbandingan)

        # Pisahkan data berdasarkan tahun
        data_2020 = df_kondisi[df_kondisi['Tahun'] == 2020]
        data_2021 = df_kondisi[df_kondisi['Tahun'] == 2021]

        # Buat bar chart
        bar_chart = go.Figure()

        # Tambahkan trace untuk tahun 2020
        bar_chart.add_trace(go.Bar(
            x=data_2020['Kategori'],
            y=data_2020['Jumlah'],
            name='2020'
        ))

        # Tambahkan trace untuk tahun 2021
        bar_chart.add_trace(go.Bar(
            x=data_2021['Kategori'],
            y=data_2021['Jumlah'],
            name='2021'
        ))

        # Update layout
        bar_chart.update_layout(
            barmode='group',
            title=f"Perbandingan Kondisi Kelas di {kecamatan} (2020-2021)",
            xaxis_title='Kondisi Kelas',
            yaxis_title='Jumlah Kelas'
        )

        # Cari tetangga dengan memastikan penyelarasan indeks secara eksplisit
        # Mengambil baris pertama dari selected_row
        if tingkat == 'all':
            selected_row_first = selected_row.iloc[0]
            neighbors = geo_data[geo_data.geometry.touches(selected_row_first.geometry)]
        else:
            neighbors = geo_data[geo_data.geometry.touches(selected_row.geometry)]

        if tingkat != 'all':
            neighbors = neighbors[neighbors['tingkat'] == tingkat]

        # Pilih data berdasarkan indikator
        if indikator == 'indeks_kerusakan':
            neighbor_data = neighbors[neighbors['tahun'] == tahun].copy()
            neighbor_data['rata_kerusakan'] = neighbor_data.groupby(neighbor_data.index)['indeks_kerusakan'].transform('mean')
            # Menghapus duplikat berdasarkan index (kecamatan)
            neighbor_data = neighbor_data.loc[~neighbor_data.index.duplicated(keep='first')]
            color_col = 'rata_kerusakan'
            color_scal = 'reds'
            title_plot = f"Indeks Kerusakan Kecamatan Tetangga {kecamatan} Tahun {tahun}"
        elif indikator == 'persentase_perbaikan':
            neighbor_data = neighbors[neighbors['tahun'] == tahun].copy()
            neighbor_data['rata_perbaikan'] = neighbor_data.groupby(neighbor_data.index)['persentase_perbaikan'].transform('mean')
            # Menghapus duplikat berdasarkan index (kecamatan)
            neighbor_data = neighbor_data.loc[~neighbor_data.index.duplicated(keep='first')]
            color_col = 'rata_perbaikan'
            color_scal = 'blues'
            title_plot = f"Persentase Perbaikan Kecamatan Tetangga {kecamatan} Tahun {tahun}"
        elif indikator == 'jumlah_siswa_guru':
            neighbor_data = neighbors[neighbors['tahun'] == tahun].copy()
            neighbor_data['jumlah_siswa_guru'] = neighbor_data['jumlah_siswa'] + neighbor_data['jumlah_guru']
            neighbor_data['jumlah'] = neighbor_data.groupby(neighbor_data.index)['jumlah_siswa_guru'].transform('sum')
            # Menghapus duplikat berdasarkan index (kecamatan)
            neighbor_data = neighbor_data.loc[~neighbor_data.index.duplicated(keep='first')]
            color_col = 'jumlah'
            color_scal = 'greens'
            title_plot = f"Jumlah Siswa dan Guru Kecamatan Tetangga {kecamatan} Tahun {tahun}"

        # Buat bar chart
        barplot_chart = px.bar(
            neighbor_data,
            x=neighbor_data.index,
            y=color_col,
            title=title_plot,
            color=color_col,
            color_continuous_scale=color_scal
        )

    return (
        map_figure,
        selected_kecamatan,
        kerusakan,
        perbaikan,
        siswa,
        guru,
        pie_chart,
        bar_chart,
        barplot_chart
    )

if __name__ == '__main__':
    app.run_server(debug=True)


