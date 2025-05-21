import os
import requests
import zipfile
from bs4 import BeautifulSoup
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium
import fiona

# Base folder
base_folder = r"C:\StreamlitApp"
os.makedirs(base_folder, exist_ok=True)

# Streamlit UI
st.title("South Sudan Health Facilities Map")

# Dataset info
dataset_url = "https://data.humdata.org/dataset/hotosm_ssd_health_facilities"

try:
    # Setup dataset folders
    dataset_name = dataset_url.split("/")[-1]
    dataset_folder = os.path.join(base_folder, dataset_name)
    os.makedirs(dataset_folder, exist_ok=True)

    # Scrape KML ZIP link
    response = requests.get(dataset_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    kml_link = None
    for link in soup.find_all('a', href=True):
        if ".zip" in link['href'] and "kml" in link['href'].lower():
            kml_link = link['href']
            break

    if not kml_link:
        st.error("KML ZIP file link not found!")
        st.stop()

    if not kml_link.startswith("http"):
        kml_link = "https://data.humdata.org" + kml_link

    # Download
    zip_path = os.path.join(dataset_folder, "data.zip")
    with open(zip_path, 'wb') as file:
        file.write(requests.get(kml_link).content)

    # Extract
    extract_folder = os.path.join(dataset_folder, "extracted")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Find KML file
    kml_file = None
    for file in os.listdir(extract_folder):
        if file.endswith(".kml"):
            kml_file = os.path.join(extract_folder, file)
            break

    if not kml_file:
        st.error("No KML file found!")
        st.stop()

    # List all KML layers
    layers = fiona.listlayers(kml_file)
    st.write("Available Layers:", layers)

    # Load the first non-empty layer
    gdf = None
    for layer in layers:
        temp_gdf = gpd.read_file(kml_file, driver='KML', layer=layer)
        if not temp_gdf.empty:
            gdf = temp_gdf
            break

    if gdf is None or gdf.empty:
        st.error("No valid features found in any KML layer.")
        st.stop()

    # Drop rows without geometry
    gdf = gdf.dropna(subset=["geometry"])

    # Center for map
    centroid = gdf.geometry.centroid.to_crs(epsg=4326).unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=6)

    # Add markers
    for _, row in gdf.iterrows():
        if row.geometry.geom_type == "Point":
            lon, lat = row.geometry.x, row.geometry.y
            popup = row.get('Name') or row.get('description') or "Health Facility"
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)


    st.subheader("Interactive Map")
    st_data = st_folium(m, width=700, height=500)

except Exception as e:
    st.exception(e)
