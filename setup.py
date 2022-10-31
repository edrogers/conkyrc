from setuptools import setup, find_packages
from nws_weather import __version__

setup(
    name="nws_weather",
    version=__version__,
    package_data={"nws_weather": ["nws_to_yahoo_code_map.json"]},
    packages=find_packages(),
    python_requires=">=3.10",
    include_package_data=True,
    install_requires=["requests", "typer"],
    entry_points="""
        [console_scripts]
        nwsweather=nws_weather.nws_weather:app
    """,
)
