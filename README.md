# Metawatch Dashboard


![Python](https://img.shields.io/badge/python-3.6%7C3.7-blue.svg)
[![License](https://img.shields.io/badge/license-GPL3-blue.svg)](https://github.com/ily123/metawatch-dash/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Dashboard to visualize patterns of player behavior in Blizzard's World of Warcraft.

For backend see [this repo](https://github.com/ily123/metawatch), and deployed
application [here](https://bit.ly/35ZdAvD)

# Installation and Usage
* Clone repo locally
    ```
    git clone https://github.com/ily123/metawatch-dash
    ```
* Create & activate virtual env using your favorite tool
* Install dependensices inside the env
    ```
    pip install -r requirements.txt
    ```
* Rename ```data/example_summary.sqlite``` to ```data/summary.sqlite```
* Launch the app
    ```
    python application.py
    ```
* To see in browser go to:
    ```
    localhost:8080
    ```

