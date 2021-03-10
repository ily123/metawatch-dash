"""Module for uploading data to the M+ MySQL database."""
import configparser
from typing import List, Optional, Tuple, Union

import mysql.connector
import pandas as pd


class MplusDatabase(object):
    """Class for working with M+ MySQL database."""

    __utility_tables = ["realm", "region", "dungeon", "spec", "period"]
    __table_fields = {  # these are used to formulate batch inserts queries
        "period": [
            "region",
            "id",
            "start_timestamp",
            "end_timestamp",
            "tyrannical",
            "affixes",
        ],
        "run": [
            "id",
            "dungeon",
            "level",
            "period",
            "timestamp",
            "duration",
            "faction",
            "region",
            "score",
            "istimed",
            "composition",
        ],
        "roster": ["run_id", "character_id", "name", "spec", "realm"],
        "run_composition": [
            "run_id",
            "mage_arcane",
            "mage_fire",
            "mage_frost",
            "paladin_holy",
            "paladin_protection",
            "paladin_retribution",
            "warrior_arms",
            "warrior_fury",
            "warrior_protection",
            "druid_balance",
            "druid_feral",
            "druid_guardian",
            "druid_restoration",
            "death_knight_blood",
            "death_knight_frost",
            "death_knight_unholy",
            "hunter_beast_mastery",
            "hunter_marksmanship",
            "hunter_survival",
            "priest_discipline",
            "priest_holy",
            "priest_shadow",
            "rogue_assassination",
            "rogue_outlaw",
            "rogue_subtlety",
            "shaman_elemental",
            "shaman_enhancement",
            "shaman_restoration",
            "warlock_affliction",
            "warlock_demonology",
            "warlock_destruction",
            "monk_brewmaster",
            "monk_windwalker",
            "monk_mistweaver",
            "demon_hunter_havoc",
            "demon_hunter_vengeance",
        ],
    }  # is this time to move these into their own container?

    def __init__(self, config_file_path):
        """Inits with database config file."""
        # self.credentials = self.parse_config_file(config_file_path)
        parser = configparser.ConfigParser()
        parser.read(config_file_path)
        self.credentials = {}
        self.credentials["user"] = parser["DATABASE"]["user"]
        self.credentials["password"] = parser["DATABASE"]["password"]
        self.credentials["host"] = parser["DATABASE"]["host"]
        self.credentials["database"] = "keyruns"

    def connect(self):
        """Connects to the database.

        Returns
        -------
        conn : mysql.connector connection
            open connection to the MDB.
        """
        conn = mysql.connector.connect(**self.credentials)
        return conn

    def insert(self, table, data):
        """Batch-inserts list of rows into database.

        Warning: make sure row fields align with fields in the table.
        """
        if not isinstance(data, list):
            raise TypeError("Supply data as a list of rows.")
        if table not in self.__table_fields.keys():
            raise ValueError("Table not annotated in object attrs.")
        fields = self.get_table_fields(table)
        connection = self.connect()
        cursor = connection.cursor()
        try:
            query = (
                "INSERT IGNORE into {table} ({table_fields}) VALUES ({blanks})"
            ).format(
                table=table,
                table_fields=",".join(fields),
                blanks=",".join(["%s" for i in range(0, len(fields))]),
            )
            # executemany supposedly batches data into a single query
            cursor.executemany(query, data)
            connection.commit()
        except Exception as error:
            raise Exception("Problem with inserting data into MDB: [%s]" % error)
        finally:
            cursor.close()
            connection.close()

    def send_query_to_mdb(self, query, isfetch=False) -> Optional[List[tuple]]:
        """Sends non-insert query to MDB."""
        result = None
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("use keyruns")
            cursor.execute(query)
            if isfetch:
                result = cursor.fetchall()
            conn.commit()
        except Exception as error:
            print("ERROR CONNECTING TO MDB: ", error)
            if "Commands out of sync; you can't run this command now" in str(error):
                print(
                    """
                    NOTE: You probably sent a SELECT query that returns something,
                    but didn't set isfetch to True. So now it's trying to commit() after
                    a transaction that hasn't been fetched. Try setting isfetch to True.
                    """
                )
        finally:
            conn.close()
        return result

    def get_table_fields(self, table):
        """Returns fieds in table, in correct order.

        The table schemas are set up by hand and correspond to MDB.
        """
        return self.__table_fields[table]

    def get_utility_table(self, table):
        """Retrieves utility table from the database in SELECT * fashion.

        Params
        ------
        table : str
            name of the utility table:
              'realm' : mapping of realm names, ids, and cluter ids
              'dungeon' : mapping of dungeon names and ids
              'region' : mapping of region tokens to ids
              'spec' : mapping of class-spec ids and names
              'period' : period id to region and timestamp

        Returns
        -------
        data : pd.DataFrame
            response the database sent back, formatted as pandas df
        """
        if table not in self.__utility_tables:
            raise ValueError("%s is not a legal utility table." % table)
        data, columns = None, None
        connection = self.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * from %s" % table)
            data = cursor.fetchall()
            columns = cursor.column_names
        except:
            raise Exception("Problem retrieving util table.")
        finally:
            cursor.close()
            connection.close()
        return pd.DataFrame(data, columns=columns)

    def pull_existing_run_ids(self, region: int, period: int) -> List[int]:
        """Pulls id column from the 'run' table for specified period/region."""
        query = "SELECT id FROM run WHERE region=%d and period=%d" % (region, period)
        run_ids = self.send_query_to_mdb(query=query, isfetch=True)
        run_ids = [int(item[0]) for item in run_ids]
        return run_ids

    def update_summary_spec_table(self, period_start, period_end) -> None:
        """Updates 'summary_spec' table with runs from specified period band."""
        # at some point, I need to make this method more flexible wrt period clause
        update_query = """
            INSERT INTO summary_spec
            SELECT period, spec, level, count(level) as count
            FROM run
            INNER JOIN roster on run.id = roster.run_id
            WHERE run.period BETWEEN %d AND %d
            GROUP BY period, spec, level
            ON DUPLICATE KEY UPDATE count=VALUES(count);
        """
        update_query = update_query % (period_start, period_end)
        self.send_query_to_mdb(update_query)

    def get_summary_spec_table_as_df(self) -> pd.DataFrame:
        """Exports summary_spec table formatted for front-end.

        The summary table is grouped by by spec/level/season."""
        query = "SELECT * from summary_spec;"
        data_ = self.send_query_to_mdb(query, isfetch=True)
        data = pd.DataFrame(data_, columns=["period", "spec", "level", "count"])
        data["season"] = "unknown"
        data.loc[(data.period) >= 734 & (data.period <= 771), "season"] = "bfa4"
        data.loc[data.period >= 772, "season"] = "bfa4_postpatch"
        data.loc[data.period >= 780, "season"] = "SL1"
        data_grouped = (
            data[["season", "spec", "level", "count"]]
            .groupby(["season", "spec", "level"])
            .sum()
        )
        data_grouped.reset_index(inplace=True)
        return data_grouped

    def update_weekly_top500_table(self, period_start: int, period_end: int) -> None:
        """Updates 'period_rank' and 'summary_top500' tables with period runs"""
        # this is janky: I need to dynamically update the list of top 500 runs
        # (the rankings change throughout the week)
        # rather than mess around with primary keys, comparing ranks, etc
        # just drop the week of interest from the table,
        # and regenerate ranks for that week from scratch
        drop_query = "DELETE FROM period_rank WHERE period BETWEEN %d and %d" % (
            period_start,
            period_end,
        )
        self.send_query_to_mdb(drop_query)

        # now regen ranks for that period
        # this query is a bit hairy:
        # it selects runs from 'run' table, partitions them into groups by
        # dungeon and period, then applies DENSE_RANK within groups over the
        # 'score' column. Runs with rank <= 500 are selected and inserted
        # into the 'period_rank' table
        # it's a minor time save over regenerating the entire table or using a view
        # it also makes the table exportable
        rank_update_query = """
            INSERT INTO period_rank
            SELECT period, period_rank, id from (
            SELECT id, dungeon, period, score,
            DENSE_RANK() OVER(
            PARTITION BY period, dungeon ORDER BY score DESC
            ) as period_rank from run WHERE period BETWEEN %d and %d) as subtable
            WHERE period_rank <= 500
        """
        rank_update_query = rank_update_query % (period_start, period_end)
        self.send_query_to_mdb(rank_update_query)

        # now, join the top 500 ranks to roster, count stats, and save into summary
        summary_update_query = """
            INSERT INTO summary_top500
            SELECT period, spec, count(spec) FROM period_rank
            LEFT JOIN roster
            ON period_rank.id = roster.run_id
            WHERE period_rank.period BETWEEN %d and %d
            GROUP BY period, spec
            ON DUPLICATE KEY UPDATE count=VALUES(count);
        """
        summary_update_query = summary_update_query % (period_start, period_end)
        self.send_query_to_mdb(summary_update_query)

    def get_weekly_top500(self):
        """Aggs 'period_rank'/'roster' join by spec/period."""
        query = "SELECT * FROM summary_top500"
        data = self.send_query_to_mdb(query, isfetch=True)
        return data

    def get_composition_data(
        self, period_start: int, period_end: int
    ) -> Union[List[Tuple[str, int, float, float, int]], None]:
        """Fetches composition data for a period interval.

        Parameters
        ----------
        period_start : int
            start of the period, using Blizzard's period id
        period_end : int
            end of the period, using Blizzard's period id

        Returns
        -------
        data : List[tuple(str, int, float, float, int)], optional
            list of tuples with comp data, including tokenized comp name
            the number of runs, and average, std dev, and max of the run key levels
        """
        query = """
            SELECT composition, COUNT(level), AVG(level), STD(level), MAX(level)
            FROM run
            WHERE period between {start} and {end}
            GROUP BY composition
            ORDER BY COUNT(level);
        """.format(
            start=period_start, end=period_end
        )
        data = self.send_query_to_mdb(query, isfetch=True)
        # the third column is returned as "decimal.Decimal", convert to "float"
        if data:
            data = [(c1, c2, float(c3), c4, c5) for c1, c2, c3, c4, c5 in data]
        return data

    def get_activity_data(self) -> List[Tuple[int, int]]:
        """Fetches key runs per period data.

        Returns
        -------
        data : List[tuple(int, int)]
            List of period and its number of key runs
        """
        query = """
            SELECT period, count(period)
            FROM run
            GROUP BY period
        """
        # Consider doing it this way after DB merge:
        # SELECT period, tyrannical, COUNT(level), MAX(level), AVG(level)
        # from run left join period on run.period = period.id where period.region = 1
        # group by period;
        data = self.send_query_to_mdb(query, isfetch=True)
        return data

    def get_composition_data_COLLATE(
        self, period_start: int, period_end: int
    ) -> Union[List[Tuple[str, int, float, float, int]], None]:
        """Fetches composition data for a period interval.

        Parameters
        ----------
        period_start : int
            start of the period, using Blizzard's period id
        period_end : int
            end of the period, using Blizzard's period id

        Returns
        -------
        data : List[tuple(str, int, float, float, int)], optional
            list of tuples with comp data, including tokenized comp name
            the number of runs, and average, std dev, and max of the run key levels
        """

        query = """
            SELECT Composition, COUNT(level), AVG(level), STD(level), MAX(level)
            FROM run
            WHERE period between {start} and {end}
            GROUP BY Composition, Cast(composition As binary(100))
            ORDER BY COUNT(level);
        """.format(
            start=period_start, end=period_end
        )
        data = self.send_query_to_mdb(query, isfetch=True)
        # the third column is returned as "decimal.Decimal", convert to "float"
        if data:
            data = [(c1, c2, float(c3), c4, c5) for c1, c2, c3, c4, c5 in data]
        return data

    def update_ranks_table(
        self, period_start: int, period_end: int, min_level: int
    ) -> None:
        """Updates ranks for specified runs.

        Parameters
        ----------
        period_start : int
            start of the period, using Blizzard's period id
        period_end : int
            end of the period, using Blizzard's period id
        min_level : int
            minimum level of keys to rank
        """
        # CREATE table ranks_(id bigint not null PRIMARY KEY, rank_ bigint);
        query = """
            INSERT INTO run_rank select run.id, RANK() OVER(partition by run.dungeon, period.tyrannical ORDER BY run.score DESC) as rank_
            from run left join period on run.period = period.id
            where period.region = 1 and run.period BETWEEN {start} AND {end} and run.level >= {min_level}
            ON DUPLICATE KEY UPDATE run_rank.rank_=VALUES(rank_);
        """.format(
            start=period_start, end=period_end, min_level=min_level
        )
        self.send_query_to_mdb(query, isfetch=False)

    def get_player_runs(
        self, name: str, realm: int
    ) -> List[Tuple[str, int, int, int, int]]:
        """Returns m+ runs for player.

        Parameters
        ----------
        name : str
            player character name
        realm : int
            blizzard id of the player realm

        Returns
        -------
        runs : list
            list of runs including meta information and roster
        """
        if not isinstance(realm, int):
            raise TypeError("Realm id needs to be an integer. You provided: %s" % realm)
        query = """
            SELECT run.id, roster.name, roster.realm, roster.spec, run.dungeon,
                run.level, run.istimed, run.period, period.affixes, run_rank.rank_
            FROM
                (select run_id from roster where name="{name}" and realm={realm}) AS run_ids
            LEFT JOIN roster ON run_ids.run_id = roster.run_id
            LEFT JOIN run_rank ON run_rank.run_id=run_ids.run_id
            LEFT JOIN run ON run.id = run_ids.run_id
            LEFT JOIN period ON period.id=run.period
            WHERE period.region = 1 AND run.period BETWEEN 780 AND 1000;
        """.format(
            name=name, realm=realm
        )
        data = self.send_query_to_mdb(query, isfetch=True)
        return data
