from datetime import datetime

class Purchase:
    """
    Classe para armazenar os dados de cada compra do usuario,
    contendo numero de ativos, data de compra e preco de compra
    """

    def __init__(self, date: str, price: float, quantity: int):
        # Validação de formato de data: deve ser yyyy-mm-dd
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Expected format: YYYY-MM-DD.")

        self.date = date
        self.price = price
        self.quantity = quantity
