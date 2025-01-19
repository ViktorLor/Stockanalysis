import pandas as pd
import yfinance as yf
import os

S_P500 = False
emerging = True
# Step 1: Get the S&P 500 tickers
if S_P500:
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500_table = pd.read_html(url)
    sp500_df = sp500_table[0]
    tickers = sp500_df['Symbol'].tolist()

# if emerging and the file is not already saved
if emerging and not os.path.exists("emerging_tickers.txt"):
# 1. Download EEM holdings from the iShares website
    url = "https://www.ishares.com/us/products/239637/ishares-msci-emerging-markets-etf/1467271812596.ajax?fileType=csv&fileName=EEM_holdings&dataType=fund"
    holdings = pd.read_csv(url, skiprows=9)  # Adjust skiprows if format changes

    # 2. Clean/rename columns if needed, then extract tickers
    holdings.columns = [col.strip() for col in holdings.columns]
    holdings.dropna(axis=0, how='all', inplace=True)


    # the exchange map is  in exchanges.txt and has the format: "Exchange;Abbreviation"
    exchange_map = {}
    with open("exchanges.txt") as f:
        for line in f:
            # some exchanges have an empty abbreviation, so we need to handle that
            exchange, abbreviation = line.strip().split(";")
            exchange_map[exchange] = abbreviation

    # 2. Convert full exchange name to abbreviation (or empty if not found)
    holdings["Exchange"] = holdings["Exchange"].map(exchange_map).fillna("")

    # 3. Build final tickers
    tickers = []

    for ticker, exchange in zip(holdings["Ticker"], holdings["Exchange"]):
        # Pad with leading zeros if it's numeric and under 4 digits
        if ticker.isdigit() and len(ticker) < 4:
            ticker = ticker.zfill(4)  # e.g., "233" -> "0233"

        # If exchange abbreviation is empty, use just the raw ticker
        if not exchange:
            tickers.append(ticker)
        else:
            # If abbreviation exists, append as TICKER.EXCHANGE
            tickers.append(f"{ticker}{exchange}")



# Step 2: Fetch stock data for all tickers
all_stock_data = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        historical_data = stock.history(period="1mo")  # Last 1 year of data
        historical_data['Ticker'] = ticker  # Add ticker symbol for identification
        all_stock_data.append(historical_data)
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")


# Step 3: Combine all data into a single DataFrame
combined_data = pd.concat(all_stock_data)

# Save to a CSV for further analysis
combined_data.to_csv("emerging_stock_data.csv")

print("Data fetched and saved to emerging_stock_data.csv")

# save file
