import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as plt

# st.write('''
#          # Data Dashboard''')

lat_lon_df = pd.read_csv("lat_long.csv")
lat_lon_df = lat_lon_df.transpose()
df = pd.read_csv("crop_production.csv")
df = df[df["State_Name"]=="Maharashtra"]
merged_df = pd.merge(df, lat_lon_df, left_on='District_Name', right_index=True, how='left')
merged_df = merged_df.rename(columns={0: 'lat', 1: 'lon'})
st.map(merged_df)
# print(merged_df)