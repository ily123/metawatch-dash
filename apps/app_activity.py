import math
import time

import blizzcolors
import constructor
import dash_core_components as dcc
import dash_html_components as html
import dataserver
import pandas as pd
from app import app
from dash.dependencies import Input, Output, State

DB_FILE_PATH = "data/summary.sqlite"
dataserver_ = dataserver.DataServer(DB_FILE_PATH)

layout = html.Div(
    [
        html.H3("PLAYER ACTIVITY"),
        html.P("""This figure shows the number of runs recorded each week."""),
    ]
)
