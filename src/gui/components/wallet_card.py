from dash import html
import dash_bootstrap_components as dbc
from stocktracker.wallet import Wallet

def wallet_card(wallet, index):
    # NÃO chame wallet.update_wallet_status() aqui!
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.H5(wallet.name, className="mb-0 d-inline"),
                        dbc.Button(
                            html.Span("⋮"),
                            id={
                                'type': 'wallet-menu-btn',
                                'index': index
                            },
                            className="float-end btn-sm",
                            n_clicks=0,
                            color="link",
                            style={
                                'padding': '0 0.5rem',
                                'fontSize': '1.25rem',
                                'lineHeight': '1',
                                "borderBottom": "none"
                            }
                        )
                    ],
                    className="position-relative",
                    style={
                        "backgroundColor": "#212529",
                        "borderBottom": "none"}
                ),
                style={
                    "backgroundColor": "#212529",
                    "borderBottom": "none"}
            ),
            dbc.CardBody(
                [
                    html.P(f"Stocks: {len(wallet.stocks)}", className="card-text"),
                    html.P(f"Total Value: ${wallet.total_value:,.2f}", className="card-text"),
                    dbc.Button(
                        "View Details",
                        href=f"/stocks/{index}",
                        color="primary",
                        outline=True,
                        className="mt-2"
                    )
                ],
                style={"backgroundColor": "#212529"}
            )
        ],
        className="h-100",
        style={
            "backgroundColor": "#212529",
            "border": "none",}
    )