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
    prevent_initial_call=True,
)
def find_compositions(
    value, tank_slot, healer_slot, first_dps_slot, second_dps_slot, third_dps_slot
):
    """Finds compositions that include selected specs."""
    fields = [tank_slot, healer_slot, first_dps_slot, second_dps_slot, third_dps_slot]
    fields = [field for field in fields if field]
    # Each field can have multiple entries. These need to be treated as
    # OR selectors. For example, if field = [a, b, c], find all comps that
    # include a or b or c
    mask = None
    for field in fields:  # too many loops T_T
        field_mask = None
        if len(field) > 1:
            for spec in field:
                if type(field_mask) == pd.Series:
                    field_mask = (field_mask) | (composition[spec] > 0)
                else:
                    field_mask = composition[spec] > 0
        else:
            # the .count is there in case the user wants to find comp
            # with two or three of the same spec
            field_mask = composition[field[0]] >= fields.count(field)
        if type(mask) == pd.Series:
            mask = mask & field_mask
        else:
            mask = field_mask
    print(fields)
    print(mask.sum())
    print(composition[mask])
    return 'You have selected "{}"'.format(value)
