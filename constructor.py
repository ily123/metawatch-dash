"""App helper for construction of simple HTML components."""
from typing import List

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

import blizzcolors


def multi_spec_dropdown(id_: str, role: str) -> dcc.Dropdown:
    """Constructs spec dropdown for page 2 composition app.

    Parameters
    ----------
    id_ : str
        html id of the component
    role : str
        specs to include in the figure; one of {'tank', 'healer', 'mdps', 'rdps'}

    Returns
    -------
    dropdown : dcc.Dropdown
        dropdown component with specs of given role
    """
    dropdown = dcc.Dropdown(
        id=id_,
        className="spec-input",
        options=[
            {
                "label": spec["spec_name"].upper() + " " + spec["class_name"].upper(),
                "value": spec["token"],
            }
            for spec in blizzcolors.Specs().specs
            if spec["role"][-3:] in role
        ],
        multi=True,
        placeholder="ALL INCLUDED BY DEFAULT.",
    )
    drop_wrap = html.Div(
        children=[html.Label(role.upper()), dropdown],
    )
    return drop_wrap


def sortby_dropdown(id_: str) -> dcc.Dropdown:
    """Constructs sort dropdown for page 2 composition app.

    Parameters
    ----------
    id_ : str
        html id of the component

    Returns
    -------
    dropdown : dcc.Dropdown
        dropdown component with sort option
    """
    dropdown = dcc.Dropdown(
        id=id_,
        className="spec-input",
        options=[
            {
                "label": "Total number of runs (N)",
                "value": "total",
            },
            {
                "label": "Average key level of runs (AVG)",
                "value": "avg",
            },
            {
                "label": "Max Key Level (MAX), then Avg Key Level, then Total Keys",
                "value": "max+avg+total",
            },
            {
                "label": "Max Key Level (MAX), then Total Keys, then Avg Key Level",
                "value": "max+total+avg",
            },
        ],
        value="total",
        clearable=False,
    )
    drop_wrap = html.Div(
        children=[html.Label("SORT BY"), dropdown],
    )
    return drop_wrap


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


def role_options(include_all: bool) -> List[dict]:
    """Returns options for class selection dropdown.

    Parameter
    --------
    include_all: bool
        flag to include "all specs" as one of the options

    Returns
    -------
    role_options : List[dict]
        list of spec role options and values
    """
    role_options = [
        {"label": "TANK", "value": "tank"},
        {"label": "HEALER", "value": "healer"},
        {"label": "MELEE DPS", "value": "mdps"},
        {"label": "RANGE DPS", "value": "rdps"},
    ]
    if include_all:
        role_options.append({"label": "ALL SPECS", "value": "all"})
    return role_options


def spec_dropdown(id_: str, include_all: bool = False) -> dcc.Dropdown:
    """Constructs dropdown with class role options.

    Parameters
    ----------
    id_ : str
        html id of the component
    include_all: bool
        flag to include "all specs" as one of the options

    Returns
    -------
    role_dropdown : dcc.Dropdown
        dropdown component with spec roles as options
    """
    role_dropdown = dcc.Dropdown(
        className="dropdown",
        id=id_,
        options=role_options(include_all),
        placeholder="SELECT SPEC ROLE",
        value="all" if include_all else "tank",
        clearable=False,
    )
    return role_dropdown


def key_level_slider(
    id_: str, range_max: int, selected_range: List[int]
) -> dcc.RangeSlider:
    """Constructs slider for tier list figure.

    Parameters
    ----------
    id_ : str
        name of the component, for callbacks
    range_max : int
        max value of slider range
    selected_range : List[int, int]
        default value position of the slider

    Returns
    ------
    slider : dcc.RangeSlider
    """
    slider = dcc.RangeSlider(
        id=id_,
        min=2,
        max=range_max,
        step=None,
        marks=dict(
            zip(
                range(2, range_max + 1),
                [str(i) for i in range(2, range_max + 1)],
            )
        ),
        value=selected_range,
    )
    return slider


def faq_errata() -> dcc.Markdown:
    """Returns markdown text element for page 1 errata div."""
    errata_and_faq = dcc.Markdown(  # &nbsp; is a hacky way to add a blank line to MD
        """
        **How frequently are the data updated?**

        The data are updated every hour.

        &nbsp;

        **Why did you make this web site? Isn't raider.io enough?**

        Raider.io is great.
        For my part, I wanted a bit more insight into the data, so I made this dashboard.

        Other good M+ stats websites are
        [mplus.subcreation.net](https://mplus.subcreation.net)
        and [bestkeystone.com](https://bestkeystone.com).

        &nbsp;

        **I saw a mistake, have a comment, have an idea**

         My reddit handle is
         [u/OtherwiseUniversity7](https://www.reddit.com/user/OtherwiseUniversity7).
         Drop me a note whenever :)

        &nbsp;
        """
    )
    return errata_and_faq


def annotate_weekly_figure(fig: go.Figure) -> go.Figure:
    """Annotates weekly figure with seasonal labels."""
    # add season timeline labels
    fig.add_annotation(
        dict(
            x=1,
            y=1,
            yref="paper",
            xanchor="left",
            yanchor="top",
            text="BFA S4 begins",
            showarrow=True,
        )
    )
    fig.add_annotation(
        dict(
            x=39,
            y=1,
            yref="paper",
            xanchor="center",
            yanchor="top",
            text="BFA Post-patch begins",
            showarrow=True,
        )
    )
    fig.add_annotation(
        dict(
            x=47,
            y=1,
            yref="paper",
            xanchor="left",
            yanchor="top",
            text="SL S1 begins",
            showarrow=True,
        )
    )
    return fig
