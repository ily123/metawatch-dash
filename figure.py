"""
Draws interactive ridge plot for key run distribution.

    Example use:

    ridgeplot = figure.RidgePlot(data)
    fig = ridgeplot.figure

Data is a pandas df formatted as:
    columns are [key level]s
    rows are [spec]s
    cells are number of runs at [key level] for [spec]
"""

import importlib
from typing import Tuple, Type  # you have to import Type

import pandas as pd
import plotly.graph_objects as go

import blizzcolors


class RidgePlot:
    """Draws the ridge plot."""

    def __init__(self, data, patch):
        """Inits with the formatted pandas dataframe.

        Params
        ------
        data : DataFrame
            spec should be the row, and level of key the columns
        """
        self.patch = patch
        self.data = data  # the table should already be pivoted
        self.summary = self._get_summary_table(data)
        sorted_summary = self._sort_summary(sort_by="best_key")

        self.traces = self._construct_traces(sorted_summary)
        self.annotations = self._construct_annotations(sorted_summary)
        self.buttons = self._construct_buttons()
        self.figure = self._assemble_components()

    def _get_summary_table(self, data):
        """Computes total population and best key for each spec."""
        summary = pd.DataFrame(data.index)
        summary["total_run"] = data.sum(axis=1).values
        summary["best_key"] = data.apply(
            lambda x: self._find_highest_key(x), axis=1
        ).values
        return summary

    @staticmethod
    def _find_highest_key(row):
        """Finds index of the last non-zero int in list."""
        highest_key_index = None
        for bin_, num_keys_in_bin in enumerate(row):
            if num_keys_in_bin != 0:
                highest_key_index = bin_
        highest_key_level = highest_key_index + 2  # key level starts with 2
        return highest_key_level

    def _sort_summary(self, sort_by="best_key"):
        """Sorts summary by the given column."""
        if sort_by not in ["best_key", "total_run"]:
            raise ValueError(
                (
                    "Data can be sorted either by best_key"
                    "or by total_run number of runs"
                )
            )
        sort_order = ["best_key", "total_run"]
        if sort_by == "total_run":
            sort_order = sort_order[::-1]
        sorted_summary = self.summary.sort_values(by=sort_order, ascending=False)
        return sorted_summary

    def _calculate_vertical_offset(self):
        """Calculates size of vertical gap between traces."""
        # let's make the gap be as wide as median # of keys at +15 level
        gap = self.data.max(axis=1).median()
        return gap

    def _construct_traces(self, sorted_summary):
        """Makes line/fill traces of the data distribution."""
        key_levels = list(self.data)
        key_levels_x = [i - 2 for i in list(key_levels)]  # x =0, key - 2
        vertical_offset = self._calculate_vertical_offset()
        num_specs = len(self.summary)
        specs = blizzcolors.Specs()
        traces = {}
        for index, row in enumerate(list(sorted_summary.values)):
            spec_id = row[0]
            spec_color = "rgba(%d,%d,%d,0.9)" % specs.get_color(spec_id)
            runs = self.data.loc[self.data.index == spec_id].values[0]
            # horizontal baseline for each ridge distribution
            baseline_y = vertical_offset * (num_specs - index)
            baseline = go.Scatter(
                x=key_levels_x,
                y=[baseline_y] * len(key_levels_x),
                line=dict(width=0.5, color="black"),
                hoverinfo="skip",
            )
            # the distribution of runs vs key level (the star of the show)
            ridge = go.Scatter(
                x=key_levels_x,
                y=[baseline_y + run for run in runs],
                fill="tozerox",
                fillcolor=spec_color,
                line=dict(width=1, color="black", shape="spline"),
                name=specs.get_spec_name(spec_id).upper(),
                text=[f"{y:,}" for y in runs],
                customdata=[i + 2 for i in key_levels_x],
                hovertemplate="KEY LEVEL: +%{customdata}<br>RUNS: %{text}",
            )
            traces[spec_id] = {"ridge": ridge, "baseline": baseline}
        return traces

    def _get_ridge_recolor_pattern(self, keep_role):
        """Generates color list that informs recolor of the traces.

        Given a spec role, recolors all traces not of that role to gray.

        Parameters
        ----------
        keep_role : str
            spec role ('tank', 'healer', 'mdps', 'rdps')

        Returns
        -------
        recolor : list
            list of colors, where color at index i corresponds to trace at
            index i in fig.data
        """
        valid_roles = ["tank", "healer", "mdps", "rdps"]
        keep_role = keep_role.lower()
        if keep_role not in valid_roles:
            raise ValueError("Spec role invalid. Must be one of: %s")
        recolor = []
        specs = blizzcolors.Specs()
        custom_gray = "rgba(0,0,0,0.3)"
        for spec_id, spec_traces in self.traces.items():
            spec_role = specs.get_role(spec_id)
            # reassign color based on spec role
            new_ridge_color = None
            if spec_role == keep_role:
                new_ridge_color = spec_traces["ridge"].fillcolor
            else:
                new_ridge_color = custom_gray
            # keep baseline the original color
            baseline_color = spec_traces["baseline"].line.color
            recolor.append(new_ridge_color)
            recolor.append(baseline_color)
        return recolor

    def _get_all_traces(self):
        """Extracts raw trace objects from trace dict."""
        trace_list = []
        for traces in self.traces.values():
            trace_list.append(traces["ridge"])
            trace_list.append(traces["baseline"])
        return trace_list

    def _construct_annotations(self, sorted_summary):
        """Constructs annotations."""
        annotations = {}
        # spec name placed left of its ridge plot
        annotations["spec_name"] = self._make_spec_name_annos(sorted_summary)
        # best key completed by spec text, placed on top of the ridge plot
        annotations["spec_best_key"] = self._make_spec_best_key_annos(sorted_summary)
        # annotation next to the button row, the label
        annotations["button_label"] = self._make_role_selector_button_text_label()
        # legend element that says "BEST KEY"
        annotations["legend_best_key"] = self._make_best_key_pointer_anno()

        return annotations

    def _make_spec_name_annos(self, sorted_summary):
        """Make spec name annotations."""
        annotations = {}
        vertical_offset = self._calculate_vertical_offset()
        num_specs = len(sorted_summary)
        specs = blizzcolors.Specs()
        for index, row in enumerate(list(sorted_summary.values)):
            spec_id = row[0]
            spec_name = specs.get_spec_name(spec_id).upper()
            baseline_y = vertical_offset * (num_specs - index)
            anno = self._make_spec_name_annotation(
                position_x=0, position_y=baseline_y, text=spec_name
            )
            annotations[spec_id] = anno
        return annotations

    @staticmethod
    def _make_spec_name_annotation(position_x, position_y, text):
        """Creates spec name annotation at position (x, y)."""
        annotation = dict(
            x=position_x,
            y=position_y,
            text=text,
            font=dict(color="black", size=15, family="Monaco, regular"),
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            borderpad=0,
        )
        return annotation

    def _make_spec_best_key_annos(self, sorted_summary):
        """Make best key annotations for each spec."""
        annotations = {}
        vertical_offset = self._calculate_vertical_offset()
        num_specs = len(sorted_summary)
        for index, row in enumerate(list(sorted_summary.values)):
            spec_id, _, best_key_level = row
            baseline_y = vertical_offset * (num_specs - index)
            anno = self._make_spec_best_key_annotation(
                position_x=best_key_level - 2,
                position_y=baseline_y,
                text="+%d " % best_key_level,
            )
            annotations[spec_id] = anno
        return annotations

    @staticmethod
    def _make_spec_best_key_annotation(position_x, position_y, text):
        """Creates text annotation of each spec's best key."""
        annotation = dict(
            x=position_x,
            y=position_y,
            text=text,
            font=dict(color="black", size=15, family="Monaco, regular"),
            align="center",
            showarrow=True,
            ax=0,
            ay=-15,
            arrowsize=2,
            arrowwidth=1,
            arrowhead=6,
            arrowcolor="gray",
        )
        return annotation

    def _make_best_key_pointer_anno(self):
        """Makes BEST KEY label + arrow that points to the best key."""
        annotation = dict(
            x=self.summary.best_key.max() - 2,
            y=self._calculate_vertical_offset() * (36 + 1.5),
            align="center",
            showarrow=True,
            ax=0,
            ay=-20,
            arrowsize=2,
            arrowwidth=1,
            arrowhead=6,
            # arrowcolor = 'rgba(0,0,0,0.75)'
            arrowcolor="gray",
            text="BEST<br>KEY",
        )
        return annotation

    def _keep_annotations(self, keep_role):
        """Returns annotation list based on spec role."""
        # these are then assigned to specific role-selector buttons
        keep_role = keep_role.lower()
        keep_annotations = []
        always_keep = [
            self.annotations["button_label"],
            self.annotations["legend_best_key"],
        ]
        keep_annotations.extend(always_keep)
        if keep_role == "all":
            keep_annotations.extend(self.annotations["spec_best_key"].values())
            keep_annotations.extend(self.annotations["spec_name"].values())
        else:
            names = self._sort_annos_by_spec(self.annotations["spec_name"], keep_role)
            best_keys = self._sort_annos_by_spec(
                self.annotations["spec_best_key"], keep_role
            )
            keep_annotations.extend(names)
            keep_annotations.extend(best_keys)
        return keep_annotations

    @staticmethod
    def _sort_annos_by_spec(annotations, keep_role):
        """Given a dictionary of annotations, return those that match role."""
        valid_roles = ["tank", "healer", "mdps", "rdps"]
        specs = blizzcolors.Specs()
        if keep_role not in valid_roles:
            raise ValueError("Spec role invalid. Must be one of: %s")
        keep_annotations = []
        for spec_id, annotation in annotations.items():
            spec_role = specs.get_role(spec_id)
            if spec_role == keep_role:
                keep_annotations.append(annotation)
        return keep_annotations

    def _construct_buttons(self):
        """Creates buttons that change colors and annos based on spec role."""
        role_selector = self._make_role_selector_buttons()
        # clear_button = self.make_annotation_button()
        # return [role_selector, clear_button]
        return [role_selector]

    def _make_clear_button(self):
        """Creates buttoni that clears best key annotations."""
        anno_display = dict(
            type="buttons",
            xanchor="right",
            x=1,
            y=1.05,
            buttons=[
                dict(
                    args=[{"annotations": self._keep_annotations("all")}],
                    label="CLEAR BEST KEY",
                    method="relayout",
                )
            ],
            showactive=False,
        )
        return anno_display

    def _make_role_selector_buttons(self):
        """Creates row of bottons that recolor plot based on spec role."""
        default_colors = self._get_default_colors()
        buttons = [
            dict(
                args=[
                    {"fillcolor": default_colors},
                    {"annotations": self._keep_annotations("all")},
                ],
                label="ALL",
                method="update",
            ),
            dict(
                args=[
                    {"fillcolor": self._get_ridge_recolor_pattern("tank")},
                    {"annotations": self._keep_annotations("tank")},
                ],
                label="TANK",
                method="update",
            ),
            dict(
                args=[
                    {"fillcolor": self._get_ridge_recolor_pattern("healer")},
                    {"annotations": self._keep_annotations("healer")},
                ],
                label="HEALER",
                method="update",
            ),
            dict(
                args=[
                    {"fillcolor": self._get_ridge_recolor_pattern("mdps")},
                    {"annotations": self._keep_annotations("mdps")},
                ],
                label="MELEE",
                method="update",
            ),
            dict(
                args=[
                    {"fillcolor": self._get_ridge_recolor_pattern("rdps")},
                    {"annotations": self._keep_annotations("rdps")},
                ],
                label="RANGE",
                method="update",
            ),
        ]
        role_selector = dict(
            type="buttons",
            direction="left",
            xanchor="left",
            x=0.07,
            y=1.045,
            buttons=buttons,
        )
        return role_selector

    @staticmethod
    def _make_role_selector_button_text_label():
        """Creates a text label for the botton row."""
        annotation = dict(
            x=0, y=1.04, xref="paper", yref="paper", text="SPECS:", showarrow=False
        )
        return annotation

    def _get_default_colors(self):
        """Extracts colors from traces."""
        default_colors = []
        for spec_traces in self.traces.values():
            default_colors.append(spec_traces["ridge"].fillcolor)
            default_colors.append(spec_traces["baseline"].line.color)
        return default_colors

    def _get_all_annotations(self):
        """Returns all annotations that figure shows by default."""
        return self.annotations.values()

    def _assemble_components(self) -> Type[go.Figure]:
        """Assembles traces, annotations, and buttons into a plotly figure."""
        fig = go.Figure(data=self._get_all_traces())
        fig.update_layout(width=900, height=1500, showlegend=False)
        fig.update_layout(updatemenus=self.buttons)
        fig.update_layout(annotations=self._keep_annotations("all"))
        max_x = self.summary.best_key.max()
        xaxis = dict(
            title="<b>KEY LEVEL</b>",
            range=[-6, max_x - 1],
            tickvals=[0] + list(range(3, max_x - 1, 5)),
            ticktext=["+2"] + ["+" + str(i + 2) for i in range(3, max_x - 1, 5)],
        )

        xaxis2 = dict(
            range=[-6, max_x - 1],
            tickvals=[0] + list(range(3, max_x - 1, 5)),
            ticktext=["+2"] + ["+" + str(i + 2) for i in range(3, max_x - 1, 5)],
            side="top",
            overlaying="x",
        )

        bin_ymax = self.data.to_numpy().max()  # tallest spec/key bin
        ymax = 36 * self._calculate_vertical_offset() + bin_ymax + (bin_ymax * 0.1)
        yaxis = go.layout.YAxis(range=[0, ymax], tickvals=[])
        fig.update_layout(yaxis=yaxis)
        fig.update_layout(xaxis=xaxis, xaxis2=xaxis2)
        # this is a stupid hack... The upper x-axis won't show up unless
        # there is a trace associated with it. So associate this dummy trace
        # with the secondary axis. The trace is invisible.
        fig.add_trace(go.Scatter(x=[1], y=[1], xaxis="x2", visible=False))

        title = dict(
            yref="container",
            yanchor="top",
            y=0.99,
            x=0.5,
            text="<b>TOTAL RUNS BY SPEC AND KEY LEVEL (%s)</b>" % self.patch,
        )
        fig.update_layout(title=title)
        return fig


class BasicHistogram:
    """Draws a histogram of key levels vs runs."""

    def __init__(self, data, patch):
        """Inits with dataframe of key levels vs runs."""
        self.data = data
        self.patch = patch

    def get_xaxis(self):
        """Constructs xaxis."""
        min_x = min(list(self.data.index))
        max_x = max(list(self.data.index))
        range_ = (min_x, max_x)
        tickvals = list(range(0, max_x + 1, 5))
        tickvals[0] = 2
        xaxis = dict(
            title="<b>KEY LEVEL</b>",
            range=range_,
            tickvals=tickvals,
            ticktext=["+" + str(tv) for tv in tickvals],
        )
        return xaxis

    def make_figure(self):
        """Draws plotly histogram."""
        key_level = list(self.data.index)
        runs = list(self.data.values)
        total_runs = sum(runs)
        percentile_rank = 100 * self.data.cumsum() / total_runs
        custom_text = [
            "KEY LEVEL: +{x}<br>RUNS: {y:,}".format(x=item[0], y=item[1])
            for item in zip(key_level, runs)
        ]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=key_level,
                y=runs,
                mode="lines+markers",
                line=dict(width=1, color="black", shape="spline"),
                fillcolor="rgba(1,1,1,0.5)",
                fill="tozeroy",
                text=custom_text,
                customdata=percentile_rank,
                hovertemplate="%{text}" + "<extra>%{customdata:.2f} percentile</extra>",
            )
        )
        fig.update_layout(
            title_text="<b>TOTAL RUNS BY KEY LEVEL (%s)</b>" % self.patch,
            title_x=0.5,
            yaxis_title="<b>NUMER OF RUNS</b>",
            xaxis=self.get_xaxis(),
        )
        return fig


class BubblePlot:
    """Circle plot for total runs."""

    REFERENCE_SIZES = [10 ** n for n in range(1, 8)]
    REFERENCE_LABELS = dict(
        zip(
            REFERENCE_SIZES,
            [
                text + " runs"
                for text in ["10", "100", "1k", "10k", "100k", "1M", "10M"]
            ],
        )
    )

    def __init__(self, data, patch):
        """Inits with spec run data."""
        self.data = data.sum(axis=1).sort_values(ascending=False)
        self.patch = patch
        self.specs = blizzcolors.Specs()

    def make_figure2(self):
        (
            marker_x,
            marker_y,
            marker_size,
            marker_color,
            marker_text,
        ) = self._arrange_bubbles()
        fig = go.Figure(
            data=go.Scatter(
                x=marker_x,
                y=marker_y,
                mode="markers",
                marker_sizemode="area",
                marker_size=marker_size,
                marker_color=marker_color,
                marker_opacity=0.9,
                line_color="black",
                text=marker_text,
                hovertemplate="%{text}<extra></extra>",
            ),
        )
        fig.update_layout(annotations=self.make_anno())
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            width=900,
            height=600,
            showlegend=False,
            title=dict(
                text="<b>TOTAL RUNS RECORDED BY EACH SPEC (%s)</b>" % self.patch, x=0.5
            ),
        )
        fig.add_trace(self._add_reference_bubbles())
        for anno in self._add_reference_annotations():
            fig.add_annotation(anno)
        return fig

    def _arrange_bubbles(self):
        """Arranges bubble position on the canvas."""
        spec_order = self.data.index
        marker_size = []
        marker_color = []
        marker_y = []
        marker_x = []
        marker_text = []
        text_template = "%s<br>Number of runs: %s<br>Pct of top spec: %d%%<br>"
        y = 4
        for spec_role in ["tank", "healer", "mdps", "rdps"]:
            spec_ids = self.specs.get_spec_ids_for_role(spec_role)
            # sort spec from most to least popular
            sorted_specs = []
            for spec in spec_order:
                if spec in spec_ids:
                    sorted_specs.append(spec)

            x = 1
            runs_by_top_spec = self.data[sorted_specs[0]]
            for spec_id in sorted_specs:
                marker_y.append(y)
                marker_x.append(x)
                spec_color = "rgb(%d,%d,%d)" % self.specs.get_color(spec_id)
                marker_color.append(spec_color)
                marker_size.append(1500 * self.data[spec_id] / self.data.iloc[0])
                marker_text.append(
                    text_template
                    % (
                        self.specs.get_spec_name(spec_id).upper(),
                        "{:,}".format(self.data[spec_id]),
                        100 * (self.data[spec_id] / runs_by_top_spec),
                    )
                )
                x += 1
            y -= 1
        return marker_x, marker_y, marker_size, marker_color, marker_text

    def calibrate_reference_marker_size(self):
        """Pick 3 reference bubbles most similar to the actual data."""
        largest_data_bubble = self.data.iloc[0]
        if largest_data_bubble < 100:
            return [1, 10, 100]
        smallest_diff = 10e10
        desired_ref = 0
        for index, ref in enumerate(self.REFERENCE_SIZES):
            diff = abs(largest_data_bubble - ref)
            if smallest_diff > diff:
                smallest_diff = diff
                desired_ref = index
        return self.REFERENCE_SIZES[desired_ref - 2 : desired_ref + 1]

    def _add_reference_bubbles(self):
        """Adds 1x, 10x, 100x reference legend."""
        marker_size = self.calibrate_reference_marker_size()
        # convert raw market size into relative size
        largest_data_bubble = self.data.iloc[0]
        print(largest_data_bubble)
        marker_size = [1500 * ms / largest_data_bubble for ms in marker_size]
        data = go.Scatter(
            x=[9, 9, 9],
            y=[4, 3.6, 3],
            mode="markers",
            marker_sizemode="area",
            # marker_sizemin=30,
            marker_size=marker_size,
            marker_color=["black", "black", "black"],
            marker_opacity=0.5,
            line_color="black",
            text=["100k RUNS", "1M RUNS", "10M RUNS"],
            hovertemplate="%{text}<extra></extra>",
        )
        return data

    def _add_reference_annotations(self):
        """Adds label text next to reference bubbles."""
        x = [10] * 3
        y = [4, 3.6, 3]
        ref_marker_size = self.calibrate_reference_marker_size()
        text = [self.REFERENCE_LABELS[ms] for ms in ref_marker_size]
        annotations = []
        for i in [0, 1, 2]:
            annotation = dict(
                x=x[i],
                y=y[i],
                text=text[i],
                showarrow=False,
                xanchor="left",
                yanchor="middle",
                borderpad=0,
                font=dict(color="black", size=15, family="Monaco, regular"),
            )
            annotations.append(annotation)
        return annotations

    def get_ref_size(self):
        """Fits size of reference bubbles to data."""

    def make_anno(self):
        annotations = []
        position_x = 0
        position_y = 4
        for spec_role in ["tanks", "healers", "melee", "range"]:
            annotation = dict(
                x=position_x,
                y=position_y,
                text=spec_role.upper(),
                font=dict(color="black", size=15, family="Monaco, regular"),
                showarrow=False,
                xanchor="right",
                yanchor="middle",
                borderpad=0,
            )
            position_y -= 1
            annotations.append(annotation)
        return annotations

    def _get_marker_colors(self):
        """Sets marker colors based on spec colors."""
        marker_colors = []
        for spec_id in self.data.index:
            spec_color = "rgb(%d,%d,%d)" % self.specs.get_color(spec_id)
            marker_colors.append(spec_color)
        return marker_colors


class StackedChart:

    hovertemplate = {
        "area+key": "KEY LEVEL: +%{x:d}<br> SHARE: %{y:.0f}%",
        "area+week": "WEEK: %{x}<br> SHARE: %{y:.0f}%",
        "bar+key": "%{text}<br>KEY LEVEL: %{x}<br> SHARE: %{y:.0f}%<extra></extra>",
        "bar+week": "%{text}<br>WEEK: %{x}<br> SHARE: %{y:.0f}%<extra></extra>",
    }

    def __init__(self, data, xaxis_type, spec_role, patch):
        self.specs = blizzcolors.Specs()
        self.xaxis_type = xaxis_type
        self.spec_role = spec_role
        self.data = self.normalize_for_role(data, spec_role)
        self.patch = patch
        self.traces = None

    def normalize_for_role(self, data, spec_role):
        # normalize data to 100% in each x bin
        spec_ids = self.specs.get_spec_ids_for_role(spec_role)
        data = data.loc[spec_ids, :]
        data = 100 * data / data.sum(axis=0)
        # adjust x axis to start with 1 for weekly charts
        if self.xaxis_type == "week":
            data.columns = data.columns - min(data.columns) + 1
        return data

    def get_xaxis(self) -> dict:
        """Creates plotly xaxis for the figure."""
        # add 0.5 padding to xrange for bar plots
        # otherwise, the bars are clipped by the axis box
        min_x = min(list(self.data))
        max_x = max(list(self.data))
        padding = self.get_padding_for_bar()
        range_ = (min_x - padding, max_x + padding)
        if self.xaxis_type == "key":
            tickvals = list(range(0, max_x + 1, 5))
            tickvals[0] = 2
            xaxis = dict(
                title="<b>KEY LEVEL</b>",
                range=range_,
                tickvals=tickvals,
                ticktext=["+" + str(tv) for tv in tickvals],
            )
        elif self.xaxis_type == "week":
            if max_x > 11:
                tickvals = list(range(0, max_x + 1, 4))
                tickvals[0] = 1
            else:
                tickvals = list(range(1, max_x + 1, 1))
            xaxis = dict(
                title="<b>WEEK</b>",
                range=range_,
                tickvals=tickvals,
                ticktext=[str(tv - min_x + 1) for tv in tickvals],
            )
        return xaxis

    def get_fig_title(self) -> str:
        """Creates figure title text."""
        fig_title = ""
        if self.xaxis_type == "key":
            fig_title = "<b>SHARE OF %s SPECS AT EACH KEY LEVEL (%s)</b>" % (
                self.spec_role,
                self.patch,
            )
        elif self.xaxis_type == "week":
            fig_title = "<b>SHARE OF %s SPECS IN WEEKLY TOP 6000 RUNS (%s)</b>" % (
                self.spec_role,
                self.patch,
            )
        return fig_title.upper()

    def get_padding_for_bar(self):
        """Sets axis limit padding for bar plots."""
        padding = 0
        if isinstance(self.traces[0], go.Bar):
            padding = 0.5
        return padding

    @staticmethod
    def get_yaxis() -> dict:
        """Sets yaxis properties of a %normalized share-of-total figure."""
        ytickvals = [0, 20, 40, 60, 80, 100]
        yaxis = dict(
            title="<b>SPEC SHARE (%)</b>",
            range=[0, 101],
            tickvals=ytickvals,
            ticktext=[str(val) + "%" for val in ytickvals],
        )
        return yaxis

    def assemble_figure(self):
        """Assemble plotly figure from pre-made components."""
        fig = go.Figure(
            data=self.traces,
            layout=dict(
                xaxis=self.get_xaxis(),
                yaxis=self.get_yaxis(),
                width=900,
                height=500,
                barmode="stack",  # plotly ignores barmode unless traces are bar
                title=dict(
                    text=self.get_fig_title(),
                    font_size=15,
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
            ),
        )
        return fig


class StackedAreaChart(StackedChart):
    def __init__(self, data, xaxis_type, spec_role, patch):
        super().__init__(data, xaxis_type, spec_role, patch)
        self.traces = self._make_traces()

    def _make_traces(self):
        """Crates traces for each spec in data set."""
        spec_ids = self.specs.get_spec_ids_for_role(self.spec_role)
        traces = []
        for spec_id in spec_ids:
            key_level = list(self.data)
            spec_share = list(self.data.loc[self.data.index == spec_id, :].values[0])
            spec_color = "rgba(%d,%d,%d,0.7)" % self.specs.get_color(spec_id)
            trace = go.Scatter(
                x=key_level,
                y=spec_share,
                mode="lines",
                line=dict(width=1.5, color="black"),
                hoveron="points",
                hovertext="test",
                hovertemplate=self.hovertemplate["area+" + self.xaxis_type],
                fillcolor=spec_color,
                stackgroup="one",
                groupnorm="percent",
                name=self.specs.get_spec_name(spec_id).upper(),
            )
            traces.append(trace)
        return traces


class StackedBarChart(StackedChart):
    def __init__(self, data, xaxis_type, spec_role, patch):
        super().__init__(data, xaxis_type, spec_role, patch)
        self.traces = self._make_traces()

    def _make_traces(self):
        """Crates traces for each spec in data set."""
        spec_ids = self.specs.get_spec_ids_for_role(self.spec_role)
        traces = []
        for spec_id in spec_ids:
            key_level = list(self.data)
            spec_share = list(self.data.loc[self.data.index == spec_id, :].values[0])
            spec_color = "rgba(%d,%d,%d,0.7)" % self.specs.get_color(spec_id)
            traces.append(
                go.Bar(
                    name=self.specs.get_spec_name(spec_id).upper(),
                    x=key_level,
                    y=spec_share,
                    marker=dict(color=spec_color, line=dict(color="black", width=1)),
                    hoverlabel_align="right",
                    text=[self.specs.get_spec_name(spec_id).upper()] * len(key_level),
                    hoverlabel=dict(bgcolor="black"),
                    hovertemplate=self.hovertemplate["bar+" + self.xaxis_type],
                )
            )
        return traces
