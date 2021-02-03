import constructor
import dash_html_components as html
from app import app

from apps import app_activity, app_comps, app_specs

layout = html.Div(
    [
        html.H3("FAQ"),
        html.Br(),
        html.Div(id="faq", children=constructor.faq_errata()),
        html.Br(),
    ]
)
