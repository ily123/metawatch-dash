import dash_core_components as dcc
import dash_html_components as html
import dataserver
from app import app
from dash.dependencies import Input, Output

DB_FILE_PATH = "data/summary.sqlite"
dataserver_ = dataserver.DataServer(DB_FILE_PATH)

layout = html.Div(
    [
        html.H3("COMPS"),
        dcc.Dropdown(
            id="app-comps-dropdown",
            options=[
                {"label": "App 1 - {}".format(i), "value": i}
                for i in ["NYC", "MTL", "LA"]
            ],
        ),
        html.Div(id="app-comps-display-value"),
        dcc.Link("Go to Specs", href="/"),
    ]
)


@app.callback(
    Output("app-comps-display-value", "children"), Input("app-comps-dropdown", "value")
)
def display_value(value):
    return 'You have selected COMPS "{}"'.format(id(dataserver_))
