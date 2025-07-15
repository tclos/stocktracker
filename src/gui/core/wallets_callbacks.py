import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Dash components
from dash import Input, Output, State, callback_context, no_update, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# Import custom components
from gui.components.wallet_card import wallet_card
from stocktracker.wallet import Wallet

def register_wallets_callbacks(app, wallets):
    """
    Registers all wallet-related Dash callbacks with separated modal controls
    
    Args:
        app: Dash application instance
        wallets: List of Wallet objects (shared state between callbacks)
    """

    # Callback for controlling opening and closing of delete wallet modal
    @app.callback(
        Output("delete-wallet-modal", "is_open"),   # Controls modal visibility
        Output("wallet-to-delete", "data"),         # Stores wallet index to delete
        Input({"type": "wallet-menu-btn", "index": ALL}, "n_clicks"),   # Menu buttons
        Input("submit-delete-wallet", "n_clicks"),  # Delete confirmation button
        Input("cancel-delete-wallet", "n_clicks"),  # Delete cancellation button
        prevent_initial_call=True
    )
    def control_delete_modal(menu_clicks, submit_click, cancel_click):
        """
        Handles opening/closing of delete confirmation modal.
        
        Returns:
            Tuple of (modal_is_open, wallet_index_to_delete)
        """
        ctx = callback_context
        if not ctx.triggered:   # No trigger event
            return PreventUpdate
        
        # Only proceed if button was actually clicked (n_clicks increased)
        if ctx.triggered[0]["value"] == 0:
            return no_update, no_update
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]  # Get which button was clicked
        
        if "wallet-menu-btn" in trigger_id:
            # Extract wallet index from the button ID
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            wallet_index = eval(button_id)["index"]
            #print(f"Opening delete modal for wallet index: {wallet_index}")  # Debug
            return True, wallet_index   # Open modal and store index
        
        elif trigger_id in ["submit-delete-wallet", "cancel-delete-wallet"]:
            #print(f"Closing modal via {trigger_id}") # Debug
            return False, None  # Close modal
            
        return False, None  # Default

    
    # Callback for deletion of wallet
    @app.callback(
        Output("wallets-container", "children", allow_duplicate=True),
        Input("submit-delete-wallet", "n_clicks"),  # Delete confirmation trigger
        State("wallet-to-delete", "data"),          # Wallet index to delete
        prevent_initial_call=True
    )
    def delete_wallet(_, wallet_index):
        """
        Executes wallet deletion and updates display.
        
        Args:
            _: Unused n_clicks value
            wallet_index: Index of wallet to delete (from State)
        """
        if wallet_index is not None and 0 <= wallet_index < len(wallets):
            #print(f"Deleting wallet at index: {wallet_index}")  # Debug
            del wallets[wallet_index]   # Remove wallet from list
        return update_wallets_display(wallets, _)   # Refresh display
    
    # Callback for creating wallet
    @app.callback(
        Output("create-wallet-modal", "is_open"),  # Modal visibility
        Output("new-wallet-name", "value"),        # Input field value
        Input("create-wallet-button", "n_clicks"),  # Open modal button
        Input("submit-create-wallet", "n_clicks"),  # Create confirmation
        Input("close-create-wallet", "n_clicks"),   # Cancel button
        State("new-wallet-name", "value"),         # Current input value
        prevent_initial_call=True
    )
    def control_create_modal(open_click, submit_click, close_click, name_value):
        """
        Handles create wallet modal visibility and form submission.
        
        Returns:
            Tuple of (modal_is_open, input_field_value)
        """
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "create-wallet-button":
            return True, no_update  # Open modal, keep current value
            
        if trigger_id == "submit-create-wallet":
            if name_value and name_value.strip():   # Validate input
                wallets.append(Wallet(name_value.strip()))  # Add new wallet
                return False, ""  # Close and clear on success
            return True, name_value  # Stay open if invalid
            
        return False, ""    # Close and clear for cancel/close

    # Callback for updating wallet cards display
    @app.callback(
        Output("wallets-container", "children"),    # Target the wallet cards container
        [Input("wallet-to-delete", "data"),         # Changes when wallet deleted
        Input("submit-create-wallet", "n_clicks")], # When new wallet added
        prevent_initial_call=True                   # Don't run on page load
    )
    def update_wallets_display(wallet_index, _):
        """
        Rebuilds the wallet cards display whenever wallets list changes.
        Returns list of wallet card components in a responsive grid.
        """
        return [
            dbc.Col(
                wallet_card(wallet, i), # Create card for each wallet
                md=4,                   # 3 cards per row on medium screens
                className="mb-4"
            )
            for i, wallet in enumerate(wallets) # Process all wallets
        ] 