import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as plt

st.write('''
         # Data Dashboard''')

df1 = pd.read_csv("crop_production.csv")
df = pd.DataFrame(np.random.randn(1000, 2) / [50, 50] + [18.521428, 73.8544541], columns=['lat', 'lon'])
st.map(df)
st.write(df1)