"""
Author: Viktor Loreth
Date: 01/01/2024

This program recommends stocks based on defined characteristics
"""

import utils as ut
import pandas as pd


ut.get_sp500_tickers()

classifier = ut.StockClassifier()
sp500_tickers = ut.get_sp500_tickers()

results = []
for sym in sp500_tickers:
    category = classifier.classify_ticker(sym)
    performance = ut.get_trailing_prices_and_yearly_return_avg(sym, "2024-12-31")
    results.append((sym, category))
    # also append the trailing prices and yearly return
    for x in performance.values():
        results.append(x)

# Convert results to DataFrame
df_results = pd.DataFrame(results)
print(df_results)


print(results)

# You can also save to CSV if desired:
df_results.to_csv("sp500_classifications.csv", index=False)