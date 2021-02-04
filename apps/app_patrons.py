
import constructor
import dash_html_components as html
from app import app


layout = html.Div(
    [
        html.H3("CREDITS"),
        html.P("This is where Patron names will go. Once we have some patrons. We will totally have patrons."),
        html.P("If you are interested in becoming the FIRST PATRON, see our Patreon at https://www.patreon.com/benched", id="patreon-alert"),
        html.P("If you sign up and something doesn't work, don't panic, we will figure it out."),
        html.Br(),
        html.Br(),
    ]
)
