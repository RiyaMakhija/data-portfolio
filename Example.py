import pandas as pd
from sqlalchemy import create_engine
import pyodbc

conn = pyodbc.connect(
    r"Driver={ODBC Driver 17 for SQL Server};"
    r"Server=LENOVO\SQLEXPRESS;"
    r"Database=mydatabase;"
    r"Trusted_Connection=yes;"
)


# Load the Excel file

dimension_df = pd.read_excel("C:\\Datasets\\sample-chocolate-sales-data-all.xlsx", sheet_name='Dimension Data', header=2)
# Print column names to verify the data
print(dimension_df.columns)
dimension_df.columns = dimension_df.columns.str.strip()

Shipments_df = pd.read_excel("C:\\Datasets\\sample-chocolate-sales-data-all.xlsx", sheet_name='Shipments')
# Print column names to verify the data
print(dimension_df.columns)

calendar_df = pd.read_excel("C:\\Datasets\\sample-chocolate-sales-data-all.xlsx", 
                            sheet_name='Calendar',  # Change this to your sheet name
                            header=1,  # Row 2 is the header row
                            usecols="B:G") 


product_df = dimension_df[['Product', 'Category', 'Cost_per_box', 'PID']].dropna(subset=['Product'])
location_df = dimension_df[['Geo', 'Region', 'GID']].dropna(subset=['Geo'])
people_df = dimension_df[['Sales_Person', 'Team', 'Picture', 'SPID']].dropna(subset=['Sales_Person'])


# Optional: clean dollar values in 'Cost_per_box'
product_df['Cost_per_box'] = product_df['Cost_per_box'].replace(r'[\$,]', '', regex=True).astype(float)

cursor = conn.cursor()

# Assuming the dataframes are already created: product_df, location_df, people_df
# Example: product_df = pd.read_excel("C:\\path\\to\\your\\file.xlsx")

# Insert data for 'Product' table
'''for index, row in product_df.iterrows():
    cursor.execute("""
        INSERT INTO Product (Product, Category, Cost_per_box,PID)
        VALUES (?, ?, ?, ?)
    """, 
        
        row['Product'],
        row['Category'],
        float(row['Cost_per_box']),
        row['PID'] # Ensure it's float for Cost_per_box
    )

# Insert data for 'Location' table
for index, row in location_df.iterrows():
    cursor.execute("""
        INSERT INTO Location (Geo, Region, GID)
        VALUES (?, ?, ?)
    """, 
        
        row['Geo'],
        row['Region'],
        row['GID']
    )

# Insert data for 'People' table
for index, row in people_df.iterrows():
    cursor.execute("""
        INSERT INTO People (Sales_Person, Team, Picture, SPID )
        VALUES (?, ?, ?, ?)
    """, 
        
        row['Sales_Person'],
        row['Team'],
        row['Picture'],
        row['SPID']
    )

# Insert data for 'Shipments' table

for index, row in Shipments_df.iterrows():
    cursor.execute("""
        INSERT INTO Shipments (ShipmentID, SPID, PID, GID, Shipdate, Amount, Boxes, Order_Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, 
        row['ShipmentID'],
        row['SPID'],
        row['PID'],
        row['GID'],
        row['Shipdate'],  # Ensure Shipdate is in proper date format
        float(row['Amount']),
        int(row['Boxes']),
        row['Order_Status']
    )


# Insert data for 'Calendar' table
for index, row in calendar_df.iterrows():
    cursor.execute("""
        INSERT INTO Calendar (cal_date, Month_num, month_name, year, weekday_num, weekday_name)
        VALUES (?, ?, ?, ?, ?, ?)
    """, 
        row['cal_date'],  # Ensure cal_date is in proper date format
        int(row['Month_num']),
        row['month_name'],
        int(row['year']),
        int(row['weekday_num']),
        row['weekday_name']
    )'''

Result = Shipments_df.groupby('Order_Status')['Amount'].sum()
print(Result)

# Commit the transaction to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()

print("data tables uploaded successfully.")
