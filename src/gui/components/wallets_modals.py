import dash_bootstrap_components as dbc


def create_wallet_modal():
    """
    Creates and returns the 'Create New Wallet' modal.

    Returns:
        Modal
    """
    return dbc.Modal(
        [
            dbc.ModalHeader("Create New Wallet"),  # Modal Title
            dbc.ModalBody(
                dbc.Form(
                    [
                        dbc.Input(
                            id="new-wallet-name",  # ID referenced in callbacks
                            placeholder="Enter wallet name",
                            className="mb-3",
                        )
                    ]
                )
            ),
            dbc.ModalFooter(
                [
                    # Cancel button: closes modal without action
                    dbc.Button(
                        "Cancel",
                        id="close-create-wallet",
                        color="secondary",
                        className="me-2",
                    ),
                    # Create button: submits the form
                    dbc.Button("Create", id="submit-create-wallet", color="primary"),
                ]
            ),
        ],
        id="create-wallet-modal",   # Main modal ID for visibility control
        is_open=False,  # Initially hidden
    )


def delete_wallet_modal():
    """
    Creates and returns the 'Confirm Deletion' modal dialog.
    
    Returns:
        Modal
    """
    return dbc.Modal(
        [
            dbc.ModalHeader("Confirm Deletion"),    # Model Title
            dbc.ModalBody("Are you sure you want to delete this wallet?"),
            dbc.ModalFooter(
                [
                    # Cancel button: closes modal without action
                    dbc.Button(
                        "Cancel",
                        id="cancel-delete-wallet",
                        color="secondary",
                        className="me-2",
                    ),
                    # Delete button: confirms deletion
                    dbc.Button(
                        "Delete",
                        id="submit-delete-wallet",  # Changed to match your existing pattern
                        color="danger",
                    ),
                ]
            ),
        ],
        id="delete-wallet-modal",   # Main modal ID for visibility control
        is_open=False,  # Initially hidden
    )