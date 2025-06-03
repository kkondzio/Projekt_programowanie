import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Wczytanie danych shapefile
shapefile_path = "map_assets/wojewodztwa.shp"
gdf = gpd.read_file(shapefile_path)

# Filtrujemy tylko województwa (jeśli plik zawiera różne poziomy administracyjne)
# Zakładamy, że kolumna z nazwami województw to 'JPT_NAZWA_' - może się różnić w Twoich danych
if 'JPT_NAZWA_' not in gdf.columns:
    # Spróbuj znaleźć odpowiednią kolumnę z nazwami
    name_col = None
    for col in gdf.columns:
        if 'nazwa' in col.lower() or 'name' in col.lower():
            name_col = col
            break
    if name_col is None:
        name_col = gdf.columns[1]  # Domyślnie druga kolumna
    gdf = gdf.rename(columns={name_col: 'JPT_NAZWA_'})

# Tworzymie unikalnych kolorów dla każdego województwa
n_woj = len(gdf)
colors = plt.cm.get_cmap('tab20', n_woj)
gdf['color'] = [colors(i) for i in range(n_woj)]

# Funkcja do obsługi kliknięć
def on_click(event):
    if event.inaxes != ax:
        return

    # Przekształcenie współrzędnych ekranu na współrzędne danych (geograficzne)
    data_coords = ax.transData.inverted().transform((event.x, event.y))
    point = Point(data_coords)

    for idx, row in gdf.iterrows():
        if row['geometry'].contains(point):
            print(f"Kliknięto: {row['JPT_NAZWA_']}")
            break

# Rysowanie mapy
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(ax=ax, color=gdf['color'], edgecolor='black', linewidth=0.5)

# Dodanie etykiet
for idx, row in gdf.iterrows():
    centroid = row['geometry'].centroid
    ax.text(centroid.x, centroid.y, row['JPT_NAZWA_'], fontsize=8, ha='center')

# Konfiguracja wykresu
ax.set_title('Podział administracyjny Polski - województwa', fontsize=15)
ax.set_axis_off()

# Podłączenie obsługi zdarzeń
fig.canvas.mpl_connect('button_press_event', on_click)

plt.tight_layout()
plt.show()