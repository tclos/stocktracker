from stocktracker.purchase import Purchase
from stocktracker.stockAPI import StockAPI
from stocktracker.utils import get_current_date, get_oldest_date
from collections import OrderedDict


class Stock:
    def __init__(
        self,
        ticket: str,
        quantity: int,
        price: int = None,
        purchase_date: str = get_current_date(),
    ):
        # OBS: data compra no formato yyyy/mm/dd
        self.ticket = ticket
        self.quantity = quantity
        self.api = StockAPI()

        stock_history = self.api.get_history(self.ticket, purchase_date)

        if stock_history.empty:
            raise ValueError(f"No data for the purchase date: {purchase_date}")
        
        self.current_price = stock_history["Open"].iloc[-1] # Get latest opening price

        self.historical_high = stock_history["High"].max()
        self.historical_low = stock_history["Low"].min()
        # self.sector = self.api.get_sector(self.ticket)

        if not price:
            price = stock_history["Open"].iloc[-1]

        # Dicionario onde a chave é o a data da acao e o valor um objeto Compra
        self.purchases = {}
        purchase = Purchase(purchase_date, price, quantity)
        self.purchases[purchase_date] = purchase

        self.total_spent = purchase.price * purchase.quantity
        self.current_value = 0  # valor atual total do ativo sera averiguado somente quando quisermos obter valorização, nao tem pra que guardar ele ja agora
        self.gain = 0
        
        self.update_stock_status()

    def add_purchase(self, date: str, quantity_purchase: int, purchase_price: float):
        if date is None:
            date = get_current_date()

        stock_history = self.api.get_history(self.ticket, date)

        if stock_history.empty:
            raise ValueError(f"No data for the purchase date: {date}")

        purchase = Purchase(date, purchase_price, quantity_purchase)

        # adiciona objeto Compra para o dicionario e já atualiza valor_gasto
        self.purchases[date] = purchase
        self.purchases = OrderedDict(
            sorted(self.purchases.items())
        )  # para implementar a venda de acoes usando FIFO
        # precisamos deixar o dicionario ordenado
        self.quantity += quantity_purchase
        self.total_spent += purchase_price * quantity_purchase

        self.update_stock_status()

    def sell(self, quantity):
        removed = 0  # quantas acoes foram removidas
        spent_removed = 0

        datas = list(self.purchases.keys())

        for data in datas:
            purchase = self.purchases[data]

            if purchase.quantity <= (quantity - removed):
                # remove toda compra
                removed += purchase.quantity
                spent_removed += purchase.quantity * purchase.price
                del self.purchases[data]
                if (
                    removed == quantity
                ):  # para de remover acoes das proximas datas quando já remover o suficiente
                    break  # sai do loop
            else:
                # remove só parte da compra
                delta = quantity - removed
                purchase.quantity -= delta
                removed += delta
                spent_removed += delta * purchase.price

                break

        self.quantity -= removed
        self.total_spent -= spent_removed
        self.update_stock_status()

        return removed, spent_removed

    def update_stock_status(self):
        # se a purchases estiver vazia, n chama api, alteracao necessaroa para testes 
        if not self.purchases:
            self.current_value = 0
            self.historical_high = 0
            self.historical_low = 0
            self.gain = 0
            return    

        # atualiza o valor atual, maximo e minimo
        oldest_date = get_oldest_date(list(self.purchases.keys()))

        price, high, low = self.api.get_latest_price(self.ticket, oldest_date)
        self.current_value = price
        self.historical_high = high
        self.historical_low = low

        # modificar a valorizacao para depender apenas de valor gasto, ja que pode ter comprado a acao por precos diferentes
        total_current = self.current_value * self.quantity
        self.gain = (
            (total_current - self.total_spent) / self.total_spent
        ) * 100  # Em porcentagem
