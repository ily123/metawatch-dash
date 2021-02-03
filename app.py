import dash

app = dash.Dash(__name__, suppress_callback_exceptions=True)
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
application = app.server
