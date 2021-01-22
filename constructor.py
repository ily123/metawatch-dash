"""App helper for construction of simple HTML components."""
from typing import List

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


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


def spec_dropdown(id_, include_all=False):
    """Constructs dropdown with class role options."""
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


def role_options(include_all: bool) -> List[dict]:
    """Returns options for class selection dropdown."""
    role_options = [
        {"label": "TANK", "value": "tank"},
        {"label": "HEALER", "value": "healer"},
        {"label": "MELEE DPS", "value": "mdps"},
        {"label": "RANGE DPS", "value": "rdps"},
    ]
    if include_all:
        role_options.append({"label": "ALL SPECS", "value": "all"})
    return role_options


def page1_errata() -> dcc.Markdown:
    """Returns markdown text for page 1 errata div."""
    errata_and_faq = dcc.Markdown(  # &nbsp; is a hacky way to add a blank line to MD
        """
        #### FAQ:

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
