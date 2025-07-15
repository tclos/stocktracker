import pandas as pd

import dash_bootstrap_components as dbc
from dash import dcc, html


def add_stock_modal():
    """Returns a modal component for adding a stock to the wallet"""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Add Stock")),  # Title
            dbc.ModalBody(
                [
                    html.Div(id="add-stock-error"),  # Error display at the top
                    # Form containing all the inputs for adding a stock
                    dbc.Form(
                        [
                            # Stock ticket input
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Stock Ticket",
                                        html_for="stock-ticket-input",
                                        width=4,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="stock-ticket-input",
                                            type="text",
                                            placeholder="ex: AAPL",
                                        ),
                                        width=8,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            # Quantity input
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Quantity", html_for="quantity-input", width=4
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="quantity-input",
                                            type="number",
                                            min=1,
                                            step=1,
                                            placeholder="ex: 10",
                                        ),
                                        width=8,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            # Price per share input
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Price per Share",
                                        html_for="price-input",
                                        width=4,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="price-input",
                                            type="number",
                                            min=0.01,
                                            step=0.01,
                                            placeholder="ex. 200.00",
                                        ),
                                        width=8,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            # Purchase date input
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Purchase Date", html_for="date-input", width=4
                                    ),
                                    dbc.Col(
                                        dcc.DatePickerSingle(
                                            id="date-input",
                                            min_date_allowed="2000-01-01",
                                            max_date_allowed="2100-12-31",
                                            initial_visible_month=pd.to_datetime(
                                                "today"
                                            ),
                                            date=pd.to_datetime("today").date(),
                                            display_format="YYYY-MM-DD",
                                        ),
                                        width=8,
                                    ),
                                ],
                                className="mb-3",
                            ),
                        ]
                    ),
                ]
            ),
            # Cancel and Submit buttons
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="close-add-stock",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button("Add Stock", id="submit-add-stock", color="primary"),
                ]
            ),
        ],
        id="modal-add-stock",
        is_open=False,  # Modal is closed by default
    )


def sell_stock_modal():
    """Returns a modal component for selling a stock from the portfolio"""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Sell Stock")),  # Title
            dbc.ModalBody(
                [
                    html.Div(id="sell-stock-error"),  # Placeholder to show errors
                    # Form containing all the inputs for selling a stock
                    dbc.Form(
                        [
                            # Dropdown to select stock to sell
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Stock Ticket",
                                        html_for="sell-ticket-input",
                                        width=4,
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="sell-ticket-input",
                                            placeholder="Select a stock...",
                                            clearable=False,  # Must select one, cannot clear
                                        ),
                                        width=8,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            # Quantity to sell input
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Quantity to Sell",
                                        html_for="sell-quantity-input",
                                        width=4,
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            id="sell-quantity-input",
                                            type="number",
                                            min=1,
                                            step=1,
                                            placeholder="Leave empty to sell all",
                                            invalid=False,
                                        ),
                                        width=8,
                                    ),
                                ],
                                className="mb-3",
                            ),
                        ]
                    ),
                ]
            ),
            # Cancel and Submit buttons
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="close-sell-stock",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button("Sell Stock", id="submit-sell-stock", color="primary"),
                ]
            ),
        ],
        id="modal-sell-stock",
        is_open=False,  # Modal is closed by default
    )