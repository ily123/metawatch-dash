import constructor
import dash_core_components as dcc
import dash_html_components as html
import dataserver
import figure
from app import app

DB_FILE_PATH = "data/summary.sqlite"
dataserver_ = dataserver.DataServer(DB_FILE_PATH)
data = dataserver_.get_activity_data()
fig_ = figure.BasicBarChart(data)
fig = fig_.draw_figure()
fig = constructor.annotate_weekly_figure(fig)

fig_config = dict(
    modeBarButtonsToRemove=[
        "zoomIn2d",
        "zoomOut2d",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "toggleSpikelines",
        "autoScale2d",
        "lasso2d",
        "select2d",
    ],
    displaylogo=False,
)

layout = html.Div(
    [
        html.H3("PLAYER ACTIVITY"),
        html.P(
            """This figure shows the number of runs recorded each week
            since the start of BFA S4."""
        ),
        dcc.Graph(figure=fig, config=fig_config),
    ]
)
