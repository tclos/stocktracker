import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import csv
from stocktracker.wallet import Wallet
from stocktracker.stock import Stock
from stocktracker.purchase import Purchase

class performancereport:
    """
    Classe para gerar e gerenciar relatórios de performance em CSV
    com persistência na pasta src/data/
    """

    @staticmethod
    def generate_all_reports(wallet: Wallet, purchase_filename: str = "purchase_history.csv", metrics_filename: str = "metrics_report.txt", asset_filename: str = "assets_listing.csv"):
    #gera 3 relatorios: historico de compras e vendas, listagem de todos os ativos, e report em um txt com metricas da carteira

        performancereport.generate_metrics_report(wallet, metrics_filename)
        performancereport.generate_purchase_history(wallet, purchase_filename)
        performancereport.generate_assets_listing(wallet, asset_filename)
        


    @staticmethod
    def generate_metrics_report(wallet: Wallet, metrics_filename):
    #gera um txt com portfolio gain, avg gain, gain per asset, avg gain per sector, total_spent, total_value
        wallet.update_wallet_status()
        filepath = os.path.join(performancereport.get_data_path(), metrics_filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f"Wallet Name: {wallet.name}\n")
            file.write("="*50 + "\n")
            file.write("Wallet Metrics:\n")
            file.write(f"  Portfolio gain (%): {wallet.total_gain:.2f}\n")
            file.write(f"  Current value: {wallet.total_value:.2f}\n")
            file.write(f"  Total spent: {wallet.total_spent:.2f}\n")
            file.write(f"  Number of tickets: {wallet.tickets_count}\n")
            file.write(f"  Number of shares: {wallet.total_quantity}\n")
            
            file.write("Stock Details:\n")
            for ticket, stock in wallet.stocks.items():
                file.write(f"Ticket: {ticket}\n")
                file.write(f"  Total quantity: {stock.quantity}\n")
                file.write(f"  Total spent: {stock.total_spent:.2f}\n")
                file.write(f"  Current value: {stock.current_value:.2f}\n")
                file.write(f"  Current total value: {stock.current_value * stock.quantity:.2f}\n")
                file.write(f"  Gain (%): {stock.gain:.2f}%\n")
                file.write(f"  Purchases:\n")
                for data_compra, compra in stock.purchases.items():
                    file.write(
                        f"    Data: {data_compra}, Quantity: {compra.quantity}, Purchase price: {compra.price:.2f}\n"
                    )


        


    @staticmethod
    def generate_purchase_history(wallet: Wallet, purchase_filename):
        wallet.update_wallet_status()
        filepath = os.path.join(performancereport.get_data_path(), purchase_filename)

        fieldnames = [
            "wallet_name", "ticket", "quantity", "price_paid_per_asset", "total_spent", # "sector",
            "current_price", "current_value", "gain_pct", "purchase_date"
        ]

        records = []

        for ticket, stock in wallet.stocks.items():
            for date, purchase in stock.purchases.items():              #acessa um stock, com loop interno acessa dados de cada
                records.append({                                        #purchase individualmente
                    "wallet_name": wallet.name,
                    "ticket": ticket,
                    #"sector": stock.sector,
                    "quantity": purchase.quantity,
                    "price_paid_per_asset": purchase.price,
                    "total_spent": purchase.price * purchase.quantity,
                    "current_price": "n/a",
                    "current_value": "n/a",
                    "gain_pct": "n/a",
                    "purchase_date": date,
                })

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"Purchase history saved at: {filepath}")



    @staticmethod
    def generate_assets_listing(wallet: Wallet, assets_filename):
        wallet.update_wallet_status()
        filepath = os.path.join(performancereport.get_data_path(), assets_filename)
        records = []

        fieldnames = [
            "wallet_name", "ticket", "quantity", "average_price",     # "sector",
            "total_spent", "current_price", "current_value", "gain_pct"
        ]

        for ticket, stock in wallet.stocks.items():

            records.append({                                            #escreve dados do stock
                "wallet_name": wallet.name,
                "ticket": ticket,
                #"sector": stock.sector,
                "quantity": stock.quantity,
                "average_price": stock.total_spent / stock.quantity if stock.quantity > 0 else 0,
                "total_spent": stock.total_spent,
                "current_price": stock.current_value,
                "current_value": stock.current_value * stock.quantity,
                "gain_pct": stock.gain,
            })

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"Assets listing saved at: {filepath}")

        
    @staticmethod
    def get_data_path():
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        data_path = os.path.join(current_dir, "data") 
        os.makedirs(data_path, exist_ok=True) # cria a pasta "data" em src/stocktracker/data se nao existir
        return data_path                      # retorna o caminho onde o csv sera criado

    @staticmethod
    def generate_csv_report(wallet: Wallet, filename: str = "portfolio.csv"):   #cria portfolio.csv na pasta data
        wallet.update_wallet_status()
        filepath = os.path.join(performancereport.get_data_path(), filename)

        fieldnames = [
            "wallet_name", "type", "ticket", "quantity", "price",         # "sector",
            "total_spent", "current_price", "current_value", "gain_pct", "purchase_date"
        ]

        records = []

        for ticket, stock in wallet.stocks.items():
            for date, purchase in stock.purchases.items():              #acessa um stock, com loop interno acessa dados de cada
                records.append({                                        #purchase individualmente
                    "wallet_name": wallet.name,
                    "type": "PURCHASE",
                    "ticket": ticket,
                    # "sector": stock.sector,
                    "quantity": purchase.quantity,
                    "price": purchase.price,
                    "total_spent": purchase.price * purchase.quantity,
                    "current_price": "n/a",
                    "current_value": "n/a",
                    "gain_pct": "n/a",
                    "purchase_date": date,
                })

            records.append({                                            #escreve dados do stock
                "wallet_name": wallet.name,
                "type": "STOCK",
                "ticket": ticket,
                # "sector": stock.sector,
                "quantity": stock.quantity,
                "price": stock.total_spent / stock.quantity if stock.quantity > 0 else 0,
                "total_spent": stock.total_spent,
                "current_price": stock.current_value,
                "current_value": stock.current_value * stock.quantity,
                "gain_pct": stock.gain,
                "purchase_date": "",
            })

        records.append({      #escreve por fim dados da carteira
            "wallet_name": wallet.name,
            "type": "PORTFOLIO",
            "ticket": "ALL",
            # "sector": "ALL",
            "quantity": wallet.tickets_count,
            "price": "",
            "total_spent": wallet.total_spent,
            "current_price": "",
            "current_value": wallet.total_value,
            "gain_pct": wallet.total_gain,
            "purchase_date": "",
        })

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"Relatório salvo em: {filepath}")

    @staticmethod
    def restore_from_csv(filename: str = "portfolio.csv") -> Wallet:
        filepath = os.path.join(performancereport.get_data_path(), filename) #acessa src/stocktracker/data
        if not os.path.exists(filepath):                                     #verifica se existe "portfolio.csv" nele
            print("Arquivo de carteira não encontrado.")
            return None

        wallet = Wallet("")

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get wallet name from first row
                if 'wallet_name' in row and row['wallet_name']:
                    wallet.name = row['wallet_name']
                if row["type"] == "PURCHASE":
                    ticket = row["ticket"]
                    date = row["purchase_date"]
                    quantity = int(row["quantity"])
                    price = float(row["price"])

                    if ticket in wallet.stocks:
                        stock = wallet.stocks[ticket]
                        stock.purchases[date] = Purchase(date, price, quantity)
                        stock.quantity += quantity
                        stock.total_spent += price * quantity
                    else:
                        stock = Stock(ticket, 0, date)
                        stock.purchases = {}
                        stock.purchases[date] = Purchase(date, price, quantity)
                        stock.quantity = quantity
                        stock.total_spent = price * quantity
                        wallet.stocks[ticket] = stock

        wallet.update_wallet_status()
        return wallet
