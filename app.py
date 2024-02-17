import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as plt
import pydeck as pdk

lat_lon_df = pd.read_csv("lat_lon.csv")
df = pd.read_csv("crop_production.csv")
df = df[df["State_Name"]=="Maharashtra"]
df = pd.merge(df, lat_lon_df, on="District_Name")

# Streamlit UI
st.title('Crop Analysis')

# Selectors for crop_year, crop, and season
crop_year = st.selectbox('Select Crop Year:', df['Crop_Year'].unique())
crop = st.selectbox('Select Crop:', df['Crop'].unique())
season = st.selectbox('Select Season:', df['Season'].unique())

# Filter dataframe based on user selections
filtered_df = df[(df['Crop_Year'] == crop_year) & (df['Crop'] == crop) & (df['Season'] == season)]

# Pydeck map visualization
view_state = pdk.ViewState(latitude=filtered_df['lat'].mean(), longitude=filtered_df['lon'].mean(), zoom=5, pitch=50)

area_layer = pdk.Layer(
    'ScatterplotLayer',
    data=filtered_df,
    get_position=['lon', 'lat'],
    get_radius='Area * 10',  
    get_fill_color=[0, 0, 255],
    pickable=True,
    auto_highlight=True
)

production_layer = pdk.Layer(
    'ColumnLayer',
    data=filtered_df,
    get_position=['lon', 'lat', 'Area'],  
    get_elevation='Production * 10',  
    get_fill_color=[255, 0, 0, 140], 
    pickable=True,
    auto_highlight=True,
)

# Render pydeck chart
st.pydeck_chart(pdk.Deck(layers=[area_layer, production_layer], initial_view_state=view_state))