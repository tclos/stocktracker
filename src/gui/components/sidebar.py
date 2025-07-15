from dash import html

def sidebar():
    link_style = {
        "display": "block",
        "padding": "0.25rem 0",
        "color": "white",
        "borderBottom": "1px solid #444",
        "textDecoration": "none",
    }
    
    return html.Div(
        [
            html.H2("StockTracker"),
            html.Hr(),
            html.A("Home", href="/", style=link_style),
            html.A("Wallets", href="/wallets", style=link_style),
        ],
        style={
            "position": "fixed",
            "width": "15rem",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "padding": "2rem 1rem",
            "backgroundColor": "#212529",
        },
    )
