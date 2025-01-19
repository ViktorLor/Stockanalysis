import utils as ut
import matplotlib.pyplot as plt

# Define the tickers and filename
tickers = ["meta", "amzn", "aapl", "ibm"]

# tickers = ut.get_sp500_tickers()[0:50]

# fetch the data
combined_data = ut.fetch_from_yfinance(tickers, period="1mo")

# add a new column for normalized returns to combined_data
combined_data['Normed Return'] = None

# Use transform to create the normalized return columns
combined_data['Normed Return (Open)'] = combined_data.groupby('Ticker')['Open'].transform(lambda x: x / x.iloc[0])
combined_data['Normed Return (High)'] = combined_data.groupby('Ticker')['High'].transform(lambda x: x / x.iloc[0])

# Pivot so that each ticker is a column
normed_returns = combined_data.pivot_table(
    values='Normed Return (Open)',
    index=combined_data.index,
    columns='Ticker'
)

# loop through normed returns for each ticker and calculate the daily return to plot it as a histogram
for ticker in tickers:
    normed_returns[ticker].plot(label=ticker, figsize=(12, 8))
plt.legend()
plt.show()

# Plot the normalized returns
ut.plot_stocks(normed_returns, tickers)