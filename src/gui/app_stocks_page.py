import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dash
import dash_bootstrap_components as dbc

from gui.pages.stocks_layout import create_layout
from gui.core.stocks_callbacks import register_stocks_callbacks

from stocktracker.wallet import Wallet

# Initialize the Dash application with configuration
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True
)

# =============================================================================
# DEMO WALLET SETUP
# =============================================================================
# Initialize wallet
tech_wallet = Wallet("Tech Titans")
tech_wallet.add_stock("AAPL", 15, 182.63, "2025-6-3")   # Apple Inc.
tech_wallet.add_stock("MSFT", 8, 402.15, "2025-5-15")   # Microsoft
tech_wallet.add_stock("NVDA", 5, 118.11, "2025-6-12")   # NVIDIA
tech_wallet.add_stock("GOOG", 21, 200.00, "2025-6-12")   # Google

# =============================================================================
# APPLICATION SETUP
# =============================================================================
# Configure the application layout using the wallet layout creator
app.layout = create_layout(tech_wallet)

register_stocks_callbacks(app, tech_wallet)

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=True)
