import pandas as pd
import numpy as np
import pyodbc

#  Load data from Excel
df = pd.read_excel("C:\\Datasets\\global_sales_data.xlsx")

df.fillna({
    'Product': 'Unknown',
    'Category': 'Misc',
    'Region': 'Unknown',
    'Customer': 'Guest',
    'Quantity': 0,
    'Sales': 0.0,
    'Profit': 0.0
}, inplace=True)

df['Category'] = df['Category'].str.upper()

# Add a new column with a basic NumPy transformation (e.g., Profit Margin %)
df['Profit_Margin'] = np.where(df['Sales'] != 0, (df['Profit'] / df['Sales']) * 100, 0)

print("\n✅ Transformed Data Preview:")
print(df.head())

conn = pyodbc.connect(
    r"Driver={ODBC Driver 17 for SQL Server};"
    r"Server=LENOVO\SQLEXPRESS;"
    r"Database=mydatabase;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO global_sales (OrderID, OrderDate, Product, Category, Region, Customer, Quantity, Sales, Profit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
        int(row['OrderID']),
        row['OrderDate'],
        row['Product'],
        row['Category'],
        row['Region'],
        row['Customer'],
        int(row['Quantity']),
        float(row['Sales']),
        float(row['Profit'])
    )




conn.commit()
cursor.close()
conn.close()

print("✅ Data successfully transformed and loaded into SQL Server!")
