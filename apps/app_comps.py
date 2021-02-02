import math
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
print(composition)
composition = blizzcolors.vectorize_comps(composition)
# check that each comp has 5 members
members = composition.composition.astype(str).map(len)
composition = composition[members == 5]
# check that each comp has a healer and a tank
tank_cols = [
    "death_knight_blood",
    "demon_hunter_vengeance",
    "druid_guardian",
    "monk_brewmaster",
    "paladin_protection",
    "warrior_protection",
]
healer_cols = [
    "druid_restoration",
    "monk_mistweaver",
    "paladin_holy",
    "priest_discipline",
    "priest_holy",
    "shaman_restoration",
]

mask_tanks = composition[tank_cols].sum(axis=1) == 1
mask_healers = composition[healer_cols].sum(axis=1) == 1
mask = mask_tanks & mask_healers
composition = composition[mask]

layout = html.Div(
    [
        html.H3("COMPOSITION EXPLORER"),
        html.P(
            """Select specs for each party slot.
            You can type part of the spec name to filter the dropdown list."""
        ),
        constructor.multi_spec_dropdown(id_="tank_slot", role="tank"),
        constructor.multi_spec_dropdown(id_="healer_slot", role="healer"),
        constructor.multi_spec_dropdown(id_="first_dps_slot", role="dps"),
        constructor.multi_spec_dropdown(id_="second_dps_slot", role="dps"),
        constructor.multi_spec_dropdown(id_="third_dps_slot", role="dps"),
        constructor.sortby_dropdown(id_="sort-by-dropdown"),
        html.Div(
            html.Button("FIND COMPS", id="comp-finder-submit-button", n_clicks=0),
            id="comp-finder-submit-button-wrapper",
        ),
        html.Br(),
        html.Div(id="app-comps-display-value"),
        html.Div(
            children=[
                html.P("Page", id="page-label", className="pagination-wrap"),
                dcc.Input(
                    id="comp-page-number",
                    className="pagination-wrap",
                    type="number",
                    placeholder=1,
                    value=1,
                ),
                html.Button(
                    "Go",
                    className="pagination-wrap",
                    id="page-submit-button",
                    n_clicks=0,
                ),
                html.P(id="page-count-label", className="pagination-wrap"),
            ],
        ),
    ]
)


@app.callback(
    [
        Output(component_id="app-comps-display-value", component_property="children"),
        Output(component_id="comp-page-number", component_property="value"),
        Output(component_id="page-count-label", component_property="children"),
    ],
    Input(component_id="comp-finder-submit-button", component_property="n_clicks"),
    Input(component_id="page-submit-button", component_property="n_clicks"),
    [
        State(component_id="sort-by-dropdown", component_property="value"),
        State(component_id="comp-page-number", component_property="value"),
        State(
            component_id="comp-finder-submit-button",
            component_property="n_clicks_timestamp",
        ),
        State(
            component_id="page-submit-button", component_property="n_clicks_timestamp"
        ),
        State(component_id="tank_slot", component_property="value"),
        State(component_id="healer_slot", component_property="value"),
        State(component_id="first_dps_slot", component_property="value"),
        State(component_id="second_dps_slot", component_property="value"),
        State(component_id="third_dps_slot", component_property="value"),
    ],
    prevent_initial_call=False,
)
def find_compositions(
    main_submit_click,
    page_change_click,
    sortby,
    page_number,
    main_click_ts,
    page_click_ts,
    tank_slot,
    healer_slot,
    first_dps_slot,
    second_dps_slot,
    third_dps_slot,
):
    """Finds compositions that include selected specs."""
    if page_number < 1:
        page_number = 1
    if main_click_ts and page_click_ts:
        if int(main_click_ts) > int(page_click_ts):
            page_number = 1
    fields = [tank_slot, healer_slot, first_dps_slot, second_dps_slot, third_dps_slot]
    fields = [field for field in fields if field]
    mask = None
    if fields == []:
        mask = [True] * len(composition)
    # Each field can have multiple entries. These need to be treated as
    # OR selectors. For example, if field = [a, b, c], find all comps that
    # include a or b or c
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
    cmpz = composition[mask].copy(deep=True)
    # sort the result inplace
    sortby_col = {
        "max+total+avg": ["level_max", "run_count", "level_mean"],
        "max+avg+total": ["level_max", "level_mean", "run_count"],
        "total": ["run_count", "level_mean"],
        "avg": ["level_mean", "run_count"],
    }
    cmpz.sort_values(by=sortby_col[sortby], axis=0, ascending=False, inplace=True)
    total_pages = math.ceil(len(cmpz) / 50.0)

    if page_number > total_pages:
        page_number = total_pages - 1
        cmpz = cmpz[page_number * 50 :]
    else:
        page_number = page_number - 1
        cmpz = cmpz[50 * page_number : (50 * page_number) + 50]
    return format_output(cmpz), page_number + 1, "of %d" % total_pages


# def find_tank(result: pd.DataFrame):


def format_output(result0: pd.DataFrame) -> html.Table:
    """Formats results of the comp search into a data table."""
    # Formatting the results is a massive PITA.
    # There are 40+ columns, and condensing them into something that
    # both fits on the screen and is interpretable is rough.
    # So here is what we do:
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
    # drop both healers and tanks from the main table
    result0.drop(
        inplace=True,
        labels=tank_cols + healer_cols,
        axis=1,
    )
    # and append the condensed columns
    result0["tank"] = tanks
    result0["healer"] = healers

    # remove stats for now
    stats = result0[["run_count", "level_mean", "level_max"]].copy(deep=True)
    stats = stats.round(decimals=1)
    stats = list(stats.values)
    result0.drop(
        inplace=True,
        labels=["composition", "run_count", "level_mean", "level_std", "level_max"],
        axis=1,
    )
    t0 = time.time()
    # Drop DPS columns that are all 0.
    mask = list(result0.sum(axis=0) != 0)
    result0 = result0.loc[:, mask]

    # rearrange columns
    new_order = ["tank", "healer"]
    dps_cols = [dps for dps in result0.columns if dps not in new_order]
    dps_order = result0[dps_cols].sum(axis=0)
    dps_order = dps_order.sort_values(ascending=False, inplace=False).index.values
    new_order.extend(dps_order)
    result0 = result0[new_order]

    rows = result0.apply(lambda row: list(row), axis=1)
    colors = dict(
        [[spec["token"], spec["color"]] for spec in blizzcolors.Specs().specs]
    )
    chars = 10
    if len(result0.columns) >= 20:
        chars = 2
    elif len(result0.columns) < 20 and len(result0.columns) >= 17:
        chars = 3
    elif len(result0.columns) < 17 and len(result0.columns) >= 10:
        chars = 4
    abbr = dict(
        [[spec["token"], spec["abbr"][:chars]] for spec in blizzcolors.Specs().specs]
    )
    table = html.Table(children=[])
    for row_index, row in enumerate(rows):
        row_ = html.Tr(
            children=[
                html.Td(stats[row_index][0]),
                html.Td("%1.1f" % stats[row_index][1]),
                html.Td(stats[row_index][2]),
            ]
        )
        bg_color = "lightgray" if row_index % 2 == 0 else "white"
        for index, cell in enumerate(row):
            style = {}
            if result0.columns[index] in ["tank", "healer"]:
                color = colors[cell]
                style = {
                    "background-color": "rgb(%d,%d,%d)" % color,
                    "border": "1px solid black",
                }
                title = cell.upper().replace("_", " ")
                cell = abbr[cell]
            elif cell == 0:
                style = {"background-color": bg_color, "color": bg_color}
                title = ""
            else:
                style = {
                    "background-color": "rgb(%d,%d,%d)"
                    % colors[result0.columns[index]],
                    "border": "1px solid black",
                }
                title = result0.columns[index].upper().replace("_", " ")
                if cell == 1:
                    cell = abbr[result0.columns[index]]
                else:
                    cell = "x%d" % cell
            row_.children.append(html.Td(cell, title=title, style=style))
        row_.style = {"background-color": bg_color}
        table.children.append(row_)
    table.children.insert(
        0,
        html.Tr(
            [
                html.Th(column[:chars])
                for column in ["N", "AVG", "MAX", "TANK", "HLR"]
                + [abbr[tkn] for tkn in result0.columns[2:]]
            ],
            style={"font-size": "15px"},
        ),
    )
    print("Table formatting ", time.time() - t0)
    return table
