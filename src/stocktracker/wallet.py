from stocktracker.stock import Stock
import pandas as pd

import yfinance as yf


class Wallet:

    # Lista de acoes e suas quantidades que o usuario possui.

    def __init__(self, name: str):
        self.name = name
        self.stocks = {}  # dicionario que aponta para o objeto acao
        self.total_value = (
            0  # somatorio dos valores de cada acao no momento que o usuario abre o app
        )
        self.total_spent = 0  # valor gasto na compra das acoes ate entao. Valorizacao = valor_total - valor_gasto
        self.total_gain = 0  # valorizacao de cada acao esta em percentual. Falta ver como representar isso numa carteira com distribuições desiguais de valor entre ativos
        self.total_quantity = 0 #n tipos diferentes de ativos na carteira
        self.tickets_count = 0 # somatorio da quantidade de cada ativo

    def add_stock(self, stock: str, n_stocks: int, price: float, data_compra: str = None):
        # antes verifica se ja exsite este stock no dicionario
        # se nao, inicializa classe stock

        # PROBLEMA: devemos fazer com que o cara possa comprar a acao X mais de uma vez e salvar os precos de compra diferentes
        # Deve receber uma data de compra e salvar o valor pago junto com a quantidade de ativos comprados para cada vez que o usuario add ativos na carteira

        if stock in self.stocks:
            # self.stocks[stock].numero_acoes += n_stocks
            # self.stocks[stock].atualiza_valor_gasto(n_stocks, data_compra)
            # self.stocks[stock].atualiza_status_acao()
            self.stocks[stock].add_purchase(data_compra, n_stocks, price)

        else:
            self.stocks[stock] = Stock(stock, n_stocks, price, data_compra)

    def remove_stock(self, stock: str, n_stocks: int = None):
        self.update_wallet_status()

        if stock not in self.stocks:
            print(f"Stock: {stock} is not in the wallet.")
            return

        stock_quantity = self.stocks[stock].quantity

        if n_stocks is None:
            # Remove tudo
            self.total_value -= self.stocks[stock].current_value * stock_quantity
            self.total_spent -= self.stocks[stock].total_spent
            del self.stocks[stock]

        elif n_stocks < stock_quantity:
            removed, spent_removed = self.stocks[stock].sell(n_stocks)
            self.total_spent -= spent_removed
            self.total_value -= self.stocks[stock].current_value * removed

        elif n_stocks == stock_quantity:
            self.total_value -= self.stocks[stock].current_value * stock_quantity
            self.total_spent -= self.stocks[stock].total_spent
            del self.stocks[stock]

        else:
            raise ValueError("Attempting to remove more shares than are available in your wallet.")

    def clear(self):
        self.stocks.clear()

    def generate_report(self):
        # usar stock info pra add % de cada setor etc
        # https://www.geeksforgeeks.org/what-is-yfinance-library/
        self.update_wallet_status()

        print(f"Total shares: {self.total_quantity}")
        print(f"Number of tickers: {self.tickets_count}")
        print(f"Total spent: ${self.total_spent:.2f}")
        print(f"Current total value: ${self.total_value:.2f}")
        print(f"Portfolio gain: {self.total_gain:.2f}%")

    def update_wallet_status(self):
        # Atualiza valor atual e valor gasto da carteira
        for stock in self.stocks.values():
            stock.update_stock_status()

        self.total_value = sum(
            stock.current_value * stock.quantity for stock in self.stocks.values()
        )
        self.total_spent = sum(stock.total_spent for stock in self.stocks.values())
        self.total_quantity = len(self.stocks)
        self.tickets_count = sum(stock.quantity for stock in self.stocks.values())

        # Valorização = ((valor_atual - valor_gasto) / valor_gasto) * 100
        if self.total_spent > 0:
            self.total_gain = (
                (self.total_value - self.total_spent) / self.total_spent
            ) * 100  # Em porcentagem
        else:
            self.total_gain = 0.0

    def print_stock_details(self):
        self.update_wallet_status()
        for ticket, stock in self.stocks.items():
            print(f"Ticket: {ticket}")
            print(f"  Total quantity: {stock.quantity}")
            print(f"  Total spent: {stock.total_spent:.2f}")
            print(f"  Current value: {stock.current_value:.2f}")
            print(f"  Current total value: {stock.current_value * stock.quantity:.2f}")
            print(f"  Gain (%): {stock.gain:.2f}%")
            print(f"  Purchases:")
            for data_compra, compra in stock.purchases.items():
                print(
                    f"    Date: {data_compra}, Quantity: {compra.quantity}, Purchase price: {compra.price:.2f}"
                )
    
    def to_dataframe(self):
        data = []
        for ticket, acao in self.stocks.items():
            preco_medio = acao.total_spent / acao.quantity if acao.quantity > 0 else 0
            valorizacao = (
                ((acao.current_price * acao.quantity - acao.total_spent) / acao.total_spent) * 100
                if acao.total_spent > 0 else 0
            )
            data.append({
                "Ticket": ticket,
                # "Setor": acao.sector,
                "Quantidade": acao.quantity,
                "Preço Médio": preco_medio,
                "Preço Atual": acao.current_price,
                "Valor Atual": acao.current_price * acao.quantity,
                "Valor Gasto": acao.total_spent,
                "Valorização (%)": valorizacao,
                # "Data Compra(s)": list(acao.purchases.keys()),
            })

        df = pd.DataFrame(data)
        return df
    
    def get_performance_history(self, days=None):
        """
        Retorna uma Series com o valor total da carteira para cada dia útil dos últimos `days` dias,
        considerando a data de aquisição de cada ação.
        """
        min_purchase_date = None
        for stock in self.stocks.values():
            for purchase_date in stock.purchases.keys():
                pd_date = pd.to_datetime(purchase_date)
                if min_purchase_date is None or pd_date < min_purchase_date:
                    min_purchase_date = pd_date

        end_date = pd.to_datetime("today")
        
        # If no purchases found and no days specified, return empty Series
        if min_purchase_date is None and days is None:
            return pd.Series(dtype=float)
        
        if min_purchase_date is None:
            start_date = end_date - pd.Timedelta(days=days if days else 30)
        else:
            start_date = min_purchase_date
            if days:
                # Ensure we have at least N days of history
                start_date = min(start_date, end_date - pd.Timedelta(days=days))

        date_range = pd.date_range(start=start_date, end=end_date, freq="B")
        if not self.stocks:
            # Carteira vazia: retorna série zerada
            return pd.Series([0]*len(date_range), index=date_range)

        df = pd.DataFrame(index=date_range)

        for ticket, stock in self.stocks.items():
            hist = stock.api.get_history(ticket, start_date.strftime("%Y-%m-%d"))
            if hist.empty or "Close" not in hist.columns:
                continue

            hist.index = hist.index.tz_localize(None) if hist.index.tzinfo else hist.index
            hist.index = hist.index.normalize()
            hist = hist.reindex(df.index).ffill()

            qty_series = pd.Series(0, index=df.index)
            for purchase_date, purchase in stock.purchases.items():
                purchase_date = pd.to_datetime(purchase_date)
                qty_series.loc[qty_series.index >= purchase_date] += purchase.quantity

            df[ticket] = hist["Close"] * qty_series

        # Se não há nenhuma coluna (nenhum ativo válido), retorna zeros
        if df.empty or df.sum(axis=1).sum() == 0:
            return pd.Series([0]*len(date_range), index=date_range)

        df["Total"] = df.sum(axis=1, skipna=True)
        # Se todos os valores são zero até a data da primeira compra, mas depois há valores, mantém a série
        if df["Total"].sum() == 0:
            cutoff_date = end_date - pd.Timedelta(days=days)
            return df["Total"].loc[df.index >= cutoff_date]
        return df["Total"]

