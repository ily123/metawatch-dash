# Metawatch Dashboard


![Python](https://img.shields.io/badge/python-3.6%7C3.7-blue.svg)
[![License](https://img.shields.io/badge/license-GPL3-blue.svg)](https://github.com/ily123/metawatch-dash/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Dashboard to visualize patterns of player behavior in Blizzard's World of Warcraft.

For backend see [this repo](https://github.com/ily123/metawatch), and deployed
application [here](https://bit.ly/35ZdAvD)

# Installation and Usage
* The code was tested on Python 3.6.9 and 3.7.9, but should run on any major version 3.6 and up

* To run dashboard locally, clone repo
    ```
    git clone https://github.com/ily123/metawatch-dash
    ```
* Create & activate virtual env using your favorite tool
    ```
    python3 -m venv myenv
    source myenv/bin/activate
    ```
* Install dependensices inside the env
    ```
    cd metawatch-dash/
    pip install -r requirements.txt
    ```
* Rename ```data/example_summary.sqlite``` to ```data/summary.sqlite```:
    ```
    mv data/example_summary.sqlite data/summary.sqlite
    ```
* Launch the app
    ```
    python application.py
    ```
* To see in browser go to:
    ```
    localhost:8080
    ```
* To quit:
    ```
    # press Ctrl + C to stop the app server
    # to exit virtual env
    deactivate
    ```

