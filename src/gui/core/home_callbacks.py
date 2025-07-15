import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dash import html, Input, Output
from dash.exceptions import PreventUpdate
from stocktracker.utils import get_yahoo_movers


def register_home_callbacks(app):
    """
    Registers the callback for updating the home page's market movers section.

    This includes:
    - Top Gainers
    - Top Losers
    - Most Active stocks

    Args:
        app: The Dash app instance.
    """

    @app.callback(
        [
            Output("gainers-content", "children"),  # Target the "Top Gainers" card body
            Output("losers-content", "children"),  # Target the "Top Losers" card body
            Output(
                "most-active-content", "children"
            ),  # Target the "Most Active" card body
        ],
        Input("url", "pathname"),  # Triggered when URL path changes
        prevent_initial_call=False,  # Allow callback on initial page load
    )
    def update_market_movers(pathname):
        """
        Updates the content of each mover card when the user is on the home page.

        Only runs when pathname is `/`, which corresponds to the home route.
        """
        # If we're not on the home page, do nothing
        if pathname != "/":
            raise PreventUpdate

        # Call utility functions to scrape movers from Yahoo (returns lists of dicts)
        gainers = get_yahoo_movers("gainers") or []
        losers = get_yahoo_movers("losers") or []
        active = get_yahoo_movers("most-active") or []

        # Format each stock item into a small HTML row
        def format_item(item):
            return html.Div(
                [
                    html.Span(
                        f"{item['symbol']} ", className="font-weight-bold"
                    ),  # Stock Ticket
                    html.Span(
                        f" ${item['change']}",  # Show price change
                        # Green if up, red if down
                        style={
                            "color": "#00C853" if item["is_positive"] else "#FF3D00"
                        },
                    ),
                ],
                className="py-3",
            )

        # Return a list of formatted Divs for each category (limit to top 5 items)
        return (
            [format_item(item) for item in gainers[:5]],
            [format_item(item) for item in losers[:5]],
            [format_item(item) for item in active[:5]],
        )