import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dash import html, dcc
from gui.components.mover_card import create_mover_card
from gui.components.sidebar import sidebar


def create_layout():
    """
    Constructs the layout for the home page of the app.
    It includes:
    - Sidebar for navigation
    - A main content area with a header
    - Cards for displaying top stock movers (gainers, losers, most active)
    """
    return html.Div(
        id="home-container",  # Container for the entire home page
        children=[
            sidebar(),
            html.Div(
                id="main-content",  # Main content area
                style={
                    "marginLeft": "17rem",
                    "padding": "2rem 1.5rem",
                    "minHeight": "100vh",
                },
                children=[
                    # Header section with title and subtitle
                    html.Div(
                        id="header-section",
                        children=[
                            html.H2("Market Overview", className="mb-1"),  # Main title
                            html.P(
                                "Today's top market movers", className="text-muted mb-3"
                            ),
                        ],
                        className="pb-2",
                    ),
                    # Section containing the market mover cards (gainers, losers, most active)
                    html.Div(
                        dcc.Loading(
                            id="movers-loading",  # Loading spinner wrapper
                            type="circle",  # Circular spinner animation
                            children=html.Div(
                                id="movers-container",  # Container that will receive updated stock content
                                children=[
                                    create_mover_card(
                                        "most-active", "🔥 Most Active"
                                    ),  # Card for most active stocks
                                    create_mover_card(
                                        "gainers", "🚀 Top Gainers"
                                    ),  # Card for gainers
                                    create_mover_card(
                                        "losers", "📉 Top Losers"
                                    ),  # Card for losers
                                ],
                                style={
                                    "display": "flex",
                                    "flexWrap": "wrap",
                                    "gap": "20px",  # Space between cards
                                    "marginTop": "20px",
                                },
                            ),
                        )
                    ),
                ],
            ),
        ],
    )