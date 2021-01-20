import dash_core_components as dcc
import dash_html_components as html
import dataserver
from app import app
from dash.dependencies import Input, Output

DB_FILE_PATH = "data/summary.sqlite"
dataserver_ = dataserver.DataServer(DB_FILE_PATH)

layout = html.Div(
    [
        html.H3("SPECS"),
        dcc.Dropdown(
            id="app-specs-dropdown",
            options=[
                {"label": "App 1 - {}".format(i), "value": i}
                for i in ["NYC", "MTL", "LA"]
            ],
        ),
        html.Div(id="app-specs-display-value"),
        dcc.Link("Go to Comps", href="/comps"),
    ]
)


@app.callback(
    Output("app-specs-display-value", "children"), Input("app-specs-dropdown", "value")
)
def display_value1(value):
    return 'You have selected SPECS "{}"'.format(id(dataserver_))
