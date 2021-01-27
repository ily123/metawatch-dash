import time

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
x = composition.composition.astype(str).map(len)
composition = composition[x == 5]
composition = blizzcolors.vectorize_comps(composition)

layout = html.Div(
    [
        html.H3("COMPOSITION EXPLORER"),
        html.P(
            "Select specs for each party slot. Type inside field to search spec name."
        ),
        constructor.multi_spec_dropdown(id_="tank_slot", role="tank"),
        constructor.multi_spec_dropdown(id_="healer_slot", role="healer"),
        constructor.multi_spec_dropdown(id_="first_dps_slot", role="dps"),
        constructor.multi_spec_dropdown(id_="second_dps_slot", role="dps"),
        constructor.multi_spec_dropdown(id_="third_dps_slot", role="dps"),
        html.Button("FIND COMPS", id="comp-finder-submit-button", n_clicks=0),
        dcc.Input(id="comp-page-number", type="number", placeholder=1, value=1),
        html.Button("Go", id="page-submit-button", n_clicks=0),
        html.Div(id="app-comps-display-value"),
    ]
)


@app.callback(
    Output(component_id="app-comps-display-value", component_property="children"),
    Input(component_id="comp-finder-submit-button", component_property="n_clicks"),
    Input(component_id="page-submit-button", component_property="n_clicks"),
    [
        State(component_id="comp-page-number", component_property="value"),
        State(component_id="tank_slot", component_property="value"),
        State(component_id="healer_slot", component_property="value"),
        State(component_id="first_dps_slot", component_property="value"),
        State(component_id="second_dps_slot", component_property="value"),
        State(component_id="third_dps_slot", component_property="value"),
    ],
    prevent_initial_call=True,
)
def find_compositions(
    main_submit_click,
    page_change_click,
    page_number,
    tank_slot,
    healer_slot,
    first_dps_slot,
    second_dps_slot,
    third_dps_slot,
):
    """Finds compositions that include selected specs."""
    page_number = page_number - 1
    t0 = time.time()
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
    print("Comp filtering: ", time.time() - t0)
    return format_output(
        cmpz[50 * page_number : (50 * page_number) + 50]
    )  # [["composition", "run_count", "level_mean", "level_std"]])


# def find_tank(result: pd.DataFrame):


def format_output(result0: pd.DataFrame) -> html.Table:
    """Formats results of the comp search into a data table."""
    # Formatting the results is a massive PITA.
    # There are 40+ columns, and condensing them into something that
    # both fits on the screen and is interpretable is rough.
    # So here is what we do:
    print(result0)
    # Find the tanks and condense them into a single column.
    tank_cols = [
        "death_knight_blood",
        "demon_hunter_vengeance",
        "druid_guardian",
        "monk_brewmaster",
        "paladin_protection",
        "warrior_protection",
    ]
    tanks = result0[tank_cols].apply(lambda row: tank_cols[list(row).index(1)], axis=1)
    # Find the healers and condense them into a single column.
    healer_cols = [
        "druid_restoration",
        "monk_mistweaver",
        "paladin_holy",
        "priest_discipline",
        "priest_holy",
        "shaman_restoration",
    ]
    healers = result0[healer_cols].apply(
        lambda row: healer_cols[list(row).index(1)], axis=1
    )
    print(healers)
    # drop both healers and tanks from the main table
    result0.drop(
        inplace=True,
        labels=tank_cols + healer_cols,
        axis=1,
    )
    # and append the condensed columns
    result0["tank"] = tanks
    result0["healer"] = healers

    # Drop DPS columns that are all 0.
    result0 = result0.copy()
    mask = result0.sum(axis=0) != 0
    mask = list(mask)
    result0 = result0.loc[:, mask].copy()
    # remove stats for now
    stats = result0[["run_count", "level_mean", "level_std"]].copy()
    stats = stats.round(decimals=1)
    stats = list(stats.values)
    print(stats)
    result0.drop(
        inplace=True,
        labels=["composition", "run_count", "level_mean", "level_std"],
        axis=1,
    )
    t0 = time.time()

    # rearrange columns
    new_order = ["tank", "healer"]
    dps_cols = [dps for dps in result0.columns if dps not in new_order]
    dps_order = result0[dps_cols].sum(axis=0).copy()
    dps_order = dps_order.sort_values(ascending=False, inplace=False).index.values
    new_order.extend(dps_order)
    result0 = result0[new_order].copy()
    print(result0)

    rows = result0.apply(lambda row: list(row), axis=1)
    # spec_name_to_col_index = dict(zip(range(len(result0.columns), result0.columns)))
    colors = dict(
        [[spec["token"], spec["color"]] for spec in blizzcolors.Specs().specs]
    )
    abbr = dict([[spec["token"], spec["abbr"]] for spec in blizzcolors.Specs().specs])
    table = html.Table(children=[])
    for row_index, row in enumerate(rows):
        row_ = html.Tr(children=[html.Td(stats[row_index][i]) for i in range(3)])
        bg_color = "lightgray" if row_index % 2 == 0 else "white"
        for index, cell in enumerate(row):
            style = {}
            if result0.columns[index] in ["tank", "healer"]:
                color = colors[cell]
                style = {
                    "background-color": "rgb(%d,%d,%d)" % color,
                    "border": "1px solid black",
                }
                cell = abbr[cell]
            elif cell == 0:
                style = {"background-color": bg_color, "color": bg_color}
            else:
                style = {
                    "background-color": "rgb(%d,%d,%d)"
                    % colors[result0.columns[index]],
                    "border": "1px solid black",
                }
                if cell == 1:
                    cell = abbr[result0.columns[index]]
                else:
                    cell = "%sx%d" % (abbr[result0.columns[index]][0:2], cell)
            row_.children.append(html.Td(cell, style=style))
        row_.style = {"background-color": bg_color}
        table.children.append(row_)
    table.children.insert(
        0,
        html.Tr(
            [
                html.Th(column)
                for column in ["N", "AVG", "STD", "TANK", "HLR"]
                + [abbr[tkn] for tkn in result0.columns[2:]]
            ],
            style={"font-size": "15px"},
        ),
    )
    print("Table formatting ", time.time() - t0)
    print(result0.columns)
    return table
