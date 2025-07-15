import dash_bootstrap_components as dbc


def create_mover_card(mover_type, title):
    """
    Creates a Bootstrap card component used to display stock movers (like Top Gainers, Top Losers, etc.)

    Args:
        mover_type (str): Identifier used to assign unique IDs to each card content area.
        title (str): The display title for the card (ex: "Top Gainers").

    Returns:
        dbc.Card: A styled Bootstrap card component.
    """
    return dbc.Card(
        [
            # Card Header: shows the title at the top of the card
            dbc.CardHeader(
                title,
                className="py-2 border-0",
                style={
                    "fontSize": "1.25rem",
                    "fontWeight": "700",
                    "backgroundColor": "#212529",
                },
            ),
            # Card Body: area where stock data will be dynamically inserted via callbacks
            dbc.CardBody(
                id=f"{mover_type}-content",  # Unique ID for each card body ("gainers-content", etc.)
                className="py-3 px-3 text-white",
                style={
                    "fontSize": "1.1rem",
                    "fontWeight": "500",
                    "minHeight": "200px",
                    "backgroundColor": "#212529",
                },
            ),
        ],
        id=f"{mover_type}-card",  # Unique ID for the entire card
        className="bg-dark shadow-sm rounded mb-3",
        style={
            "width": "300px",
            "display": "inline-block",  # Align cards side by side
            "marginRight": "20px",  # Spacing between cards
            "verticalAlign": "top",
            "border": "none",
            "backgroundColor": "#212529",
        },
    )