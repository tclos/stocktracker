import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from dash import dcc, html, Input, Output, State, callback_context, no_update, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

import yfinance as yf

from stocktracker.performancereport import performancereport


def get_benchmark_history(benchmark_ticket, start_date, end_date):
    benchmark = yf.Ticker(benchmark_ticket)
    hist = benchmark.history(start=start_date, end=end_date)
    if hist.empty or "Close" not in hist.columns:
        return None
    hist.index = hist.index.tz_localize(None) if hist.index.tzinfo else hist.index
    hist.index = hist.index.normalize()
    return hist["Close"]


def register_stocks_callbacks(app, wallets):
    """
    Register all callbacks for the Dash application.

    Args:
        app: The Dash application instance
        wallet: The wallet object containing stock portfolio data
    """

    # Store the current wallet ID in a dcc.Store component
    @app.callback(
        Output("current-wallet-store", "data"),
        Input("url", "pathname"),
        State("current-wallet-store", "data"),
        prevent_initial_call=True
    )
    def update_current_wallet(pathname, current_data):
        """Extract wallet index from URL and store it"""
        if pathname.startswith("/stocks/"):
            try:
                wallet_index = int(pathname.split("/")[-1])
                if wallet_index < 0 or wallet_index >= len(wallets):
                    return current_data or {}
                return {"wallet_index": wallet_index}
            except ValueError:
                return current_data or {}
        return current_data or {}

    # Get the current wallet based on stored index
    def get_current_wallet(wallet_data):
        if not wallet_data or "wallet_index" not in wallet_data:
            return None
        
        wallet_index = wallet_data["wallet_index"]
        try:
            return wallets[wallet_index]
        except IndexError:
            return None
    
    
    # Callback to toggle the add stock modal open/close state
    @app.callback(
        Output("modal-add-stock", "is_open"),  # Controls modal visibility
        [
            Input("open-add-stock", "n_clicks"),
            Input("close-add-stock", "n_clicks"),
        ],  # Triggered by these buttons
        [State("modal-add-stock", "is_open")],  # Current state of modal
        prevent_initial_call=True,  # Prevents callback from firing on page load
    )
    def toggle_add_stock_modal(open_click, close_click, is_open):
        """Toggle the visibility of the add stock modal."""
        if open_click or close_click:  # If either button was clicked
            return not is_open  # Toggle the current state
        return is_open  # Return current state if no relevant clicks

    @app.callback(
        Output("modal-add-stock", "is_open", allow_duplicate=True),  # Can close modal
        Output("stock-list", "children"),  # Refresh the stock list display
        Output(
            "wallet-performance", "figure", allow_duplicate=True
        ),  # Update performance chart
        Output("add-stock-error", "children"),  # Display error messages
        Input("submit-add-stock", "n_clicks"),  # Triggered by submit button
        [
            State("stock-ticket-input", "value"),  # Stock symbol input
            State("quantity-input", "value"),  # Number of shares
            State("price-input", "value"),  # Purchase price
            State("date-input", "date"),  # Purchase date
            State("wallet-performance", "figure"),  # Current chart state
            State("current-wallet-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_stock(submit_clicks, ticket, quantity, price, date, current_figure, wallet_data):
        """Handle adding new stocks to the portfolio."""
        if not submit_clicks:  # If callback triggered without button click
            raise PreventUpdate  # Don't update anything
        
        wallet = get_current_wallet(wallet_data)
        if not wallet:
            return (
                True,
                no_update,
                no_update,
                dbc.Alert("No wallet selected or wallet not found", color="danger"),
            )

        error_message = ""

        try:
            # Validate stock ticket input
            if not ticket or not isinstance(ticket, str) or len(ticket.strip()) == 0:
                raise ValueError("Please enter a valid stock ticket")

            # Validate and convert quantity
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be a positive integer")
            except (TypeError, ValueError):
                raise ValueError("Please enter a valid quantity")

            # Validate and convert price
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive number")
            except (TypeError, ValueError):
                raise ValueError("Please enter a valid price")

            # Validate and format date
            try:
                if not date:
                    raise ValueError("Please select a purchase date")

                purchase_date = pd.to_datetime(date).strftime("%Y-%m-%d")

                if pd.to_datetime(purchase_date) > pd.to_datetime("today"):
                    raise ValueError("Purchase date cannot be in the future")
            except (TypeError, ValueError):
                raise ValueError("Please enter a valid date (YYYY-MM-DD)")

            # All validations passed - add the stock to wallet
            wallet.add_stock(
                ticket.strip().upper(),  # Standardize ticket format
                quantity,  # Number of shares
                price,  # Purchase price
                purchase_date,  # Formatted purchase date
            )

            # Create updated stock list display
            # !!! Extract function from this !!
            wallet_df = wallet.to_dataframe()
            updated_stock_list = dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        dbc.Row(
                            [
                                dbc.Col(html.H6(row["Ticket"]), width=4),
                                dbc.Col(
                                    html.Div(
                                        [
                                            html.Small(f"{row['Quantidade']} shares"),
                                            html.Br(),
                                            html.Small(
                                                f"${row['Valor Atual']:.2f}",
                                                className="text-muted",
                                            ),
                                        ]
                                    ),
                                    width=8,
                                ),
                            ]
                        ),
                        id={"type": "stock-item", "index": i},
                        action=True,
                        className="px-3 py-2",
                    )
                    for i, row in wallet_df.iterrows()  # Create item for each stock
                ],
                flush=True,  # Removes borders for cleaner look
                id="stock-list",  # refresh tracking
            )

            # Return success state
            return (
                False,  # Close modal
                updated_stock_list,  # Show updated stock list
                current_figure,  # Pass through chart state
                "",  # no error message
            )

        except ValueError as e:  # Handle validation errors
            error_message = str(e)
            return (
                True,  # Keep modal open
                no_update,  # Don't update stock list
                no_update,  # Don't update chart
                dbc.Alert(error_message, color="danger"),  # Show error message
            )
        except Exception as e:
            return (
                True,  # Keep modal open
                no_update,
                no_update,
                dbc.Alert(
                    f"An unexpected error occurred: {str(e)}", color="danger"
                ),  # error message
            )

    # Callback to toggle sell stock modal
    @app.callback(
        Output("modal-sell-stock", "is_open"),
        [Input("open-sell-stock", "n_clicks"), Input("close-sell-stock", "n_clicks")],
        [State("modal-sell-stock", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_sell_stock_modal(open_click, close_click, is_open):
        """Toggle the visibility of the sell stock modal."""
        if open_click or close_click:
            return not is_open
        return is_open

    # Callback to handle selling stocks
    @app.callback(
        Output("modal-sell-stock", "is_open", allow_duplicate=True),
        Output(
            "stock-list", "children", allow_duplicate=True
        ),  # To refresh the stock list
        Output("wallet-performance", "figure", allow_duplicate=True),
        Output("sell-quantity-input", "invalid"),  # Show validation state
        Output("sell-stock-error", "children"),  # Error messages
        Input("submit-sell-stock", "n_clicks"),  # Submit button
        [
            State("sell-ticket-input", "value"),  # Selected stock
            State("sell-quantity-input", "value"),  # Quantity to sell
            State("wallet-performance", "figure"),  # Current chart
            State("current-wallet-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def sell_stock(submit_clicks, ticket, quantity, current_figure, wallet_data):
        """Handle selling stocks from the portfolio."""
        if not submit_clicks:
            raise PreventUpdate
        
        wallet = get_current_wallet(wallet_data)
        if not wallet:
            return (
                True,
                no_update,
                no_update,
                False,
                dbc.Alert("No wallet selected or wallet not found", color="danger"),
            )

        quantity_invalid = False  # Track quantity validation
        error_message = ""

        try:
            # Validate stock selection
            if not ticket:
                raise ValueError("Please select a stock to sell")

            # Handle quantity (None means sell all)
            quantity = int(quantity) if quantity else None

            # Validate quantity
            if quantity is not None and quantity <= 0:
                quantity_invalid = True
                raise ValueError("Quantity must be a positive integer")

            # Sell the stock
            wallet.remove_stock(
                stock=ticket.strip().upper(), n_stocks=quantity  # None = sell all
            )

            # Refresh stock list display
            wallet_df = wallet.to_dataframe()
            updated_stock_list = dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        dbc.Row(
                            [
                                dbc.Col(html.H6(row["Ticket"]), width=4),
                                dbc.Col(
                                    html.Div(
                                        [
                                            html.Small(f"{row['Quantidade']} shares"),
                                            html.Br(),
                                            html.Small(
                                                f"${row['Valor Atual']:.2f}",
                                                className="text-muted",
                                            ),
                                        ]
                                    ),
                                    width=8,
                                ),
                            ]
                        ),
                        id={"type": "stock-item", "index": i},
                        action=True,
                        className="px-3 py-2",
                    )
                    for i, row in wallet_df.iterrows()  # Create item for each stock
                ],
                flush=True,  # Removes borders for cleaner look
            )

            # Return success state
            return (
                False,  # Close modal
                updated_stock_list,  # Updated stock list
                current_figure,  # chart state
                False,  # Reset quantity validation
                "",  # Clear error message
            )

        except ValueError as e:  # Handle validation errors
            error_message = str(e)
            return (
                True,  # Keep modal open
                no_update,  # Don't update stock list
                no_update,  # Don't update chart
                quantity_invalid,
                dbc.Alert(error_message, color="danger"),  # Show error message
            )
        except Exception as e:  # Handle unexpected errors
            error_message = f"An unexpected error occurred: {str(e)}"
            return (
                True,
                no_update,
                no_update,
                quantity_invalid,
                dbc.Alert(f"An unexpected error occurred: {str(e)}", color="danger"),
            )

    # Callback to update sell stock dropdown options
    @app.callback(
    Output("sell-ticket-input", "options"),  # Dropdown options
    Input("stock-list", "children"),  # Trigger when stock list changes
    State("current-wallet-store", "data"),
    )
    def update_sell_stock_dropdown(_, wallet_data):
        wallet = get_current_wallet(wallet_data)
        if not wallet:
            return []
        
        wallet_df = wallet.to_dataframe()
        # Corrigido: só retorna opções se houver ações e a coluna existir
        if wallet_df.empty or "Ticket" not in wallet_df.columns:
            return []
        options = [
            {"label": stock, "value": stock} for stock in wallet_df["Ticket"].unique()
        ]
        return options

    @app.callback(
        Output("stock-historic", "figure"),
        Output("stock-historic-frame", "style"),
        Output("stock-historic-title", "children"),
        Input({"type": "stock-item", "index": ALL}, "n_clicks"),
        [State("stock-list", "children"),
        State("current-wallet-store", "data")],
        prevent_initial_call=True,
    )
    def show_stock_chart(n_clicks_list, stock_list_children, wallet_data):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        wallet = get_current_wallet(wallet_data)
        if not wallet:
            raise PreventUpdate

        # Pega o id do item clicado
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        try:
            triggered_id_dict = eval(triggered_id)
        except Exception:
            raise PreventUpdate

        if not isinstance(triggered_id_dict, dict) or triggered_id_dict.get("type") != "stock-item":
            raise PreventUpdate

        clicked_idx = triggered_id_dict.get("index")
        wallet_df = wallet.to_dataframe()
        if clicked_idx is None or clicked_idx >= len(wallet_df):
            raise PreventUpdate
        
        ticket = wallet_df.iloc[clicked_idx]["Ticket"]
        # Busca historico de preços (ultimos 30 dias)
        stock = wallet.stocks.get(ticket)
        if not stock:
            raise PreventUpdate

        api = stock.api
        end_date = pd.to_datetime("today")
        start_date = end_date - pd.Timedelta(days=30)
        hist = api.get_history(ticket, start_date.strftime("%Y-%m-%d"))
        if hist.empty:
            fig = go.Figure()
            fig.update_layout(title=f"No data for {ticket}")
            return fig, {"display": "block"}, f""            # f"{ticket} - Últimos 30 dias" # Título

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name=ticket
        ))
        fig.update_layout(
            title=f"{ticket} - Últimos 30 dias",
            xaxis_title="Data",
            yaxis_title="Preço de Fechamento",
            plot_bgcolor="#1e1e1e",
            paper_bgcolor="#1e1e1e",
            font={"color": "white"},
        )
        return fig, {"display": "block"}, f""           # f"{ticket} - Últimos 30 dias" # Título
    
    # Display stock details
    @app.callback(
        Output("stock-details", "children"),
        Input({"type": "stock-item", "index": ALL}, "n_clicks"),
        State("current-wallet-store", "data"),
        prevent_initial_call=True
    )
    def display_stock_details(n_clicks_list, wallet_data):
        ctx = callback_context
        if not ctx.triggered:
            return ""
        
        wallet = get_current_wallet(wallet_data)
        if not wallet:
            return ""
        
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        index = eval(triggered_id)["index"]
        stock = wallet.to_dataframe().iloc[index]
        return dbc.Card([
            dbc.CardHeader(f"Details for {stock['Ticket']}"),
            dbc.CardBody([
                html.P(f"Quantity: {stock['Quantidade']}"),
                html.P(f"Preço Médio: ${stock['Preço Médio']:.2f}"),
                html.P(f"Preço Atual: ${stock['Preço Atual']:.2f}"),
                html.P(f"Valorização (%): {stock['Valorização (%)']:.2f}"),
                # !!!!!Add more info later
                #html.P(f"Purchase Date: {stock['Purchase Date']}"),
            ])
        ])

    @app.callback(
    Output("wallet-performance", "figure"),
    Input("benchmark-dropdown", "value"),
    State("current-wallet-store", "data"),
    prevent_initial_call=False 
    )
    def update_wallet_performance(benchmark_ticket, wallet_data):
        wallet = get_current_wallet(wallet_data)
        if not wallet:
            return go.Figure()

        wallet_history = wallet.get_performance_history()

        # Se a carteira está vazia (todos os valores zero)
        if wallet_history.empty or wallet_history.sum() == 0:
            fig = go.Figure()
            fig.update_layout(
                title="Nenhum dado para exibir",
                xaxis_title="Data",
                yaxis_title="Valor Total (R$)",
                plot_bgcolor="#1e1e1e",
                paper_bgcolor="#1e1e1e",
                font={"color": "white"},
            )
            return fig

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=wallet_history.index,
            y=wallet_history.values,
            mode="lines",
            name="Carteira"
        ))

        # Adiciona o benchmark se selecionado
        if benchmark_ticket and benchmark_ticket != "none":
            start_date = wallet_history.index[0].strftime("%Y-%m-%d")
            end_date = wallet_history.index[-1].strftime("%Y-%m-%d")
            benchmark_prices = get_benchmark_history(benchmark_ticket, start_date, end_date)
            if benchmark_prices is not None:
                benchmark_prices = benchmark_prices.reindex(wallet_history.index).ffill()
                
                # Calculate hypothetical benchmark investment based on actual purchase dates/amounts
                benchmark_value = pd.Series(0.0, index=wallet_history.index)
                total_shares = 0.0
                
                # Collect all purchases across all stocks
                all_purchases = []
                for stock in wallet.stocks.values():
                    for date, purchase in stock.purchases.items():
                        all_purchases.append({
                            'date': pd.to_datetime(date),
                            'amount': purchase.price * purchase.quantity
                        })
                
                # Sort purchases by date
                all_purchases.sort(key=lambda x: x['date'])
                
                # Simulate investing same amounts in benchmark at same times
                for purchase in all_purchases:
                    if purchase['date'] in benchmark_prices.index:
                        price = benchmark_prices.loc[purchase['date']]
                        if price > 0:
                            shares_bought = purchase['amount'] / price
                            total_shares += shares_bought
                            # Update benchmark value from this point forward
                            mask = benchmark_value.index >= purchase['date']
                            benchmark_value[mask] += shares_bought * benchmark_prices[mask]
                
                # If no purchases (shouldn't happen if wallet has value), normalize by initial value
                if not all_purchases and not benchmark_prices.empty:
                    initial_ratio = wallet_history.iloc[0] / benchmark_prices.iloc[0]
                    benchmark_value = benchmark_prices * initial_ratio
                
                fig.add_trace(go.Scatter(
                    x=benchmark_value.index,
                    y=benchmark_value.values,
                    mode="lines",
                    name=f"{benchmark_ticket}",
                    line=dict(color='#EF553B'),
                    hovertemplate="%{y:.2f} R$<extra></extra>"
                ))

        fig.update_layout(
            title="Valor da Carteira vs Benchmark",
            xaxis_title="Data",
            yaxis_title="Valor Total (R$)",
            plot_bgcolor="#1e1e1e",
            paper_bgcolor="#1e1e1e",
            font={"color": "white"},
        )
        return fig
    

    @app.callback(
        Output("download-metrics", "data"),
        Input("download-metrics-btn", "n_clicks"),
        State("current-wallet-store", "data"),
        prevent_initial_call=True
    )
    def download_metrics(n_clicks, wallet_data):
        if n_clicks > 0 and wallet_data:
            wallet = get_current_wallet(wallet_data)
            # Generate the metrics report
            metrics_filename = f"{wallet.name.lower().replace(' ', '-')}_metrics.txt"
            performancereport.generate_metrics_report(wallet, metrics_filename)
            filepath = os.path.join(performancereport.get_data_path(), metrics_filename)
            
            # Return as downloadable file
            return dcc.send_file(filepath)
        return None

    @app.callback(
        Output("download-purchases", "data"),
        Input("download-purchases-btn", "n_clicks"),
        State("current-wallet-store", "data"),
        prevent_initial_call=True
    )
    def download_purchases(n_clicks, wallet_data):
        if n_clicks > 0 and wallet_data:
            wallet = get_current_wallet(wallet_data)
            # Generate the purchase history
            metrics_filename = f"{wallet.name.lower().replace(' ', '-')}_purchases.csv"
            performancereport.generate_purchase_history(wallet, metrics_filename)
            filepath = os.path.join(performancereport.get_data_path(), metrics_filename)
            
            # Return as downloadable file
            return dcc.send_file(filepath)
        return None

    @app.callback(
        Output("download-assets", "data"),
        Input("download-assets-btn", "n_clicks"),
        State("current-wallet-store", "data"),
        prevent_initial_call=True
    )
    def download_assets(n_clicks, wallet_data):
        if n_clicks > 0 and wallet_data:
            wallet = get_current_wallet(wallet_data)
            # Generate the assets listing
            metrics_filename = f"{wallet.name.lower().replace(' ', '-')}_assets.csv"
            performancereport.generate_assets_listing(wallet, metrics_filename)
            filepath = os.path.join(performancereport.get_data_path(), metrics_filename)
            
            # Return as downloadable file
            return dcc.send_file(filepath)
        return None
    
    @app.callback(
        Output("download-csv", "data"),
        Input("download-csv-btn", "n_clicks"),
        State("current-wallet-store", "data"),
        prevent_initial_call=True
    )
    def download_csv(n_clicks, wallet_data):
        if n_clicks > 0 and wallet_data:
            wallet = get_current_wallet(wallet_data)
            # Generate the full CSV report
            metrics_filename = f"{wallet.name.lower().replace(' ', '-')}_portfolio.csv"
            performancereport.generate_csv_report(wallet, metrics_filename)
            filepath = os.path.join(performancereport.get_data_path(), metrics_filename)
            
            # Return as downloadable file
            return dcc.send_file(filepath)
        return None