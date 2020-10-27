import datetime
import os
import sqlite3
import time

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

    # oops, forgot to sum by dungeon before piping to SQLite, do it now:
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


# current season
season = "bfa4_postpatch"
# generate the figures
db_file_path = "data/summary.sqlite"
main_summary, week_summary = get_data_from_sqlite(db_file_path, season)

RAW_AGG_DATA = get_raw_data_from_sqlite(db_file_path)
CURRENT_SEASON = "bfa4_postpatch"
spec_runs = format_raw_data_main_summary(RAW_AGG_DATA, season=CURRENT_SEASON)

PATCH_NAMES = {
    "bfa4": "BFA Season 4 / 8.3",
    "bfa4_postpatch": "BFA post-patch / 9.0.1",
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

DATA_LAST_UPDATED = datetime.datetime.fromtimestamp(
    int(os.path.getmtime(db_file_path))
).strftime("%Y-%m-%d %H:%M:%S")

figure_list = html.Ul(
    children=[
        html.Li(html.A("Overview of all keys completed this season", href="#figure1")),
        html.Li(html.A("Detailed Look at Spec Performance", href="#figure2")),
        html.Li(html.A("Weekly top 500", href="#figure3")),
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
        ],
        value="bfa4_postpatch",
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

            The first panel tells you how many runs each spec recorded
            at each key level.
            This tells you two things: how popular each spec is (the
            size of the colored area corresponds to the total number of runs each
            spec recorded this season),
            and which specs are most successful at high-end pushing
            (those are the specs with the longest tails in the 20+ range).

            The second panel gives you a
            clearer look at the total number of runs by each spec, while the third
            panel is a spec-agnostic look at runs broken down by key level.
            """,
        insight="""
            * Most specs are within 2-3 key levels of the cutting edge performers.
            Even the worst spec has done a +25.
            * Most specs that are popular with the general population
            are also the cutting-edge meta specs. It's likely that
            top-end meta propagates itself down to +15 level.
            * The bottom 4 to 6 specs are not played at
            any level of keystone. One exception are the Holy priests. They don't
            perform well at high-end keys, but are popular with the general population.
            I assume H priests are popular with the more casual players who just want
            a no-hassle heroic raid healer.
            * The takeaway for ordinary players is that you should stay
            away from the very bottom specs, but feel free to play anything else.
            """,
        factoid="""
            * Once you get past +15, the number of key runs decays exponentially.
            Every two key levels, the number of runs drops by ~50%.
            So if you are doing +20 keys, you are already in the top 3%
            of the population.
            * One way to tell if a spec is truly dead is to compare the number of runs
            it has at key level +15 vs +2. If there are more runs at +2 than at +15,
            it means that the spec is only played by newbie characters.
            Once these characters get to weekly +15s, they switch specs.
            Most of the bottom 4-6 specs are like that. Meanwhile,
            there are low-population specs that do see more play at +15 than
            at +2 (eg: feral druid, frost dk, demo lock). These are specs that are
            played at end-game, even if not at cutting edge.
            """,
    ),
    "figure2": dict(
        anchor_id="figure2",
        header_title="Detailed Look at Spec Performance",
        summary="""
            The number of runs in the high-end bracket is so low,
            that in figure 1 it's hard to see the difference between counts
            once you get past +20. To solve this problem, we normalize counts
            within each key bracket, and show spec popularity in terms of percent.

            Hint: Click on the spec names in the legend to add/remove them from the
            figure.
            """,
        insight="""
            * The meta starts kicking in at +16. That's where most specs begin to
            lose their share of representation to the meta classes.
            * Some non-meta specs stay relatively stable (or even gain share)
            in mid-range keys (disc, brew, shadow, arms), and only begin disappearing
            at higher levels.
            Play these if you want to feel special, yet somewhat competitive :)
            """,
    ),
    "figure3": dict(
        anchor_id="figure3",
        header_title="WEEKLY TOP 500",
        summary="""
            To see how the meta changes through the season, we sample the top 500 runs
            for each dungeon (that's 6000 total keys) for each week. We then count the
            number of times each spec appears in this weekly top 500 sample.

            Hint: Click on the spec names in the legend to add/remove them from the
            figure.
            """,
        insight="""
            * The meta is very stable within a single patch. Spec representation within
            top 500 rarely changes.
            * You do see *some* meta changes.
            Two examples this patch are the Balance Druids and Brewmaster Monks. Both
            started out this season strong, but faded away as time went by. These specs
            were popular in S3 for dealing with Beguiling, so there was carry-over at
            the start of S4 (additionally, monks were the default tanks for raid prog
            which probably boosted their repsentation in keys early this season).
            However, Balance was adjusted out of the meta completely by mid-season, and
            BrM fell from ~25% to ~10%.
            """,
        factoid="""
            If you notice, the data has a zig-zag quality to it.
            Spec numbers, especially the top spec, go up and down each week.
            That's the effect of the Tyrannical/Fort split.
            On Tyrannical weeks, top pushers are likely to bench their meta-class mains
            and play non-meta alts (or not play at all).
            As a result on Tyrannical weeks, the share of the meta specs in the top 500
            drops.
            Likewise, the share of meta specs rises to its max during push weeks
            (week 27 and 29 were the back to back push fort weeks, for example).

            Additionally, as we get closer to the end of the patch, many pushers
            stop playing, so we see non-meta specs gain share past week 30.
            """,
    ),
}

errata_and_faq = dcc.Markdown(  # &nbsp; is a hacky way to add a blank line to MD
    """
    #### FAQ:

    **In your top figure why are you using completed key,
    instead of timed key, for BEST KEY?**

    It's not intended. I will add a timed/completed toggle in the future releases.

    &nbsp;

    **How frequently are the data updated?**

    The data are updated daily.

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
    This website does not use cookies or sell your data to Google.
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
                "Data updated: %s US CST" % DATA_LAST_UPDATED,
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
            html.Div(id="faq", children=errata_and_faq),
        ],
    )
)


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
    if season == "bfa4" or season == "bfa4_postpatch":
        patch_name = "BFA S4 & Post-patch"
    else:
        patch_name = PATCH_NAMES[season]
    stack_figure = generate_stack_figure(
        data=week_summary,
        chart_type="week",
        role=role,
        stack_type=isbar,
        patch=patch_name,
    )
    # add "post-patch" label to last week
    # this will need to be fixed in SL main release!
    if season == "bfa4" or season == "bfa4_postpatch":  # same if statements! fix
        stack_figure.add_annotation(
            dict(
                x=39,
                y=1,
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Post-patch begins (week 39)",
                showarrow=True,
            )
        )
    return stack_figure


@app.callback(
    [
        Output(component_id="fig1-ridgeplot-season-switch", component_property="value"),
        Output(component_id="fig1-bubble-season-switch", component_property="value"),
        Output(component_id="fig1-key-hist-season-switch", component_property="value"),
        Output(component_id="fig2-season-switch", component_property="value"),
        Output(component_id="fig3-season-switch", component_property="value"),
    ],
    Input(component_id="master-season-switch", component_property="value"),
    prevent_initial_call=True,
)
def set_data(season):
    """Change data var inside DATA_CONTAINER."""
    return [season] * 5


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
