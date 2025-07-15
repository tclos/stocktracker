import yfinance as yf
from curl_cffi import requests

class StockAPI:
    def __init__(self):
        self.session = requests.Session(impersonate="chrome")

    def get_stock_data(self, ticket: str):
        return yf.Ticker(ticket, session=self.session)

    def get_history(self, ticket: str, start_date: str):
        return self.get_stock_data(ticket).history(start=start_date)

    def get_sector(self, ticket: str):
        return self.get_stock_data(ticket).info.get('sector', 'Unknown')

    def get_current_price(self, ticket: str, start_date: str):
        history = self.get_history(ticket, start_date)
        if history.empty:
            raise ValueError(f"No data for the date: {start_date}")
        return history["Open"].iloc[0]

    def get_latest_price(self, ticket: str, start_date: str):
        history = self.get_history(ticket, start_date)
        # Se não há dados, tente buscar até hoje
        if history.empty:
            # Tenta buscar até hoje
            from datetime import datetime
            today = datetime.today().strftime("%Y-%m-%d")
            history = self.get_history(ticket, start_date)
            if history.empty:
                raise ValueError(f"No data for the date: {start_date}")
        # Garante que pega o último valor disponível
        return history["Close"].iloc[-1], history["High"].max(), history["Low"].min()