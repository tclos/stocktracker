import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import required Dash components
from dash import html, dcc
import dash_bootstrap_components as dbc

# Import custom components
from gui.components.sidebar import sidebar
from gui.components.wallets_modals import create_wallet_modal, delete_wallet_modal
from gui.components.wallet_card import wallet_card

def create_layout(wallets):
    """
    Creates and returns the wallets overview layout.
    
    Args:
        wallets: List of Wallet objects to display
        
    Returns:
        A Dash HTML Div
    """
    # Create a responsive card for each wallet with its index
    wallet_cards = [
        dbc.Col(
            wallet_card(wallet, index),  # Each card gets wallet object and its index
            md=4,                        # Medium screens show 3 cards per row (12/4)
            className="mb-4"
        )
        for index, wallet in enumerate(wallets)     # Generate cards for all wallets
    ]

    # Main content area (right side of sidebar)
    content = html.Div(
        [
            # Location component tracks URL changes (used for modal initialization)
            
            html.H2("Your Wallets", className="mb-4"),  # Title
            
            # Primary action button - triggers create wallet modal
            dbc.Button(
                "Create New Wallet",
                id="create-wallet-button",  # Matches callback input
                color="success",
                outline=True,
                className="me-2",
                style={"margin-bottom": "1rem"}
            ),
            
            # Responsive grid of wallet cards
            dbc.Row(
                wallet_cards,               # All generated wallet cards
                id="wallets-container"      # ID for dynamic updates
            ),
            
            # Modals (initially hidden)
            create_wallet_modal(),          # Wallet creation form
            delete_wallet_modal(),          # Delete confirmation
            
            # Client-side storage for managing wallets:
            dcc.Store(
                id="wallet-to-delete",      # Stores index of wallet to delete
                data=None                   # Initially empty
            ),
        ],
        style={
            "margin-left": "17rem",
            "padding": "2rem 1rem"
        }
    )
    
    return html.Div([sidebar(), content])