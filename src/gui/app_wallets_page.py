import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dash
import dash_bootstrap_components as dbc

from gui.pages.wallets_layout import create_layout as create_wallets_layout
from gui.core.wallets_callbacks import register_wallets_callbacks

from stocktracker.wallet import Wallet

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True
)

# =============================================================================
# DEMO DATA SETUP - ORGANIZED BY MARKET SECTORS
# =============================================================================

def get_wallets():
    """Returns new wallet instances every time"""
    
    tech_wallet = Wallet("Tech Titans")
    tech_wallet.add_stock("AAPL", 15, 182.63, "2025-6-3")
    tech_wallet.add_stock("MSFT", 8, 402.15, "2025-5-15")
    tech_wallet.add_stock("NVDA", 5, 118.11, "2025-6-12")
    tech_wallet.add_stock("GOOG", 21, 200.00, "2025-6-12")

    finance_wallet = Wallet("Banking & Finance")
    finance_wallet.add_stock("JPM", 12, 195.34, "2025-5-20")
    finance_wallet.add_stock("BAC", 20, 37.52, "2025-6-1")
    finance_wallet.add_stock("GS", 5, 453.27, "2025-5-28")

    auto_wallet = Wallet("Auto Innovators")
    auto_wallet.add_stock("TSLA", 10, 177.48, "2025-6-3")
    auto_wallet.add_stock("F", 50, 12.06, "2025-5-10")
    auto_wallet.add_stock("GM", 30, 46.25, "2025-5-18")

    list_wallets = [tech_wallet, finance_wallet, auto_wallet]
    
    return list_wallets

# =============================================================================
# APPLICATION SETUP
# =============================================================================
wallets_l = get_wallets()
# Initialize application layout with wallets view
app.layout = create_wallets_layout(wallets_l)
# Register all wallet-related callbacks
register_wallets_callbacks(app, wallets_l)

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=True)