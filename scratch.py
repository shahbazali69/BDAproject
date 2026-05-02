import pandas as pd
df = pd.read_csv('Ecommerce_Sales_Data.csv', usecols=['total_amount'])
print(f"Min: {df['total_amount'].min()}")
print(f"Max: {df['total_amount'].max()}")
print(f"Mean: {df['total_amount'].mean():.2f}")
