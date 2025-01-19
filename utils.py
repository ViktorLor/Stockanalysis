import datetime

import pandas as pd
import os
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np



def fetch_from_yfinance(tickers,data_file="stock_data.csv", period="1y"):
    # Define the tickers and filename
    sp500_tickers = ["meta", "amzn", "aapl", "ibm"]

    # Check if the data file already exists
    if os.path.exists(data_file):
        # Load data from CSV
        combined_data = pd.read_csv(data_file, index_col=0, parse_dates=True)
        print("Data loaded from existing CSV file.")
    else:
        # Fetch data if CSV does not exist
        all_stock_data = []
        for ticker in sp500_tickers:
            try:
                stock = yf.Ticker(ticker)
                # Fetch last 1 month of data
                historical_data = stock.history(period=period)
                historical_data['Ticker'] = ticker  # Add ticker symbol
                all_stock_data.append(historical_data)
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")

        # Combine and save the data to CSV for future runs
        combined_data = pd.concat(all_stock_data)
        combined_data.to_csv(data_file)
        print("Data fetched and saved to CSV file.")

    return combined_data

def get_sp500_tickers():
    # Get the S&P 500 tickers from Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500_table = pd.read_html(url)
    sp500_df = sp500_table[0]
    sp500_tickers = sp500_df['Symbol'].tolist()
    return sp500_tickers


def plot_stocks(normed_returns, tickers):
    # Plot all tickers
    plt.figure(figsize=(10, 5))
    for ticker in tickers:
        plt.plot(normed_returns.index, normed_returns[ticker], label=ticker)

    plt.title('Normalized Stock Prices')
    plt.xlabel('Date')
    plt.ylabel('Normalized Price')
    plt.legend()
    plt.show()


class StockClassifier:
    """
    The Stock_classifier should be able to classify stocks based on the criterias defined.

    ##Example Usage:

    classifier = StockClassifier()
    symbol_to_check = "AAPL"  # Example ticker
    category = classifier.classify_ticker(symbol_to_check)
    print(symbol_to_check, "classified as:", category)



    """
    def __init__(self):
        pass

    def _get_market_cap_in_billions(self, info: dict) -> float:
        """Return market cap in billions."""
        market_cap = info.get('marketCap', 0)
        return market_cap / 1e9  # Convert to billions

    def _get_revenue_growth_pct(self, info: dict) -> float:
        """
        Tries to get revenue growth from 'revenueGrowth' or 'quarterlyRevenueGrowth' in percentage.
        Adjust if you want to calculate from actual statements.
        """
        rev_growth = info.get('revenueGrowth') or info.get('quarterlyRevenueGrowth') or 0
        return rev_growth * 100  # e.g. 0.3 => 30%

    def _get_dividend_yield_pct(self, info: dict) -> float:
        """Return dividend yield in percent."""
        dividend_yield = info.get('dividendYield', 0)
        return dividend_yield * 100  # e.g. 0.03 => 3%

    def _is_negative_ebit_margin(self, info: dict) -> bool:
        """
        Placeholder for checking negative EBIT margin.
        yfinance does not directly provide EBIT margin;
        you might calculate from financial statements (quarterly/annual).
        """
        # Example placeholder:
        return info.get('ebitdaMargins', 0) < 0

    def classify_ticker(self, symbol: str) -> str:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        market_cap_b = self._get_market_cap_in_billions(info)
        rev_growth_pct = self._get_revenue_growth_pct(info)
        div_yield_pct = self._get_dividend_yield_pct(info)
        neg_ebit_margin = self._is_negative_ebit_margin(info)

        # Momentum trades high growth
        if rev_growth_pct >= 30 and market_cap_b < 50:
            return "Momentum trades high growth"

        # Momentum trades medium growth
        if 10 <= rev_growth_pct < 30 and 10 <= market_cap_b <= 100:
            return "Momentum trades medium growth"

        # Momentum trades
        if 5 <= rev_growth_pct < 10 and market_cap_b > 100:
            return "Momentum trades"

        # Dividend
        if market_cap_b > 200 and 2 <= div_yield_pct:
            return "Dividend"

        # Turnaround
        # Interpreted as rev growth between -10% and -1%
        if -10 <= rev_growth_pct < -1 and market_cap_b > 50:
            return "Turnaround"

        # Short Term trading clusters
        # Example: If rev growth is >= 30% but EBIT margin is negative
        if rev_growth_pct >= 30 and neg_ebit_margin:
            return "Short Term trading clusters"

        return "Unclassified"



def get_trailing_prices_and_yearly_return_avg(ticker: str, date_str: str):
    """
    Calculates:
      - Stock's average Close price over the trailing 1, 3, 6, and 12 months
        (relative to the given reference date).
      - 12-month average return =
         (avg Close of the last 12 months - avg Close of the previous 12 months)
         / (avg Close of the previous 12 months) * 100.
    Returns a dict with the results.

    Note: If any interval has no data (e.g., new IPO), the result is None for that interval.
    """

    try:

        def get_mean_close_in_range(df, start_dt, end_dt):
            """
            Returns the mean Close price between start_dt (inclusive) and end_dt (exclusive).
            If no data is found, returns None.
            """
            subset = df.loc[(df.index >= start_dt) & (df.index < end_dt), 'Close']
            return subset.mean() if not subset.empty else None

        # Convert the reference date string to a pandas Timestamp
        ref_date = pd.to_datetime(date_str)

        # Download two full years of data before the reference date (plus a bit after),
        # so we have enough data to calculate the trailing 12-month and the previous 12-month window.
        start_date = ref_date - datetime.timedelta(days=365 * 3)
        end_date = ref_date + datetime.timedelta(days=1)
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            return {"error": "No data downloaded."}

        # Ensure we only keep valid 'Close' data (dropping rows with NaN in Close)
        #data = data.dropna(subset=["Close"])

        # 1-month average
        price_1m_avg = get_mean_close_in_range(
            data,
            ref_date - pd.DateOffset(months=1),
            ref_date
        )
        # 3-month average
        price_3m_avg = get_mean_close_in_range(
            data,
            ref_date - pd.DateOffset(months=3),
            ref_date
        )
        # 6-month average
        price_6m_avg = get_mean_close_in_range(
            data,
            ref_date - pd.DateOffset(months=6),
            ref_date
        )
        # 12-month average
        price_12m_avg = get_mean_close_in_range(
            data,
            ref_date - pd.DateOffset(months=12),
            ref_date
        )

        # Previous 12-month average:
        # This is used to calculate the "12-month average return":
        #   last_12m_avg vs. the 12 months prior to that (i.e., 24m -> 12m back)
        price_prev_12m_avg = get_mean_close_in_range(
            data,
            ref_date - pd.DateOffset(months=24),
            ref_date - pd.DateOffset(months=12)
        )

        if price_12m_avg is not None and price_prev_12m_avg is not None:
            yearly_return_pct = (price_12m_avg - price_prev_12m_avg) / price_prev_12m_avg * 100
        else:
            yearly_return_pct = None

        return {
            "ref_date": date_str,
            "1m_trailing_avg_close": price_1m_avg,
            "3m_trailing_avg_close": price_3m_avg,
            "6m_trailing_avg_close": price_6m_avg,
            "12m_trailing_avg_close": price_12m_avg,
            "12m_average_return_%": yearly_return_pct
        }
    except:
        return {
            "ref_date": np.nan,
            "1m_trailing_avg_close": np.nan,
            "3m_trailing_avg_close": np.nan,
            "6m_trailing_avg_close": np.nan,
            "12m_trailing_avg_close": np.nan,
            "12m_average_return_%": np.nan
        }

