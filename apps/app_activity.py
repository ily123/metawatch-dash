import math
import time

import blizzcolors
import constructor
import dash_core_components as dcc
import dash_html_components as html
import dataserver
import figure
import pandas as pd
from app import app
from dash.dependencies import Input, Output, State

DB_FILE_PATH = "data/summary.sqlite"
dataserver_ = dataserver.DataServer(DB_FILE_PATH)
data = dataserver_.get_activity_data()
fig_ = figure.BasicBarChart(data)
fig = fig_.draw_figure()
fig = constructor.annotate_weekly_figure(fig)

layout = html.Div(
    [
        html.H3("PLAYER ACTIVITY"),
        html.P(
            """This figure shows the number of runs recorded each week
            since the start of BFA S4."""
        ),
        dcc.Graph(figure=fig),
    ]
)
