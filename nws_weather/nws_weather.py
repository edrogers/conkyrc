from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import pkgutil
import re
from typing import Any, Mapping

import requests
import typer

app = typer.Typer()

weather_path = Path.home() / ".cache" / "weather.json"


@dataclass
class Location:
    station_id: str
    forecast_office_id: str
    forecast_gridpoint_x: int
    forecast_gridpoint_y: int


madison = Location(
    station_id="KMSN",
    forecast_office_id="MKX",
    forecast_gridpoint_x=37,
    forecast_gridpoint_y=63
)

@dataclass
class Forecast:
    high: int
    low: int
    cond: str
    code: int
    day: str


@app.command()
def get_weather_feature(
    days_out: int = typer.Option(..., "--days-out", "-d"),
    feature: str = typer.Option(..., "--feature", "-f"),
) -> str | float | int:
    """Given a number of days_out and a feature, return a single value
    from either the current weather conditions or the forecast.

    Args:
        days_out (int): 
            A number in the range [0, 3]
        feature (str): 
            One of "Day", "Temp", "High", "Low",
            "Cond", "Code", "Pres", "Humi", "Wind"

    Returns:
        str | float | int: The value of the feature requested (w/o units)
    """
    weather_data = json.loads(weather_path.read_text())
    if feature in ["Day", "High", "Low", "Code"]:
        forecast = weather_data["forecasts"][days_out]
        print(forecast[feature])
    elif days_out == 0:
        if feature == "Temp":
            print(weather_data["current_temperature"])
        elif feature == "Pres":
            print(weather_data["current_pressure"])
        elif feature == "Humi":
            print(weather_data["current_humidity"])
        elif feature == "Wind":
            print(weather_data["current_windspeed"])
        elif feature == "Cond":
            print(weather_data["current_condition"])
        else:
            raise ValueError(
                f"Unknown feature ({feature}) for days_out == {days_out}"
            )
    else:
        raise ValueError(
            f"Unknown feature ({feature}) for days_out == {days_out}"
        )


@app.command()
def fetch_weather_data(
    station_id: str | None = None,
    forecast_office_id: str | None = None,
    forecast_gridpoint_x: int | None = None,
    forecast_gridpoint_y: int | None = None,
):
    kwargs = [station_id, forecast_office_id, forecast_gridpoint_x, forecast_gridpoint_y]
    if any(kwarg is None for kwarg in kwargs):
        if any(kwarg is not None for kwarg in kwargs):
            raise ValueError(
                "Incomplete argument specification"
            )
        else:
            location = madison
    else:
        location = Location(
            station_id=station_id,
            forecast_office_id=forecast_office_id,
            forecast_gridpoint_x=forecast_gridpoint_x,
            forecast_gridpoint_y=forecast_gridpoint_y,
        )    
    
    current_weather = requests.get(
        f"https://api.weather.gov/stations/{location.station_id}/observations/latest"
    ).json()
    forecast = requests.get(
        f"https://api.weather.gov/gridpoints/{location.forecast_office_id}/{location.forecast_gridpoint_x},{location.forecast_gridpoint_y}/forecast"
    ).json()
    
    cwp = current_weather["properties"]
    current_temperature = round(cwp["temperature"]["value"] * 9/5 + 32)
    current_pressure =  round(cwp["barometricPressure"]["value"] * 0.00029529980164712, 2)
    current_humidity = round(cwp["relativeHumidity"]["value"])
    current_windspeed = round(cwp["windSpeed"]["value"] * 0.621371, 2)
    current_condition = cwp["textDescription"]
    forecast_periods = forecast["properties"]["periods"]
    tonight_period_number = max(
        [
            period["number"] 
            for period 
            in forecast_periods 
            if period["name"] == "Tonight"
        ]
    )
    
    forecast_days = []
    for day_num in range(3):
        period_1, period_2 = forecast_periods[
            tonight_period_number+day_num*2:tonight_period_number+(day_num+1)*2
        ]
        forecast_days.append(extract_forecast_from_period_pair(period_1, period_2))

    results = {
        "current_temperature": current_temperature,
        "current_pressure": current_pressure,
        "current_humidity": current_humidity,
        "current_windspeed": current_windspeed,
        "current_condition": current_condition,
        "forecasts": forecast_days,
        "metadata": {
            "fetch_timestamp": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
            "current_weather_generated_at": cwp["timestamp"],
            "forecast_generated_at": forecast["properties"]["generatedAt"]
        }
    }
    weather_path.write_text(json.dumps(results, indent=2))
    

def extract_forecast_from_period_pair(
    period_1: Mapping[str, Any],  # the odd period, with the High
    period_2: Mapping[str, Any],  # the even period, with the Low
) -> dict[str, Any]:
    high = period_1["temperature"]
    low = period_2["temperature"]
    cond = period_1["shortForecast"]
    day = period_1["name"][:3]
    icon_url = period_1["icon"]
    r = re.match(
        r"https:\/\/api\.weather\.gov\/icons\/land\/(day|night)\/(\w*).*",
        icon_url
    )
    nws_code = r.group(2)
    nws_to_yahoo_map = json.loads(
        pkgutil.get_data("nws_weather", "nws_to_yahoo_code_map.json").decode("utf8")
    )
    yahoo_code = nws_to_yahoo_map[nws_code]
    return {
        "High": high,
        "Low": low,
        "Cond": cond,
        "Code": yahoo_code,
        "Day": day,
    }


if __name__ == "__main__":
    app()
