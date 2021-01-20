import sqlite3
from typing import List

import pandas as pd

import blizzcolors


def get_comp_data() -> pd.DataFrame:
    """Fetches composition table from the db.

    Returns
    -------
    composition : pd.DataFrame
        dataframe with following columns - tokenized comp name
        number of runs by comp, average and std dev of the run
        key levels
    """
    conn = sqlite3.connect("data/summary.sqlite")
    composition = pd.read_sql_query("SELECT * FROM composition", conn)
    conn.close()
    return composition


def vectorize_comps(composition: pd.DataFrame) -> pd.DataFrame:
    """Appends vector representation of each comp to the composition df.

    Parameter
    ---------
    composition : pd.DataFrame
        dataframe with following columns - tokenized comp name
        number of runs by comp, average and std dev of the run
        key levels

    Returns
    -------
    composition_vectorized : pd.DataFrame
        original dataframe, plus 36 columns encoding spec frequencies
        for each comp
    """
    spec_util = blizzcolors.Specs()
    comp_matrix = composition.apply(
        lambda row: spec_util.vectorize_comp_token(row["composition"]), axis=1
    )
    comp_matrix = pd.DataFrame(comp_matrix.values.tolist())
    comp_matrix.columns = [spec["token"] for spec in spec_util.specs]
    composition_vectorized = pd.concat([composition, comp_matrix], axis=1)
    return composition_vectorized


composition = vectorize_comps(get_comp_data())
print(len(composition))
