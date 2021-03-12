import datetime
import os

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, application
from apps import app_activity, app_comps, app_faq, app_specs, app_patrons, app_character

DB_FILE_PATH = "data/summary.sqlite"
data_last_updated = datetime.datetime.fromtimestamp(
    int(os.path.getmtime(DB_FILE_PATH))
).strftime("%Y-%m-%d")

app.layout = html.Div(
    id="main-wrap",
    children=[
        dcc.Location(id="url", refresh=False),
        html.Header(html.H1("BENCHED.me")),
        html.Nav(
            [
                html.A("SPECS", href="/"),
                html.A("COMPS", href="/comps"),
                html.A("PLAYER ACTIVITY", href="/activity"),
                html.A("FAQ", href="/faq"),
                html.A(id="patron_anchor", children="Patrons", href="/patrons"),
                # I need this for later:
                # html.A("OVERVIEW", href="#figure1"),
                # html.A("SPEC PERFORMANCE", href="#figure2"),
                # html.A("WEEKLY TOP 500", href="#figure3"),
                # html.A("TIER LIST", href="#figure4"),
                # html.A("FAQ", href="#faq"),
            ]
        ),
        html.P(
            "Data updated: %s" % data_last_updated,
            style={"text-align": "right"},
        ),
        html.Main(id="page-content"),
        html.Footer(
            children=[
                html.P("Created by Uni in 2020"),
                html.P(html.A("Discord", href="https://discord.gg/FShx8cX4AY")),
                html.P(html.A("Patreon", href="https://www.patreon.com/benched")),
            ]
        ),
    ],
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname: str) -> html.Div:
    """Returns main content of the page."""
    if pathname == "/comps":
        return app_comps.layout
    elif pathname == "/activity":
        return app_activity.layout
    elif pathname == "/faq":
        return app_faq.layout
    elif pathname == "/":
        return app_specs.layout
    elif pathname == "/patrons":
        return app_patrons.layout
    elif pathname == "/abc123x":
        return app_character.layout
    else:
        return "This URL does not exist: ERROR 404"


if __name__ == "__main__":
    application.run(debug=True, port=8080)
