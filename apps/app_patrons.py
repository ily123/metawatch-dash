
import constructor
import dash_html_components as html
from app import app


layout = html.Div(
    [
        html.H3("CREDITS"),
        html.P("This website is graciously supported by:"),
        html.P("Alcaras", style={"font-weight": "bold", "color": "purple"}),
        html.Br(),
        html.Br(),
        html.Hr(),
        html.P("If you are interested in becoming a patron see https://www.patreon.com/benched"),
        html.Br(),
        html.Br(),
    ]
)
