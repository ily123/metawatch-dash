from typing import List, Tuple

import constructor
import dash_core_components as dcc
import dash_html_components as html
import dataserver
import figure
import plotly.graph_objects as go
from app import app
from dash.dependencies import Input, Output

DB_FILE_PATH = "data/summary.sqlite"
dataserver_ = dataserver.DataServer(DB_FILE_PATH)

CURRENT_SEASON = "SL1"
PATCH_NAMES = {
    "bfa4": "BFA Season 4 / 8.3",
    "bfa4_postpatch": "BFA post-patch / 9.0.1",
    "SL1": "SL Season 1 / 9.0.2",
}

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
            using sliders below.
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


# I don't like that figure 1 is
# taking longer to render than figure 2... It throws me off
# when figure 2 loads before figure 1.
# To solve this, let's precompute  panel 1 figures
# so they come preloaded on start up
# ridge plot and bubble plot (panel 1 and 2)
def create_figure1(season: str) -> Tuple[go.Figure]:
    """Create the 3 panels of figure 1 based on season.

    Parameters
    ----------
    season : str
        season for which to plot the figure

    Returns
    -------
    Tuple(go.Figure)
        Tuple containing the ridgeplot, bubble plot, and
        the histogram
    """
    patch_name = PATCH_NAMES[season]
    # ridge plot and bubble plot (panel 1 and 2)
    runs_per_spec_and_level = dataserver_.get_data_for_ridgeplot(season)
    ridgeplot = figure.RidgePlot(runs_per_spec_and_level, patch_name)
    bubble = figure.BubblePlot(runs_per_spec_and_level, patch_name)
    # histogram (panel 3)
    runs_per_level = dataserver_.get_data_for_run_histogram(season)
    hist = figure.BasicHistogram(runs_per_level, patch_name)
    return ridgeplot.figure, bubble.make_figure2(), hist.make_figure()


default_ridgeplot, default_bubble, default_hist = create_figure1(CURRENT_SEASON)


layout = html.Div(
    [
        html.Div(
            id="master-switch-wrapper",
            children=[
                html.H4("SELECT SEASON"),
                constructor.season_dropdown(id_="master-season-switch", ishidden=False),
            ],
        ),
        html.Div(
            className="figure-header",
            children=constructor.figure_header_ensemble(
                figure_header_elements["figure1"]
            ),
        ),
        dcc.Tabs(
            children=[
                dcc.Tab(
                    label="RUNS BY SPEC & KEY LEVEL",
                    children=[
                        constructor.season_dropdown(
                            id_="fig1-ridgeplot-season-switch",
                            ishidden=True,
                        ),
                        dcc.Graph(
                            className="figure",
                            id="fig1-ridgeplot",
                            figure=default_ridgeplot,
                            config=fig_config,
                            style={"margin-top": "20px"},
                        ),
                    ],
                ),
                dcc.Tab(
                    label="RUNS BY SPEC",
                    children=[
                        constructor.season_dropdown(
                            id_="fig1-bubble-season-switch", ishidden=True
                        ),
                        dcc.Graph(
                            className="figure",
                            id="fig1-bubble-chart",
                            figure=default_bubble,
                            config=fig_config,
                        ),
                    ],
                ),
                dcc.Tab(
                    label="RUNS BY KEY LEVEL",
                    children=[
                        constructor.season_dropdown(
                            id_="fig1-key-hist-season-switch", ishidden=True
                        ),
                        dcc.Graph(
                            className="figure",
                            id="fig1-key-hist",
                            figure=default_hist,
                            config=fig_config,
                        ),
                    ],
                ),
            ]
        ),
        html.Br(),
        html.Div(
            className="figure-header",
            children=constructor.figure_header_ensemble(
                figure_header_elements["figure2"]
            ),
        ),
        constructor.season_dropdown(id_="fig2-season-switch", ishidden=True),
        constructor.spec_dropdown(id_="figure2-dropdown"),
        dcc.Graph(
            id="keylevel-stacked-fig",
            config=fig_config,
        ),
        html.Hr(),
        html.Div(
            className="figure-header",
            children=constructor.figure_header_ensemble(
                figure_header_elements["figure3"]
            ),
        ),
        constructor.season_dropdown(id_="fig3-season-switch", ishidden=True),
        constructor.spec_dropdown(id_="figure3-dropdown"),
        dcc.Graph(id="week-stacked-fig", config=fig_config),
        html.Hr(),
        constructor.season_dropdown(id_="fig4-season-switch", ishidden=True),
        html.Div(
            className="figure-header",
            children=constructor.figure_header_ensemble(
                figure_header_elements["figure4"]
            ),
        ),
        html.P("Color specs on bar chart:"),
        constructor.spec_dropdown(id_="figure4-dropdown", include_all=True),
        html.P("Population-level keys"),
        html.Div(
            id="population-slider-wrapper",
            children=constructor.key_level_slider(
                id_="population-slider",
                range_max=dataserver_.get_max_key_for_season(season=CURRENT_SEASON),
                selected_range=[2, 15],
            ),
        ),
        html.P("Meta-level keys"),
        html.Div(
            id="meta-slider-wrapper",
            children=constructor.key_level_slider(
                id_="meta-slider",
                range_max=dataserver_.get_max_key_for_season(season=CURRENT_SEASON),
                selected_range=[16, 99],  # select it to the end
            ),
        ),
        dcc.Graph(id="meta-index-fig", config=fig_config),
        html.Br(),
    ]
)


@app.callback(
    [
        Output(component_id="fig1-ridgeplot", component_property="figure"),
        Output(component_id="fig1-bubble-chart", component_property="figure"),
        Output(component_id="fig1-key-hist", component_property="figure"),
    ],
    Input(component_id="fig1-ridgeplot-season-switch", component_property="value"),
    prevent_initial_call=True,
)
def update_figure1(season: str) -> Tuple[go.Figure]:
    """Updates the 3 panels of figure 1 based on season.

    Parameters
    ----------
    season : str
        season for which to plot the figure

    Returns
    -------
    Tuple(go.Figure)
        Tuple containing the ridgeplot, bubble plot, and
        the histogram
    """
    return create_figure1(season)


@app.callback(
    Output(component_id="keylevel-stacked-fig", component_property="figure"),
    [
        Input(component_id="figure2-dropdown", component_property="value"),
        Input(component_id="fig2-season-switch", component_property="value"),
    ],
)
def update_figure2(role, season) -> go.Figure:
    """Updates figure 2 (spec % vs key level).

    Parameters
    ----------
    role : str
        specs to include in the figure; one of {'tank', 'healer', 'mdps', 'rdps'}
    season : str
        season for which to plot the figure

    Returns
    -------
    stack_figure : go.Figure
        top 500 weekly bar chart
    """
    patch_name = PATCH_NAMES[season]
    runs_per_spec_and_level = dataserver_.get_data_for_ridgeplot(season)
    stac = figure.StackedBarChart(runs_per_spec_and_level, "key", role, patch_name)
    stack_figure = stac.assemble_figure()
    return stack_figure


@app.callback(
    Output(component_id="week-stacked-fig", component_property="figure"),
    [
        Input(component_id="figure3-dropdown", component_property="value"),
        Input(component_id="fig3-season-switch", component_property="value"),
    ],
)
def update_figure3(role: str, season: str) -> go.Figure:
    """Updates figure 3 (the top 500 weekly bar chart).

    Parameters
    ----------
    role : str
        specs to include in the figure; one of {'tank', 'healer', 'mdps', 'rdps'}
    season : str
        season for which to plot the figure

    Returns
    -------
    stack_figure : go.Fig
        top 500 weekly bar chart
    """
    runs_per_week_and_spec = dataserver_.get_data_for_weekly_chart()
    patch_name = "since BFA S4"
    stack_figure = figure.StackedBarChart(
        runs_per_week_and_spec, "week", role, patch_name
    )
    stack_figure = stack_figure.assemble_figure()
    stack_figure = constructor.annotate_weekly_figure(stack_figure)
    return stack_figure


@app.callback(
    Output(component_id="meta-index-fig", component_property="figure"),
    [
        Input(component_id="population-slider", component_property="value"),
        Input(component_id="meta-slider", component_property="value"),
        Input(component_id="figure4-dropdown", component_property="value"),
        Input(component_id="fig4-season-switch", component_property="value"),
    ],
)
def update_figure4(
    population_slider: List[int], meta_slider: List[int], spec_role: str, season: str
) -> go.Figure:
    """Updates figure 4 (the tier list).

    Parameters
    ----------
    population_slider : List[int]
        value of the population slider
    meta_slider : List[int]
        value of the meta slider
    season : str
        season for which to plot the figure
    spec_role : str
        specs to include in the figure; one of {'tank', 'healer', 'mdps', 'rdps'}

    Returns
    -------
    spec_meta_fig : go.Fig
        spec meta index / spec tier bar chart
    """
    population_min, population_max = population_slider
    meta_min, meta_max = meta_slider
    data = dataserver_.raw_data["specs"]
    fig = figure.MetaIndexBarChart(
        data=data[data["season"] == season],
        spec_role=spec_role,
    )
    spec_meta_fig = fig.create_figure(
        bounds=[population_min, population_max, meta_min, meta_max]
    )
    patch_name = PATCH_NAMES[season]
    spec_meta_fig.update_layout(title_text="<b>SPEC TIER LIST (%s)</b>" % patch_name)
    return spec_meta_fig


@app.callback(
    [
        Output(component_id="population-slider-wrapper", component_property="children"),
        Output(component_id="meta-slider-wrapper", component_property="children"),
    ],
    Input(component_id="master-season-switch", component_property="value"),
    prevent_initial_call=True,
)
def update_slider_max_range(season: str) -> Tuple[dcc.RangeSlider]:
    """Updates tier list sliders based on season selected in the master switch.

    Parameters
    ----------
    season : str
        season for which to plot the figure

    Returns
    --------
    population_slider : dcc.RangeSlider
        updated population slider
    meta_slider : dcc.RangeSlider
        updated meta slider
    """
    population_slider = constructor.key_level_slider(
        id_="population-slider",
        range_max=dataserver_.get_max_key_for_season(season=season),
        selected_range=[2, 15],  # select it to the end
    )
    meta_slider = constructor.key_level_slider(
        id_="meta-slider",
        range_max=dataserver_.get_max_key_for_season(season=season),
        selected_range=[16, 99],  # select it to the end
    )
    return population_slider, meta_slider


@app.callback(
    [
        Output(component_id="fig1-ridgeplot-season-switch", component_property="value"),
        Output(component_id="fig1-bubble-season-switch", component_property="value"),
        Output(component_id="fig1-key-hist-season-switch", component_property="value"),
        Output(component_id="fig2-season-switch", component_property="value"),
        Output(component_id="fig3-season-switch", component_property="value"),
        Output(component_id="fig4-season-switch", component_property="value"),
    ],
    Input(component_id="master-season-switch", component_property="value"),
    prevent_initial_call=True,
)
def set_season(season: str) -> List[str]:
    """Sets season values of individual figures via hidden switches.

    Parameter
    --------
    season : str
        season for which to plot the figures
    """
    return [season] * 6  # this is the number of hidden switches
