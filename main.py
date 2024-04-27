import requests
from datetime import datetime
import smtplib
import time
import os

MY_LAT = float(os.environ.get("MY_LAT"))  # Your latitude
MY_LONG = float(os.environ.get("MY_LONG"))  # Your longitude

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

OWM_API_KEY = os.environ.get("OWM_API_KEY")


# Your position is within +5 or -5 degrees of the ISS position.
def within_5():
    #  ISS Details
    iss_response = requests.get(url="http://api.open-notify.org/iss-now.json")
    iss_response.raise_for_status()
    iss_data = iss_response.json()

    iss_latitude = float(iss_data["iss_position"]["latitude"])
    iss_longitude = float(iss_data["iss_position"]["longitude"])

    if abs(MY_LAT - iss_latitude) <= 5 and abs(MY_LONG - iss_longitude) < 5:
        return True


#  Checks that the current hour is between sunrise and sunset in your location
def hour_between():
    #  Sunrise Details
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }

    sun_response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    sun_response.raise_for_status()
    sun_data = sun_response.json()
    sunrise = int(sun_data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(sun_data["results"]["sunset"].split("T")[1].split(":")[0])
    current_hour = datetime.now().hour

    return current_hour >= sunset or current_hour <= sunrise


# Checks that cloud cover is low enough
def low_cloud_cover():
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LONG,
        "units": "metric",
        "appid": OWM_API_KEY
    }

    cloud_response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=parameters)
    cloud_response.raise_for_status()
    cloud_data = cloud_response.json()
    cloud_current = cloud_data["current"]["clouds"]
    return int(cloud_current) <= 30


#  Code
while within_5() and hour_between() and low_cloud_cover():
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=PASSWORD)
        connection.sendmail(
            from_addr=EMAIL,
            to_addrs=EMAIL,
            msg=f"Subject:ISS ALERT\n\nLook up, the ISS is about!"
        )
    time.sleep(60)
