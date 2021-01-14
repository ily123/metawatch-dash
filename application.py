import datetime
import os
import sqlite3
import time
from typing import List, Type

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

import figure


def get_data_from_sqlite(db_file_path, season):
    """Get agg tables from the SQLite file."""
    conn = sqlite3.connect(db_file_path)
    main_query = "SELECT * FROM main_summary_seasons WHERE season='%s'" % season
    main_summary = pd.read_sql_query(main_query, conn)
    week_summary = pd.read_sql_query("SELECT * FROM weekly_summary", conn)
    conn.close()

    # pivot tables for the figure api
    main_summary = pd.pivot_table(
        main_summary,
        values="run_count",
        index=["spec"],
        columns=["level"],
        fill_value=0,
    )

    week_summary = pd.pivot_table(
        week_summary, values="run_count", index="spec", columns="period", fill_value=0
    )
    return main_summary, week_summary


def get_raw_data_from_sqlite(db_file_path):
    """Get agg tables from the SQLite file."""
    conn = sqlite3.connect(db_file_path)
    main_query = "SELECT * FROM main_summary_seasons"
    main_summary = pd.read_sql_query(main_query, conn)
    conn.close()
    return main_summary


def format_raw_data_main_summary(main_summary, season):
    """Extracts season's data and pivots it for figure API."""
    # pivot tables for the figure api
    season_mask = main_summary.season == season
    formatted_season_summary = pd.pivot_table(
        main_summary[season_mask],
        values="run_count",
        index=["spec"],
        columns=["level"],
        fill_value=0,
    )
    return formatted_season_summary


def generate_ridgeplot(data, season_patch):
    """Constructs the spec vs level ridge plot."""
    ridgeplot = figure.RidgePlot(data, season_patch)
    return ridgeplot.figure


def generate_stack_figure(data, chart_type, role, stack_type, patch):
    """Constructs stack area chart."""
    if stack_type == "area":
        stac = figure.StackedAreaChart(data, chart_type, role, patch)
    elif stack_type == "bar":
        stac = figure.StackedBarChart(data, chart_type, role, patch)
    stac_fig = stac.assemble_figure()
    return stac_fig


def generate_run_histogram(data, patch):
    """Constructs keylevel vs run count histogram."""
    data = data.sum(axis=0)
    data = round(data / 5)  # there are 5 records per run
    data = data.astype(int)
    hist = figure.BasicHistogram(data, patch)
    histfig = hist.make_figure()
    return histfig


def make_bubble_plot(data, patch):
    """Construct spec run count bubble chart."""
    bubble = figure.BubblePlot(data, patch)
    bubble_fig = bubble.make_figure2()
    return bubble_fig


def generate_meta_index_barchart(
    data: pd.DataFrame, patch: str, boundary: List[int]
) -> Type["go.Figure"]:
    """Creates meta bar chart."""
    print(data)
    fig = figure.MetaIndexBarChart(data.loc[data.season == "SL1", :], spec_role="melee")
    spec_meta_fig = fig.create_figure(boundary)
    return spec_meta_fig


# generate default figures
db_file_path = "data/summary.sqlite"

CURRENT_SEASON = "SL1"
main_summary, week_summary = get_data_from_sqlite(db_file_path, CURRENT_SEASON)

RAW_AGG_DATA = get_raw_data_from_sqlite(db_file_path)
spec_runs = format_raw_data_main_summary(RAW_AGG_DATA, season=CURRENT_SEASON)
print(spec_runs)


PATCH_NAMES = {
    "bfa4": "BFA Season 4 / 8.3",
    "bfa4_postpatch": "BFA post-patch / 9.0.1",
    "SL1": "SL Season 1 / 9.0.2",
}
ridgeplot_fig = generate_ridgeplot(spec_runs, PATCH_NAMES[CURRENT_SEASON])
bubble_fig = make_bubble_plot(spec_runs, PATCH_NAMES[CURRENT_SEASON])
histogram_fig = generate_run_histogram(spec_runs, PATCH_NAMES[CURRENT_SEASON])
stacked_levels_fig = generate_stack_figure(
    spec_runs, "key", "mdps", "bar", PATCH_NAMES[CURRENT_SEASON]
)
stacked_week_fig = generate_stack_figure(
    week_summary, "week", "mdps", "bar", PATCH_NAMES[CURRENT_SEASON]
)
meta_barchart = generate_meta_index_barchart(
    RAW_AGG_DATA, CURRENT_SEASON, boundary=[0, 14, 15, 30]
)


data_last_updated = datetime.datetime.fromtimestamp(
    int(os.path.getmtime(db_file_path))
).strftime("%Y-%m-%d")

figure_list = html.Ul(
    children=[
        html.Li(html.A("Overview of all keys completed this season", href="#figure1")),
        html.Li(html.A("Detailed Look at Spec Performance", href="#figure2")),
        html.Li(html.A("Weekly top 500", href="#figure3")),
        html.Li(html.A("Spec Tier list", href="#figure4")),
        html.Li(html.A("FAQ", href="#faq")),
    ]
)

role_options = [
    {"label": "TANK", "value": "tank"},
    {"label": "HEALER", "value": "healer"},
    {"label": "MELEE DPS", "value": "mdps"},
    {"label": "RANGE DPS", "value": "rdps"},
]

radio_options = [
    {"label": "Bar Chart", "value": "bar"},
    {"label": "Area Chart", "value": "area"},
]

scratch = """

    **What each panel shows**:

    * Panel 1 gives you a quick birds-eye view at which specs are the most numerous,
    and which spec have the longest tails. (In technical parlance, Panel 1 is a
    'ridge plot'. It shows a histogram for each spec. Each histogram tells you how many
    runs (y axis) that spec has completed at a particular key level (x axis). Mouse over
    the ridge to see exact numbers!
    * Panel 2 is supplementary to panel 1, and gives a comparison of specs population
    regardless of key level. It's another way to look at total spec populations.
    * Panel 3 is also supplementary. It shows what is already apparent from Panel 1.
    """


# html.H4(children=),
# html.Div(figure1_explanation),
def construct_figure_header(elements):
    """Constructs premade text elements that preceed figure."""
    children = [
        html.A(id=elements["anchor_id"]),
        html.H4(elements["header_title"].upper()),
        dcc.Markdown(elements["summary"]),
        html.Details(
            children=[html.Summary("Key Insights"), dcc.Markdown(elements["insight"])]
        ),
    ]
    if "factoid" in elements:
        children.append(
            html.Details(
                children=[
                    html.Summary("Interesting Factoid"),
                    dcc.Markdown(elements["factoid"]),
                ]
            )
        )
    return children


def construct_season_selector(id_, ishidden):
    """Constructs dropdown season select menu."""
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
        value="SL1",
        clearable=False,
        style={"width": "50%"},
    )
    if ishidden:
        dropdown.style = {"display": "none"}
    return dropdown


figure_header_elements = {
    "figure1": dict(
        anchor_id="figure1",
        header_title="Overview of all keys completed this season",
        summary="""
            To get a high-level view of the entire M+ activity,
            we count all keys completed this season. Then, we break that number down
            by spec & key level (first panel), by spec alone (second panel),
            or just by key level (third panel).
            """,
        insight="""
            * Most specs are within 2-3 key levels of the cutting edge performers.
            * Most specs that are popular with the general population
            are also the cutting-edge meta specs. It's likely that
            top-end meta propagates itself down to the population level.
            * The bottom few specs are also the esoteric specs not widely played
            in the population (eg: feral, frost, survival).
            * The takeaway for ordinary players is that you should stay
            away from the very bottom specs, but feel free to play anything else.
            """,
        factoid="""
            * Once you get past the "best chest reward" level of keys,
            the number of key runs decays exponentially. Every two key levels,
            the number of runs drops by ~50%. Groups that are considered pedenstrian
            by high-end standards, are probably within the top 2-3% of the population!
            Check panel 3 for the exact key level percentiles.
            * One way to tell if a spec is dead is to compare the number of runs
            it has at key level +2 vs the chest reward level. If there are more runs
            at +2 than at chest reward level, it means that the spec is not played
            in the end game. The buttom specs are often like that.
            """,
    ),
    "figure2": dict(
        anchor_id="figure2",
        header_title="Detailed Look at Spec Performance",
        summary="""
            The number of runs in the high-end bracket is so low,
            that in figure 1 it's hard to see the difference between counts
            once you get into high-level keys. To solve this problem, we normalize counts
            within each key bracket, and show spec popularity in terms of percent.

            Hint: Click on the spec names in the legend to add/remove them from the
            figure. Double click on the name to show the spec alone.
            """,
        insight="""
            * The meta starts kicking in once rewards are no longer relevant (i.e. once
            you pass the level needed for the weekly chest reward). That's where casual
            players stop playing, and dedicated pushers (and the meta classes they play)
            take over the population.
            * Some non-meta specs stay relatively stable (or even gain share)
            in mid-range keys. Go through each spec one at a time to identify them.
            Play these specs if you want to feel special, yet somewhat competitive :)
            """,
    ),
    "figure3": dict(
        anchor_id="figure3",
        header_title="WEEKLY TOP 500",
        summary="""
            To see how the meta changes through the season, we sample the top 500 runs
            _from each_ dungeon for every week. We then count the
            number of times each spec appears in top 500 sample.

            Hint: Click on the spec names in the legend to add/remove them from the
            figure.
            """,
        insight="""
            * The meta is very stable within a single patch. Spec representation within
            top 500 rarely changes.
            * When changes do happen, it's usually between patches, due to major
            buff/nerfs. They are very easy to see on the graph.
            """,
        factoid="""
            * If you notice, the data has a zig-zag quality to it.
            Spec numbers, especially the meta specs, go up and down each week.
            That's the effect of the Tyrannical/Fort split.
            On Tyrannical weeks, top pushers are likely to bench their meta-class mains
            and play non-meta alts (or not play at all).
            As a result on Tyrannical weeks, the share of the meta specs in the top 500
            drops.
            * The same logic applies to between-expansion x.0.1 patches. During these
            patches people just play whatever they want, and the top 500 sample
            looks similar to the population.
            """,
    ),
    "figure4": dict(
        anchor_id="figure4",
        header_title="SPEC TIER LIST",
        summary="""
            To rank specs, we use the Meta Ratio score. The "ratio" is between the spec's
            representation in the meta vs its representation in the population.
            For example, let's say a spec makes up 3% of all players in the population,
            but 6% in the meta. That spec's ratio is 6% / 3% = 2, i.e. that spec is
            overrepresented in the meta by a factor of 2.

            At this point in SL season 1, I define the "population" as all keys level
            2 to 15, and the "meta" as all keys 16 and above. You can adjust these
            using dropdowns below.
            """,
        insight="""
            We can break down specs into tiers based on their ratio. I do it as
            follows:

            * S-tier: ratio of at least 1.5
            * A-tier: ratio between 1 and 1.5
            * B-tier: ratio between 0.5 and 1
            * C-tier: ratio below 0.5, but greater than 0
            * F-tier: ratio of 0 (the spec is not present in the high-level bin at all)
            """,
    ),
}

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

    -----
    This website does not use cookies or sell your data.
    """
)


# removes non-essential buttons from the figure mode bar
fig_config = dict(
    modeBarButtonsToRemove=[
        "zoomIn2d",
        "zoomOut2d",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "toggleSpikelines",
        "autoScale2d",
        "lasso2d",
        "select2d",
    ],
    displaylogo=False,
)
app = dash.Dash(__name__)
application = app.server
app.title = "Benched: Mythic+ at a glance"
app.layout = html.Div(
    html.Div(
        id="wrapper",
        children=[
            html.H1(children="Benched :: Mythic+ at a glance"),
            figure_list,
            html.P(
                "Data updated: %s" % data_last_updated,
                style={"text-align": "right"},
            ),
            html.Div(
                children=[
                    html.Div(
                        dcc.Markdown(
                            "#### SELECT SEASON",
                            #       style={
                            #           "color": "red",
                            #           "display": "flex",
                            #           "justify-content": "center",
                            #       },
                        ),
                        style={"float": "left", "margin-right": "10px"},
                    ),
                    html.Div(
                        construct_season_selector(
                            id_="master-season-switch", ishidden=False
                        ),
                        style={"float": "right", "margin-top": "15px"},
                    ),
                ],
                style={"display": "inline-block"},
            ),
            html.Hr(),
            html.Div(
                className="figure-header",
                children=construct_figure_header(figure_header_elements["figure1"]),
            ),
            dcc.Tabs(
                children=[
                    dcc.Tab(
                        label="RUNS BY SPEC & KEY LEVEL",
                        children=[
                            construct_season_selector(
                                id_="fig1-ridgeplot-season-switch", ishidden=True
                            ),
                            dcc.Graph(
                                className="figure",
                                id="fig1-ridgeplot",
                                figure=ridgeplot_fig,
                                config=fig_config,
                                # add margin here to compensate for title squish
                                style={"margin-top": "20px"},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="RUNS BY SPEC",
                        children=[
                            construct_season_selector(
                                id_="fig1-bubble-season-switch", ishidden=True
                            ),
                            dcc.Graph(
                                className="figure",
                                id="fig1-bubble-chart",
                                figure=bubble_fig,
                                config=fig_config,
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="RUNS BY KEY LEVEL",
                        children=[
                            construct_season_selector(
                                id_="fig1-key-hist-season-switch", ishidden=True
                            ),
                            dcc.Graph(
                                className="figure",
                                id="fig1-key-hist",
                                figure=histogram_fig,
                                config=fig_config,
                            ),
                        ],
                    ),
                ]
            ),
            html.Hr(),
            html.Div(
                className="figure-header",
                children=construct_figure_header(figure_header_elements["figure2"]),
            ),
            construct_season_selector(id_="fig2-season-switch", ishidden=True),
            dcc.RadioItems(
                id="figure2-radio",
                options=radio_options,
                value="bar",
            ),
            dcc.Dropdown(
                className="dropdown",
                id="figure2-dropdown",
                options=role_options,
                value="tank",
                clearable=False,
            ),
            dcc.Graph(
                id="keylevel-stacked-fig", figure=stacked_levels_fig, config=fig_config
            ),
            html.Hr(),
            html.Div(
                className="figure-header",
                children=construct_figure_header(figure_header_elements["figure3"]),
            ),
            construct_season_selector(id_="fig3-season-switch", ishidden=True),
            dcc.RadioItems(
                id="figure3-radio",
                options=radio_options,
                value="bar",
            ),
            dcc.Dropdown(
                className="dropdown",
                id="figure3-dropdown",
                options=role_options,
                placeholder="SELECT SPEC ROLE",
                value="tank",
                clearable=False,
            ),
            dcc.Graph(
                id="week-stacked-fig", figure=stacked_week_fig, config=fig_config
            ),
            html.Hr(),
            construct_season_selector(id_="fig4-season-switch", ishidden=True),
            html.Div(
                className="figure-header",
                children=construct_figure_header(figure_header_elements["figure4"]),
            ),
            dcc.Dropdown(
                className="dropdown",
                id="figure4-dropdown",
                options=role_options,
                placeholder="SELECT SPEC ROLE",
                value="tank",
                clearable=False,
            ),
            dcc.RangeSlider(
                id="population-slider",
                min=2,
                max=RAW_AGG_DATA.level.max(),
                step=None,
                marks=dict(
                    zip(
                        range(2, RAW_AGG_DATA.level.max() + 1),
                        [str(i) for i in range(2, RAW_AGG_DATA.level.max() + 1)],
                    )
                ),
                value=[2, 15],
            ),
            dcc.RangeSlider(
                id="meta-slider",
                min=2,
                max=RAW_AGG_DATA.level.max(),
                step=None,
                marks=dict(
                    zip(
                        range(2, RAW_AGG_DATA.level.max() + 1),
                        [str(i) for i in range(2, RAW_AGG_DATA.level.max() + 1)],
                    )
                ),
                value=[16, RAW_AGG_DATA.level.max()],
            ),
            dcc.Graph(id="meta-index-fig", figure=meta_barchart, config=fig_config),
            html.Hr(),
            html.Div(id="faq", children=errata_and_faq),
        ],
    )
)


@app.callback(
    Output(component_id="meta-index-fig", component_property="figure"),
    [
        Input(component_id="population-slider", component_property="value"),
        Input(component_id="meta-slider", component_property="value"),
        Input(component_id="fig4-season-switch", component_property="value"),
    ],
    prevent_initial_call=True,
)
def update_figure4(population_slider: List[int], meta_slider: List[int], season: str):
    """Updates tier list figure based on slider values."""
    print(population_slider)
    population_min, population_max = population_slider
    meta_min, meta_max = meta_slider
    meta_barchart = generate_meta_index_barchart(
        RAW_AGG_DATA,
        season,
        boundary=[population_min, population_max, meta_min, meta_max],
    )
    print(population_min)
    return meta_barchart


@app.callback(
    [
        Output(component_id="fig1-ridgeplot", component_property="figure"),
        Output(component_id="fig1-bubble-chart", component_property="figure"),
        Output(component_id="fig1-key-hist", component_property="figure"),
    ],
    Input(component_id="master-season-switch", component_property="value"),
    prevent_initial_call=True,
)
def update_figure1(season):
    """Updates 3 panels of figure 1 based on season."""
    spec_runs = format_raw_data_main_summary(RAW_AGG_DATA, season=season)
    patch_name = PATCH_NAMES[season]
    ridgeplot = generate_ridgeplot(spec_runs, patch_name)
    bubble_chart = make_bubble_plot(spec_runs, patch_name)
    histogram = generate_run_histogram(spec_runs, patch_name)
    # stacked_levels = generate_stack_figure(spec_runs, "key", "mdps", "bar")
    return [ridgeplot, bubble_chart, histogram]


@app.callback(
    Output(component_id="keylevel-stacked-fig", component_property="figure"),
    [
        Input(component_id="figure2-dropdown", component_property="value"),
        Input(component_id="figure2-radio", component_property="value"),
        Input(component_id="fig2-season-switch", component_property="value"),
    ],
)
def update_figure2(role, isbar, season):
    """Switch between sorted by key and sorted by population view."""
    spec_runs = format_raw_data_main_summary(RAW_AGG_DATA, season=season)
    patch_name = PATCH_NAMES[season]
    stack_figure = generate_stack_figure(
        data=spec_runs, chart_type="key", role=role, stack_type=isbar, patch=patch_name
    )
    return stack_figure


@app.callback(
    Output(component_id="week-stacked-fig", component_property="figure"),
    [
        Input(component_id="figure3-dropdown", component_property="value"),
        Input(component_id="figure3-radio", component_property="value"),
        Input(component_id="fig3-season-switch", component_property="value"),
    ],
)
def update_figure3(role, isbar, season):
    """Switch between sorted by key and sorted by population view."""
    stack_figure = generate_stack_figure(
        data=week_summary,
        chart_type="week",
        role=role,
        stack_type=isbar,
        patch="since BFA S4",
    )
    # add timeline labels
    stack_figure.add_annotation(
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
    stack_figure.add_annotation(
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
    stack_figure.add_annotation(
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
    return stack_figure


# this is a very hacky way to add tracking, see this instead:
# https://community.plotly.com/t/how-to-add-javascript-code-from-adsense-into-dash-app/5370/6
app.index_string = """<!DOCTYPE html>
    <html>
    <head>
      <!-- Plausible.io tracking script -->
      <script async defer data-domain="benched.me" src="https://plausible.io/js/plausible.js"></script>
      <!-- End Plausible.io tracking script -->
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    </head>
    <body>
    {%app_entry%}
    <footer>
    {%config%}
    {%scripts%}
    {%renderer%}
    </footer>
    </body>
    </html>
    """

if __name__ == "__main__":
    application.run(debug=True, port=8080)
