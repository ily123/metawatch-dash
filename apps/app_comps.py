import blizzcolors
import constructor
import dash_core_components as dcc
import dash_html_components as html
import dataserver
from app import app
from dash.dependencies import Input, Output

DB_FILE_PATH = "data/summary.sqlite"
dataserver_ = dataserver.DataServer(DB_FILE_PATH)
composition = dataserver_.get_comp_data()
composition = blizzcolors.vectorize_comps(composition)

layout = html.Div(
    [
        html.H3("COMPOSITION EXPLORER"),
        html.P("Select roles for each party slot."),
        constructor.multi_spec_dropdown(id_="tank_slot", role="tank"),
        constructor.multi_spec_dropdown(id_="healer_slot", role="healer"),
        constructor.multi_spec_dropdown(id_="first_dps_slot", role="mdps"),
        constructor.multi_spec_dropdown(id_="second_dps_slot", role="rdps"),
        constructor.multi_spec_dropdown(id_="third_dps_slot", role="mdps"),
        html.Div(id="app-comps-display-value"),
    ]
)


@app.callback(
    Output("app-comps-display-value", "children"), Input("app-comps-dropdown", "value")
)
def display_value(value):
    return 'You have selected COMPS "{}"'.format(id(dataserver_))
