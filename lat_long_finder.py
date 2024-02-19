import pandas as pd
import requests
import json
from dotenv import load_dotenv
import os
import sys
import numpy as np

INDIAN_STATE_LIST = ['Andaman and Nicobar Islands', 'Andhra Pradesh', 'Arunachal Pradesh',
 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'Dadra and Nagar Haveli',
 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir ',
 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Puducherry', 'Punjab',
 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana ', 'Tripura', 'Uttar Pradesh',
 'Uttarakhand', 'West Bengal']

# Generates a csv file containing the district name, latitude and longitude for a given state. 
# Districts in the crop_production.csv are used only
def generate_lat_lon_csv(state):
    assert state in INDIAN_STATE_LIST, f"'{state}' is not a valid state."
    lat_lon_file = os.path.join(os.getcwd(), f"State Files/lat_lon_{'_'.join(word for word in state.split())}.csv")
    if os.path.isfile(lat_lon_file):
        return
    load_dotenv()
    api_key = os.environ.get("GEO_API_KEY")
    df = pd.read_csv("crop_production.csv")
    df = df[df["State_Name"]==state]
    print(df["District_Name"].unique())
    lat_lon_df = pd.DataFrame(columns=["District_Name", "lat", "lon"])

    # Make API calls to get all latitutes and longitudes
    for district in df["District_Name"].unique():
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={district} {state}&aqi=no"
        response = json.loads(requests.get(url).content)
        if 'error' in response or 'location' not in response :
            print(f"\nCoordinates for {district} could not be found! Enter coordinates manually.")
            lat_lon_df.loc[len(lat_lon_df)] = [district, np.nan, np.nan]
            continue
        elif response["location"]["country"] != "India" or state not in response["location"]["region"]:
            print(f"\nCoordinates for {district} were not found in the region you were looking for! Enter coordinates manually.")
            lat_lon_df.loc[len(lat_lon_df)] = [district, np.nan, np.nan]
            continue
        lat_lon_df.loc[len(lat_lon_df)] = [district, response["location"]["lat"], response["location"]["lon"]]

    lat_lon_df.to_csv(lat_lon_file, index=False)


if __name__ == "__main__":
    # Check if the user has provided at least one argument for the state
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <state>")
        sys.exit(1)  # Exit the script with a non-zero status to indicate an error

    # Get the state argument from the command line but user will have to pass state in the correct case
    # eg. 'Tamil Nadu' is correct, but 'tamil nadu'/'tamil Nadu'/'Tamil nadu' are not
    state = ' '.join(sys.argv[1:])

    # Call the function to process the state
    generate_lat_lon_csv(state)