"""App helper for construction of simple HTML components."""
from typing import List

import dash_core_components as dcc
import dash_html_components as html


def season_dropdown(id_: str, ishidden: bool) -> dcc.Dropdown:
    """Constructs dropdown season select menu.

    Parameters
    ----------
    id_ : str
        html id of the component
    ishidden : bool
        visibility of the component

    Returns
    -------
    season_dropdown : dcc.Dropdown
        dropdown component with M+  seasons as options
    """
    dropdown = dcc.Dropdown(
        className="dropdown",
        id=id_,
        options=[
            {"label": "BFA Season 4 (8.3)", "value": "bfa4"},
            {
                "label": "BFA post-patch (9.0.1)",
                "value": "bfa4_postpatch",
            },
            {"label": "SL Season 1 (9.0.2)", "value": "SL1"},
        ],
        value="bfa4",
        clearable=False,
    )
    if ishidden:
        dropdown.style = {"display": "none"}
    return dropdown


def figure_header_ensemble(elements: dict) -> list:
    """Constructs children components of the figure header div.

    Paremeters
    ----------
    elements : dict
        text content of the respective components

    Returns
    -------
    components : list
        list of the html and dcc components

    """
    components = [
        html.A(id=elements["anchor_id"]),
        html.H4(elements["header_title"].upper()),
        dcc.Markdown(elements["summary"]),
        html.Details(
            children=[html.Summary("Key Insights"), dcc.Markdown(elements["insight"])]
        ),
    ]
    if "factoid" in elements:
        components.append(
            html.Details(
                children=[
                    html.Summary("Interesting Factoid"),
                    dcc.Markdown(elements["factoid"]),
                ]
            )
        )
    return components
