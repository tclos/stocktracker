import sys
import os

os.environ["DASH_DEBUG"] = "False"  # Disables caching

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from gui.pages.home_layout import create_layout as create_home_layout
from gui.pages.wallets_layout import create_layout as create_wallets_layout
from gui.pages.stocks_layout import create_layout as create_stocks_layout
from gui.core.wallets_callbacks import register_wallets_callbacks
from gui.core.stocks_callbacks import register_stocks_callbacks
from gui.core.home_callbacks import register_home_callbacks

from stocktracker.wallet import Wallet

# Initialize the app
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True
)


# =============================================================================
# DEMO DATA SETUP
# =============================================================================
def get_wallets():
    """Returns new wallet instances every time"""
    
    tech_wallet = Wallet("Tech Titans")
    tech_wallet.add_stock("AAPL", 15, 182.63, "2024-06-03")
    tech_wallet.add_stock("MSFT", 8, 402.15, "2024-05-15")
    tech_wallet.add_stock("NVDA", 5, 118.11, "2024-06-12")
    tech_wallet.add_stock("GOOG", 21, 200.00, "2024-06-12")

    finance_wallet = Wallet("Banking & Finance")
    finance_wallet.add_stock("JPM", 12, 195.34, "2024-05-20")
    finance_wallet.add_stock("BAC", 20, 37.52, "2024-05-31")  # Sexta-feira (dia útil)
    finance_wallet.add_stock("GS", 5, 453.27, "2024-05-28")

    auto_wallet = Wallet("Auto Innovators")
    auto_wallet.add_stock("TSLA", 10, 177.48, "2024-06-03")
    auto_wallet.add_stock("F", 50, 12.06, "2024-05-10")
    auto_wallet.add_stock("GM", 30, 46.25, "2024-05-18")

    list_wallets = [tech_wallet, finance_wallet, auto_wallet]
    
    return list_wallets

# =============================================================================
# APPLICATION LAYOUT
# =============================================================================
# Register all callbacks at startup
wallets_l = get_wallets()
register_wallets_callbacks(app, wallets_l)
register_stocks_callbacks(app, wallets_l)
register_home_callbacks(app)


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),  # Monitors URL for routing between pages
        html.Div(id="page-content",children=create_wallets_layout(wallets_l)),  # default page
        dcc.Store(id='current-wallet-store')    # Hidden component to store the active wallet (for state persistence)
    ]
)

# =============================================================================
# CALLBACKS
# =============================================================================


@app.callback(
    Output("page-content", "children"),  # Update the main page content
    Input("url", "pathname"),            # Triggered on URL change
)
def display_page(pathname):
    if pathname == "/":
        return create_home_layout()  # Home
    elif pathname == "/wallets":
        return create_wallets_layout(wallets_l)  # Explicit wallets route
    # If URL starts with /stocks/, try to extract wallet index from the path
    elif pathname and pathname.startswith("/stocks/"):
        try:
            wallet_index = int(pathname.split("/")[-1]) # Get the wallet index from the URL
            if 0 <= wallet_index < len(wallets_l):
                return create_stocks_layout(wallets_l[wallet_index])    # Show the selected wallet
        except (ValueError, IndexError):
            pass
        # Fallback to first wallet if invalid index
        return create_stocks_layout(wallets_l[0])
    
    # Default route: show the list of wallets
    return create_wallets_layout(wallets_l)


# =============================================================================
# RUN THE APP
# =============================================================================
if __name__ == "__main__":
    app.run(debug=True, dev_tools_ui=False, dev_tools_hot_reload=False)
