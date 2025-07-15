import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dash import html, dcc
import dash_bootstrap_components as dbc

from gui.components.sidebar import sidebar
from gui.components.stocks_modals import add_stock_modal, sell_stock_modal


def create_layout(wallet):
    """
    Creates and returns the main application layout.

    Args:
        wallet: The wallet object containing portfolio data

    Returns:
        A Dash HTML Div containing the complete application layout
    """

    wallet_df = wallet.to_dataframe()  # Get current portfolio data as a DataFrame
    # Create a ListGroup component to display all stocks in the portfolio
    stock_list = dbc.ListGroup(
        [
            # Create a ListGroupItem for each stock in the portfolio
            dbc.ListGroupItem(
                # Each item contains a Row with two columns:
                dbc.Row(
                    [
                        dbc.Col(
                            html.H6(row["Ticket"]), width=4, className="font-weight-bold"
                        ),  # Left column shows the stock ticket
                        dbc.Col(
                            html.Div(
                                [  # Right column shows quantity and current value
                                    html.Small(f"{row['Quantidade']} shares"),
                                    html.Br(),  # Line break
                                    html.Small(
                                        f"${row['Valor Atual']:.2f}",
                                        className="text-success",
                                    ),
                                ]
                            ),
                            width=8,
                        ),
                    ]
                ),
                id={
                    "type": "stock-item",
                    "index": i,
                },  # Set unique ID for each item for callback targeting
                action=True,  # Makes items clickable
                className="px-3 py-2",
                style={  # Hover effects
                    "transition": "all 0.3s ease",
                    "cursor": "pointer"
                }
            )
            for i, row in wallet_df.iterrows()  # Create item for each stock
        ],
        flush=True,  # Removes borders for cleaner look
        id="stock-list",
        className="mb-4"
    )
    # Create action buttons for adding/selling stocks
    buttons = html.Div(
        [
            dbc.Button(
                "Add Stock", id="open-add-stock", color="success", className="me-2", outline=True
            ),
            dbc.Button("Sell Stock", id="open-sell-stock", color="danger", outline=True),
        ],
        # Add margin above and below buttons
        style={"margin": "1rem 0"},
    )
    # Main area
    content = html.Div(
        [
            html.H4(f"{wallet.name}'s stocks"),
            stock_list,
            buttons,  # Action buttons
            html.Hr(),
            html.Div(id='stock-details', className="p-3 bg-dark rounded mb-4"),
            html.Hr(),
            # Stock chart section
            html.Div(   
                [
                    html.H5(id="stock-historic-title", children=""),
                    dcc.Graph(
                        id="stock-historic",
                        figure={
                            "data": [],
                            "layout": {
                                "title": "",
                                "plot_bgcolor": "#1e1e1e",
                                "paper_bgcolor": "#1e1e1e",
                                "font": {"color": "white"},
                            },
                        },
                        config={"displayModeBar": False},
                    ),
                ],
                id='stock-historic-frame',
                className="mb-4",
                style={"display": "none"}  # Hidden by default
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H5("Wallet Performance"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id='benchmark-dropdown',
                                            options=[
                                                {'label': 'S&P 500', 'value': '^GSPC'},
                                                {'label': 'Dow Jones', 'value': '^DJI'},
                                                {'label': 'NASDAQ', 'value': '^IXIC'},
                                                {'label': 'None', 'value': 'none'},
                                            ],
                                            value='none',
                                            clearable=False,
                                            className="mb-3",
                                            style={
                                                'color': 'black',
                                                'width': '200px'
                                            }
                                        ),
                                        width=3
                                    ),
                                ]
                            ),
                            dcc.Graph(
                                id="wallet-performance",
                                figure={
                                    "data": [],
                                    "layout": {
                                        "title": "Wallet Value Over Time",
                                        "plot_bgcolor": "#1e1e1e",
                                        "paper_bgcolor": "#1e1e1e",
                                        "font": {"color": "white"},
                                    },
                                },
                                config={"displayModeBar": False},
                            ),
                        ]
                    )
                ]
            ),
            html.Div(
                [
                    dbc.Button(
                        "Download Metrics Report",
                        id="download-metrics-btn",
                        color="primary",
                        outline=True,
                        className="me-2 mb-2",
                        n_clicks=0
                    ),
                    dbc.Button(
                        "Download Purchase History",
                        id="download-purchases-btn",
                        color="primary",
                        outline=True,
                        className="me-2 mb-2",
                        n_clicks=0
                    ),
                    dbc.Button(
                        "Download Assets Listing",
                        id="download-assets-btn",
                        color="primary",
                        outline=True,
                        className="me-2 mb-2",
                        n_clicks=0
                    ),
                    dbc.Button(
                        "Download Full CSV Report",
                        id="download-csv-btn",
                        color="primary",
                        outline=True,
                        className="me-2 mb-2",
                        n_clicks=0
                    ),
                    
                    # Hidden download components
                    dcc.Download(id="download-metrics"),
                    dcc.Download(id="download-purchases"),
                    dcc.Download(id="download-assets"),
                    dcc.Download(id="download-csv"),
                ],
                style={
                    "margin-top": "2rem",
                    "padding": "1rem",
                    "border-top": "1px solid #dee2e6"
                }
            ),
            
            add_stock_modal(),  # Include the add stock modal (initially hidden)
            sell_stock_modal(),  # Include the sell stock modal (initially hidden)
        ],
        style={  # accounting for sidebar width
            "margin-left": "17rem",
            "padding": "2rem 1rem",
        },
    )
    # Return the complete layout with sidebar and main content
    return html.Div([sidebar(), content])