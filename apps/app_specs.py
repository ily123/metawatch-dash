import dash_core_components as dcc
import dash_html_components as html
from app import app
from dash.dependencies import Input, Output

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
    return 'You have selected "{}"'.format(value)
