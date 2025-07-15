import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_oldest_date(date_list):
    """
    Receives a list of strings in 'yyyy/mm/dd' format and returns the oldest date.
    """
    converted_dates = [datetime.strptime(date, "%Y-%m-%d") for date in date_list]
    oldest_date = min(converted_dates)
    return oldest_date.strftime("%Y-%m-%d")


def get_yahoo_movers(mover_type):
    """
    Scrapes stock market movers (gainers, losers, most-active) from Yahoo Finance.

    Args:
        mover_type (str): The category of movers to fetch, 'gainers', 'losers', or 'most-active'.

    Returns:
        list[dict] or None: A list of dictionaries, each containing:
            - symbol: Stock ticker symbol
            - change: Price change (percentage or absolute)
            - is_positive: Boolean indicating if the change is positive
        Returns None if there's an error or the structure is unexpected.
    """
    
    # Build the URL dynamically based on the requested type (e.g., gainers, losers)
    url = f"https://finance.yahoo.com/markets/stocks/{mover_type}"
    try:
        # Send HTTP GET request to Yahoo Finance with a fake user agent (to avoid being blocked)
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0'},  # Emulate a browser
            timeout=5   # Timeout for the request (in seconds)
        )
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        movers = [] # This will hold the parsed stock data
        
        # Look for the stock data table and iterate over the first 5 rows (excluding header)
        for row in soup.find('table').find_all('tr')[1:6]:  # [1:6] skips the header row
            cols = row.find_all('td')
            
            # Only proceed if the row has enough columns to extract data safely
            if len(cols) >= 4:
                symbol = cols[0].text.strip()   # Ticket symbol
                change = cols[3].text.strip()   # % or absolute change
                
                # Add structured data for each mover
                movers.append({
                    'symbol': symbol,
                    'change': change,
                    'is_positive': '+' in change,   # Determine if it's a gain or loss
                })
        return movers
    except Exception as e:
        print(f"Error: {e}")
        return None