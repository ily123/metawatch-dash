import datetime
import os

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app_comps, app_specs

DB_FILE_PATH = "data/summary.sqlite"
data_last_updated = datetime.datetime.fromtimestamp(
    int(os.path.getmtime(DB_FILE_PATH))
).strftime("%Y-%m-%d")

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Header(html.H1("BENCHED.me")),
        html.Nav(
            [
                html.A("OVERVIEW", href="#figure1"),
                html.A("SPEC PERFORMANCE", href="#figure2"),
                html.A("WEEKLY TOP 500", href="#figure3"),
                html.A("TIER LIST", href="#figure4"),
                html.A("FAQ", href="#faq"),
            ]
        ),
        dcc.Link("Go to Comps", href="/comps"),
        dcc.Link("Go to Specs", href="/"),
        html.P(
            "Data updated: %s" % data_last_updated,
            style={"text-align": "right"},
        ),
        html.Main(id="page-content"),
        html.Footer(
            children=[
                html.P("Created by Uni in 2020"),
                html.P("Discord"),
                html.P("Patreon"),
            ]
        ),
    ]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname: str) -> html.Div:
    """Returns main content of the page."""
    if pathname == "/comps":
        return app_comps.layout
    elif pathname == "/":
        return app_specs.layout
    else:
        return "This URL does not exist: ERROR 404"


if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
