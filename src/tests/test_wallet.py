import unittest
from unittest.mock import MagicMock, patch
from stocktracker.wallet import Wallet
from stocktracker.stock import Stock

class TestWallet(unittest.TestCase):
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
        self.mock_api.get_latest_price.return_value = (105, 120, 90)
        
        self.wallet_name = "Test Wallet"
        self.wallet = Wallet(self.wallet_name)
        
        # Adicionar um stock para testes
        self.ticket = "AAPL"
        self.quantity = 10
        self.price = 100
        self.date = "2023-01-01"
        self.wallet.add_stock(self.ticket, self.quantity, self.price, self.date)


    def test_initialization(self):
        self.assertEqual(self.wallet.name, self.wallet_name)
        self.assertEqual(len(self.wallet.stocks), 1)
    
    def test_add_stock(self):
        # Adicionar nova ação
        new_ticket = "GOOG"
        new_quantity = 5
        new_price = 200
        new_date = "2023-02-01"
        self.wallet.add_stock(new_ticket, new_quantity, new_price, new_date)
        
        self.assertEqual(len(self.wallet.stocks), 2)
        self.assertIn(new_ticket, self.wallet.stocks)
        
        # Adicionar à ação existente
        additional_quantity = 3
        self.wallet.add_stock(self.ticket, additional_quantity, self.price, new_date)
        self.assertEqual(len(self.wallet.stocks), 2)  # Ainda 2 tickets
        self.assertEqual(self.wallet.stocks[self.ticket].quantity, self.quantity + additional_quantity)
    
    def test_remove_stock(self):
        # Remoção parcial
        remove_qty = 5
        self.wallet.remove_stock(self.ticket, remove_qty)
        self.assertEqual(self.wallet.stocks[self.ticket].quantity, self.quantity - remove_qty)
        
        # Remoção total
        self.wallet.remove_stock(self.ticket)
        self.assertNotIn(self.ticket, self.wallet.stocks)
    
    def test_remove_more_than_available(self):
        with self.assertRaises(ValueError):
            self.wallet.remove_stock(self.ticket, self.quantity + 1)
     
    def test_clear_wallet(self):
        self.wallet.clear()
        self.assertEqual(len(self.wallet.stocks), 0)
        self.assertEqual(self.wallet.total_value, 0)
        self.assertEqual(self.wallet.total_spent, 0)
    
    def test_to_dataframe(self):
        df = self.wallet.to_dataframe()
        self.assertEqual(len(df), 1)  # Uma linha por ação
        self.assertEqual(df.iloc[0]['Ticket'], self.ticket)
        self.assertEqual(df.iloc[0]['Quantidade'], self.quantity)