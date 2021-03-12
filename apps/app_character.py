import dash_html_components as html
from app import app
from dash.dependencies import Input, Output, State

import mysql.connector
import time
import mplusdb

from typing import List, Optional, Tuple, Union

# move this to utils at some point:
AFFIX_SRC = {
    1: "https://render-us.worldofwarcraft.com/icons/56/inv_misc_volatilewater.jpg",
    2: "https://render-us.worldofwarcraft.com/icons/56/spell_magic_lesserinvisibilty.jpg",
    3: "https://render-us.worldofwarcraft.com/icons/56/spell_shaman_lavasurge.jpg",
    4: "https://render-us.worldofwarcraft.com/icons/56/spell_deathknight_necroticplague.jpg",
    5: "https://render-us.worldofwarcraft.com/icons/56/spell_nature_massteleport.jpg",
    6: "https://render-us.worldofwarcraft.com/icons/56/ability_warrior_focusedrage.jpg",
    7: "https://render-us.worldofwarcraft.com/icons/56/ability_warrior_battleshout.jpg",
    8: "https://render-us.worldofwarcraft.com/icons/56/spell_shadow_bloodboil.jpg",
    9: "https://render-us.worldofwarcraft.com/icons/56/achievement_boss_archaedas.jpg",
    10: "https://render-us.worldofwarcraft.com/icons/56/ability_toughness.jpg",
    11: "https://render-us.worldofwarcraft.com/icons/56/ability_ironmaidens_whirlofblood.jpg",
    12: "https://render-us.worldofwarcraft.com/icons/56/ability_backstab.jpg",
    13: "https://render-us.worldofwarcraft.com/icons/56/spell_fire_felflamering_red.jpg",
    14: "https://render-us.worldofwarcraft.com/icons/56/spell_nature_earthquake.jpg",
    16: "https://render-us.worldofwarcraft.com/icons/56/achievement_nazmir_boss_ghuun.jpg",
    117: "https://render-us.worldofwarcraft.com/icons/56/ability_racial_embraceoftheloa_bwonsomdi.jpg",
    119: "https://render-us.worldofwarcraft.com/icons/56/spell_shadow_mindshear.jpg",
    120: "https://render-us.worldofwarcraft.com/icons/56/trade_archaeology_nerubian_obelisk.jpg",
    121: "https://render-us.worldofwarcraft.com/icons/56/spell_animarevendreth_buff.jpg",
    122: "https://render-us.worldofwarcraft.com/icons/56/spell_holy_prayerofspirit.jpg",
    123: "https://render-us.worldofwarcraft.com/icons/56/spell_holy_prayerofshadowprotection.jpg",
    124: "https://render-us.worldofwarcraft.com/icons/56/spell_nature_cyclone.jpg",
}
mdb = mplusdb.MplusDatabase("config/db_config.ini")


layout = html.Div(
    [
        html.H3("Character Lookup"),
        html.Br(),
        html.Div(
            id="character-lookup",
            children=[
                html.Button("TEST", id="test-button", n_clicks=0),
                html.P("Output goes here", id="output"),
            ],
        ),
        html.Br(),
    ]
)


@app.callback(
    Output(component_id="output", component_property="children"),
    Input(component_id="test-button", component_property="n_clicks"),
    prevent_initial_call=True,
)
def send_query(button_click):
    """Sends player runs look up query to MDB."""
    print("click recieved")
    time.sleep(0.3)
    t0 = time.time()
    runs = mdb.get_player_runs(name="Nerfmeta", realm=1566)
    runs_html = format_mdb_response(runs, "Nerfmeta")
    return runs_html
    # return str("character query took %1.2f sec" % (time.time() - t0))


def format_mdb_response(runs: List[Tuple], name: str) -> html.Table:
    """Formats player runs into a HTML table."""
    out = html.Table(children=[])
    for run in runs:
        run = list(run)
        run[-5] = "+%d" % run[-5]
        if run[1] != name:
            continue
        row = html.Tr([html.Td(children=[str(item)]) for item in run])
        # we don't need some of the columns
        row.children.pop(0)
        # insert pic links
        test_link = (
            "https://render-us.worldofwarcraft.com/icons/56/inv_misc_volatilewater.jpg"
        )
        print(row.children[-2])
        row.children[-2] = html.Td(
            children=[
                html.Img(src=AFFIX_SRC[int(affix)], width=20, height=20)
                for affix in row.children[-2].children[0].split("_")
            ]
        )
        out.children.append(row)
    out.children.insert(
        0,
        html.Tr(
            children=[
                html.Th(head)
                for head in [
                    "Name",
                    "Realm",
                    "Spec",
                    "Dungeon",
                    "Level",
                    "Timed",
                    "Week",
                    "Affix",
                    "Rank",
                ]
            ]
        ),
    )
    return out
