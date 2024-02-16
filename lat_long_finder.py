import pandas as pd
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("GEO_API_KEY")

df = pd.read_csv("crop_production.csv")
df = df[df["State_Name"]=="Maharashtra"]
print(df["District_Name"].unique())
lat_long_dict = {}

for district in df["District_Name"].unique():
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={district} maharashtra&aqi=no"
    print(requests.get(url).content)
    response = json.loads(requests.get(url).content)
    if(response["location"] is None):
        continue
    lat_long_dict[district] = (response["location"]["lat"], response["location"]["lon"])

print(lat_long_dict)
pd.DataFrame(lat_long_dict).to_csv("lat_long.csv")
