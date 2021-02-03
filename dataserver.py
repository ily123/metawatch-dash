"""Container for methods that serve data to the apps."""

import sqlite3
from typing import Dict

import pandas as pd


class DataServer:
    """Container for methods that serve data to the apps."""

    def __init__(self, db_file_path: str) -> None:
        """Inits with path to the SQLite db file.

        Parameters
        ----------
        db_file_path : str
            path to SQLite db file
        """
        self.db_file_path = db_file_path
        self.raw_data = self.load_raw_data()

    def load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """Loads data tables from the SQLite file.

        Returns
        -------
        raw_data : dict(str, pd.DataFrame)
            Includes two dataframes with data.
            raw_data["specs"] is key count by spec/level/season
            raw_data["weekly"] is key count by spec/week(period) inside the top 500 keys
        """
        conn = sqlite3.connect(self.db_file_path)
        specs = pd.read_sql_query("SELECT * FROM main_summary_seasons", conn)
        weekly = pd.read_sql_query("SELECT * FROM weekly_summary", conn)
        raw_data = {"specs": specs, "weekly_top": weekly}
        conn.close()
        return raw_data

    def get_data_for_ridgeplot(self, season: str) -> pd.DataFrame:
        """Returns key counts for ridge plot.

        Returns
        -------
        data : pd.DataFrame
            pivoted run counts; index is spec id, columns are key levels,
        """
        data = self.raw_data["specs"]
        season_mask = data["season"] == season
        # pivot tables for the figure api
        data = pd.pivot_table(
            data[season_mask],
            values="run_count",
            index=["spec"],
            columns=["level"],
            fill_value=0,
        )
        return data

    def get_data_for_run_histogram(self, season: str) -> pd.DataFrame:
        """Returns key counts vs level for histogram on panel 3.

        Returns
        -------
        run_per_level : pd.DataFrame
            index is key level, column is run count
        """
        data = self.raw_data["specs"]
        run_per_level = (
            data.loc[data["season"] == season, ["level", "run_count"]]
            .groupby("level")
            .sum()
        )
        run_per_level = round(run_per_level / 5)  # there are 5 records per run
        run_per_level = run_per_level.astype(int)
        return run_per_level

    def get_data_for_weekly_chart(self) -> pd.DataFrame:
        """Returns top 500 key counts resolved by week and spec."""
        data = pd.pivot_table(
            self.raw_data["weekly_top"],
            values="run_count",
            index="spec",
            columns="period",
            fill_value=0,
        )
        return data

    def get_max_key_for_season(self, season) -> int:
        """Returns max level of key completed in season."""
        data = self.raw_data["specs"]
        max_key_level = data.loc[data["season"] == season, "level"].max()
        return max_key_level

    def get_comp_data(self) -> pd.DataFrame:
        """Fetches composition table from the db.

        Returns
        -------
        composition : pd.DataFrame
            dataframe with following columns - tokenized comp name,
            number of runs by comp, average and std dev of the run
            key levels
        """
        conn = sqlite3.connect(self.db_file_path)
        composition = pd.read_sql_query(
            "SELECT * FROM composition ORDER BY run_count DESC", conn
        )
        conn.close()
        return composition

    def get_activity_data(self) -> pd.DataFrame:
        """Fetches activity table from the db.

        Returns
        -------
        activity : pd.DataFrame
            dataframe with periods and their run counts
        """
        conn = sqlite3.connect(self.db_file_path)
        activity = pd.read_sql_query("SELECT * FROM activity", conn)
        conn.close()
        # this is a lazy fix.... add some of the missing data:
        # I need to fix this later.
        old_data = {
            734:552152,
            735:573429,
            736:600545,
            737:533797,
            738:600092,
            739:574013,
            740:632797,
            741:566984,
            742:530253,
            743:602726,
            744:619092,
            745:675847,
            746:664888,
            747:687195,
            748:715860,
            749:621633,
            750:734762,
            751:750325,
            752:718098,
            753:695534,
            754:693893,
            755:629968,
            756:607517,
            757:627584,
            758:601825,
            759:551282,
            760:606719,
            761:565799,
            762:604201,
            763:496264,
            764:552763,
            765:473691,
            766:403492,
            767:371905,
            768:367528,
            769:349379,
            770:285902,
            771:267267,
            772:353923
        }
        old_data = {
            "period": list(old_data.keys()),
            "run_count": list(old_data.values())
        }
        old_data = pd.DataFrame(old_data)
        activity = pd.concat([activity, old_data], axis=0)
        activity.sort_values(by="period", ascending=True, inplace=True)
        return activity
