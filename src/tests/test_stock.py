import unittest
from unittest.mock import MagicMock, patch
from stocktracker.stock import Stock
from stocktracker.purchase import Purchase

class TestStock(unittest.TestCase):
    @patch('stocktracker.stockAPI.StockAPI')
    def setUp(self, mock_api):
        # Configurar o mock da API
        self.mock_api = mock_api.return_value
        self.mock_api.get_history.return_value = MagicMock(
            empty=False,
            iloc=[MagicMock(**{'Open': 100})],
            **{
                'High.max.return_value': 120,
                'Low.min.return_value': 90,
                'Close.iloc[-1]': 105
            }
        )
        
        self.ticket = "AAPL"
        self.quantity = 5
        self.price = 100
        self.date = "2023-01-01"
        self.stock = Stock(self.ticket, self.quantity, self.price, self.date)
    
    def test_initialization(self):
        self.assertEqual(self.stock.ticket, self.ticket)
        self.assertEqual(self.stock.quantity, self.quantity)
        self.assertEqual(len(self.stock.purchases), 1)
        self.assertIn(self.date, self.stock.purchases)
    
    def test_add_purchase(self):
        new_date = "2023-02-01"
        new_quantity = 3
        new_price = 110
        self.stock.add_purchase(new_date, new_quantity, new_price)
        
        self.assertEqual(self.stock.quantity, self.quantity + new_quantity)
        self.assertEqual(len(self.stock.purchases), 2)
        self.assertIn(new_date, self.stock.purchases)
    
    def test_sell_fifo_order(self):
        """
        Testa se a venda de ações segue a política FIFO (First-In, First-Out).
        """

        # Situação inicial: uma compra existente
        self.stock.purchases = {}  # Zera as compras para controle total
        self.stock.quantity = 0
        self.stock.total_spent = 0

        # Faz 3 compras em datas diferentes, com preços diferentes
        self.stock.add_purchase("2023-01-01", 2, 100)  # 2 ações a 100
        self.stock.add_purchase("2023-02-01", 3, 110)  # 3 ações a 110
        self.stock.add_purchase("2023-03-01", 5, 120)  # 5 ações a 120

        # Agora temos 10 ações no total

        # Vamos vender 4 ações => Deve consumir todas da primeira compra (2x100) + 2 da segunda (2x110)
        removed, spent = self.stock.sell(4)

        self.assertEqual(removed, 4)
        expected_spent = (2 * 100) + (2 * 110)  # FIFO: primeiro as de 100, depois as de 110
        self.assertEqual(spent, expected_spent)

        # Confirma o estado final da stock:
        self.assertEqual(self.stock.quantity, 6)  # 10 - 4 = 6 ações restantes

        # Confirma que a compra de 2023-01-01 foi completamente removida
        self.assertNotIn("2023-01-01", self.stock.purchases)

        # Confirma que a compra de 2023-02-01 agora tem só 1 ação sobrando
        self.assertEqual(self.stock.purchases["2023-02-01"].quantity, 1)

        # A de 2023-03-01 permanece intacta com 5 ações
        self.assertEqual(self.stock.purchases["2023-03-01"].quantity, 5)

       
    @patch('stocktracker.stockAPI.StockAPI.get_history')
    def test_empty_history(self, mock_get_history):
        mock_get_history.return_value = MagicMock(empty=True)
        with self.assertRaises(ValueError):
            Stock(self.ticket, self.quantity, self.price, self.date)