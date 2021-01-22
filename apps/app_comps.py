import blizzcolors
import constructor
import dash_core_components as dcc
import dash_html_components as html
import dataserver
from app import app
from dash.dependencies import Input, Output, State

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
        html.Button("FIND COMPS", id="comp-finder-submit-button", n_clicks=0),
    ]
)


@app.callback(
    Output(component_id="app-comps-display-value", component_property="children"),
    Input(component_id="comp-finder-submit-button", component_property="n_clicks"),
    [
        State(component_id="tank_slot", component_property="value"),
        State(component_id="healer_slot", component_property="value"),
        State(component_id="first_dps_slot", component_property="value"),
        State(component_id="second_dps_slot", component_property="value"),
        State(component_id="third_dps_slot", component_property="value"),
    ],
)
def find_compositions(
    value, tank_slot, healer_slot, first_dps_slot, second_dps_slot, third_dps_slot
):
    """Finds compositions that include selected specs."""
    print(tank_slot)
    print(healer_slot)
    print(first_dps_slot)
    print(second_dps_slot)
    print(third_dps_slot)
    return 'You have selected "{}"'.format(value)
