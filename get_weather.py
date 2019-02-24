#!/usr/bin/env python

import argparse
import json


def get_weather_feature(days_out, feature):
    with open("/home/ed/.cache/weather.json", "r") as f:
        weather_json = json.load(f)
        feature_dict = {
        "High": weather_json["forecasts"][days_out]["high"],
        "Low":            weather_json["forecasts"][days_out]["low"],
        "Cond":            weather_json["forecasts"][days_out]["text"],
        "Code":            weather_json["forecasts"][days_out]["code"],
        "Day":            weather_json["forecasts"][days_out]["day"],
        }
        if days_out == 0:
            feature_dict["Temp"] = weather_json["current_observation"]["condition"]["temperature"]
            feature_dict["Pres"] = weather_json["current_observation"]["atmosphere"]["pressure"]
            feature_dict["Humi"] = weather_json["current_observation"]["atmosphere"]["humidity"]
            feature_dict["Wind"] = weather_json["current_observation"]["wind"]["speed"]

        try:
            return feature_dict[feature]
        except KeyError as e:
            raise NotImplementedError(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract weather specifics")
    parser.add_argument(
        "-d", 
        "--days_out",
        type=int,
        help="An int in range(0, 3)"
    )
    parser.add_argument(
        "-f", 
        "--feature",
        type=str,
        help=(
            'One of "Day", "Temp", "High", "Low", '
            '"Cond", "Code", "Pres", "Humi", "Wind"'
        ),
    )

    args = parser.parse_args()
    if (args.days_out is not None) and (args.feature is not None):
        print get_weather_feature(args.days_out, args.feature)
    else:
        raise ValueError("Expected 2 arguments, days_out and feature")
