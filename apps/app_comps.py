import blizzcolors
import constructor
import dash_core_components as dcc
import dash_html_components as html
import dash_table
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
        html.P("Select specs for each party slot."),
        constructor.multi_spec_dropdown(id_="tank_slot", role="tank"),
        constructor.multi_spec_dropdown(id_="healer_slot", role="healer"),
        constructor.multi_spec_dropdown(id_="first_dps_slot", role="dps"),
        constructor.multi_spec_dropdown(id_="second_dps_slot", role="dps"),
        constructor.multi_spec_dropdown(id_="third_dps_slot", role="dps"),
        html.Button("FIND COMPS", id="comp-finder-submit-button", n_clicks=0),
        html.Div(id="app-comps-display-value"),
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
    if fields == []:
        return "SHOW ALL COMPS HERE"
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
    cmpz = composition[mask]  # [:100]
    return format_output(cmpz[["composition", "run_count", "level_mean", "level_std"]])


def format_output(result: pd.DataFrame):
    """Formats results of the comp search into a data table."""
    result = blizzcolors.get_full_comp(result)
    result = result.drop(["index", "composition"], axis=1)
    print(result)

    specs = blizzcolors.Specs().specs
    token_to_color = dict(
        [[spec["token"], "rgb(%d,%d,%d)" % spec["color"]] for spec in specs]
    )
    print(list(token_to_color))
    print(token_to_color)
    result_table = dash_table.DataTable(
        id="comp_result",
        columns=[{"name": col, "id": col} for col in result.columns],
        data=result.to_dict("records"),
        # sort_action="native",
        # sort_mode="multi",
        # page_action="custom",
        row_selectable="single",
        page_size=100,
        style_as_list_view=True,
        style_cell={
            # "backgroundColor": "rgb(96, 96, 96)",
            "fontWeight": "bold",
            "textAlign": "left",
            "text-transform": "uppercase"
            # "text-shadow": "1px 1px 1px black",
        },
        style_data_conditional=(
            [
                {
                    "if": {
                        "filter_query": "{tank} = %s" % spec_token,
                        "column_id": "tank",
                    },
                    "backgroundColor": token_to_color[spec_token],
                    "fontWeight": "bold",
                }
                for spec_token in list(token_to_color)
            ]
            + [
                {
                    "if": {
                        "filter_query": "{healer} = %s" % spec_token,
                        "column_id": "healer",
                    },
                    "backgroundColor": token_to_color[spec_token],
                    "fontWeight": "bold",
                }
                for spec_token in list(token_to_color)
            ]
            + [
                {
                    "if": {
                        "filter_query": "{dps1} = %s" % spec_token,
                        "column_id": "dps1",
                    },
                    "backgroundColor": token_to_color[spec_token],
                    "fontWeight": "bold",
                }
                for spec_token in list(token_to_color)
            ]
            + [
                {
                    "if": {
                        "filter_query": "{dps2} = %s" % spec_token,
                        "column_id": "dps2",
                    },
                    "backgroundColor": token_to_color[spec_token],
                    "fontWeight": "bold",
                }
                for spec_token in list(token_to_color)
            ]
            + [
                {
                    "if": {
                        "filter_query": "{dps3} = %s" % spec_token,
                        "column_id": "dps3",
                    },
                    "backgroundColor": token_to_color[spec_token],
                    "fontWeight": "bold",
                }
                for spec_token in list(token_to_color)
            ]
            # + [{"if": {"row_index": "odd"}, "backgroundColor": "dark gray"}]
        ),
        style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
    )
    return result_table
