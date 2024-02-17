import pandas as pd
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

state="Maharashtra"

api_key = os.environ.get("GEO_API_KEY")

df = pd.read_csv("crop_production.csv")
df = df[df["State_Name"]==state]
print(df["District_Name"].unique())
lat_lon_df = pd.DataFrame(columns=["District_Name", "lat", "lon"])

for district in df["District_Name"].unique():
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={district} {state}&aqi=no"
    response = json.loads(requests.get(url).content)
    if response["location"] is None :
        print(f"\nCoordinates for {district} could not be found! Enter coordinates manually.")
        lat_lon_df.loc[len(lat_lon_df)] = [district, None, None]
        continue
    elif response["location"]["country"] != "India" and state not in response["location"]["region"]:
        print(f"\nCoordinates for {district} were not found in the region you were looking for! Enter coordinates manually.")
        lat_lon_df.loc[len(lat_lon_df)] = [district, None, None]
        continue
    lat_lon_df.loc[len(lat_lon_df)] = [district, response["location"]["lat"], response["location"]["lon"]]

lat_lon_df.to_csv("lat_lon.csv", index=False)
