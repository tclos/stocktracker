import unittest
from datetime import datetime
from stocktracker.purchase import Purchase

class TestPurchase(unittest.TestCase):
    def setUp(self):
        self.date = "2023-01-01"
        self.price = 150.50
        self.quantity = 10
        self.purchase = Purchase(self.date, self.price, self.quantity)
    
    def test_initialization(self):
        self.assertEqual(self.purchase.date, self.date)
        self.assertEqual(self.purchase.price, self.price)
        self.assertEqual(self.purchase.quantity, self.quantity)
      
    def test_invalid_date_format(self):
        with self.assertRaises(ValueError):  # Agora espera um erro
            Purchase("01-01-2023", self.price, self.quantity)  # Formato inválido (deve falhar)