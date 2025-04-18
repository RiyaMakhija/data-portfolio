import pandas as pd
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load and clean data functions
def load_data(file_path):
    try:
        sales_df = pd.read_excel(file_path, sheet_name='Sales', header=None)
        product_df = pd.read_excel(file_path, sheet_name='Product Master', skiprows=1)
        region_df = pd.read_excel(file_path, sheet_name='Region Master')
        logging.info("Excel sheets loaded successfully.")
        return sales_df, product_df, region_df
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return None, None, None

def clean_sales_headers(sales_df):
    try:
        new_headers = sales_df.iloc[3, :11].tolist()
        remaining_headers = sales_df.iloc[0, 11:].tolist() if pd.api.types.is_list_like(sales_df.iloc[0, 11:]) else list(sales_df.columns[11:])
        final_headers = new_headers + remaining_headers
        sales_df = sales_df.iloc[4:].reset_index(drop=True)
        sales_df.columns = final_headers
        logging.info("Sales headers cleaned.")
        return sales_df
    except Exception as e:
        logging.error(f"Error cleaning headers: {e}")
        return sales_df

def drop_empty_rows(df):
    return df.dropna(how='all')

def split_product_column(df):
    try:
        split_columns = df['Product'].str.split('|', expand=True)
        df['Car Model'] = split_columns[0]
        df['Car Make'] = split_columns[1]
        logging.info("Product column split into Car Model and Car Make.")
        return df
    except Exception as e:
        logging.error(f"Error splitting product column: {e}")
        return df

def convert_date_and_amount(df):
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d/%m/%y', errors='coerce')
    df['Total Amount'] = pd.to_numeric(df['Total Amount'], errors='coerce')
    return df

def flag_inconsistent_rows(df, important_columns):
    def flag_row(row):
        for col in important_columns:
            if pd.isnull(row[col]) or row[col] == '' or row[col] == 0:
                return "Missing/inconsistent data"
        return "Ok"
    df['Data_issue_flag'] = df.apply(flag_row, axis=1)
    return df

def filter_valid_amount_rows(df):
    return df[(df['Total Amount'] != 0) & df['Total Amount'].notna()]

def clean_city_column(df):
    df['City'] = df['City'].str.strip().str.title()
    df['City'] = df['City'].apply(lambda x: re.sub(r'[^A-Za-z\s]', '', x) if isinstance(x, str) else x)
    return df

def merge_region_and_product(df, region_df, product_df):
    df = pd.merge(df, region_df[['Region Code', 'Region Name', 'Country']], on='Region Code', how='left')
    df = pd.merge(df, product_df[['Car Make', 'Car Model', 'Category']], on=['Car Make', 'Car Model'], how='left')
    return df

def calculate_country_sales(df):
    return df.groupby('Country')['Total Amount'].sum().reset_index()

def calculate_product_sales(df):
    return df.groupby('Car Make')['Total Amount'].sum().reset_index()

def get_invalid_dates(df):
    return df[df['Order Date'].isna()]

def handle_duplicates_by_date(df, date_column='Order Date', subset_columns=None):
    try:
        logging.info(f"Starting duplicate handling based on column '{date_column}'")
        df[date_column] = df[date_column].fillna(pd.Timestamp("1900-01-01"))
        # If no subset_columns are specified, use all columns except the date
        if subset_columns is None:
            subset_columns = [col for col in df.columns if col != date_column]
        
        # Sort the DataFrame by date in descending order (latest first)
        sorted_df = df.sort_values(by=date_column, ascending=False)

        # Drop duplicates, keeping the latest (first after sorting)
        duplicated_df = sorted_df.drop_duplicates(subset=subset_columns, keep='first')

        return duplicated_df

    except Exception as e:
        logging.error(f"Error in handling duplicates: {e}")
        return df  # Return original DataFrame if there's an error

def calculate_product_sales_contribution(df):
    try:
        logging.info("Calculating percentage contribution of each product to total sales.")

        product_sales = df.groupby('Product')['Total Amount'].sum().reset_index()

        
        total_sales = product_sales['Total Amount'].sum()

     
        product_sales['Percentage Contribution'] = (product_sales['Total Amount'] / total_sales) * 100

        return product_sales.sort_values(by='Percentage Contribution', ascending=False)

    except Exception as e:
        logging.error(f"Error calculating product sales contribution: {e}")
        return pd.DataFrame()

def get_top_car_make_by_region(df):
    try:
        logging.info("Identifying top-performing Car Make in each Region.")

        grouped = df.groupby(['Region Name', 'Car Make'])['Total Amount'].sum().reset_index()

        top_products = grouped.sort_values('Total Amount', ascending=False).groupby('Region Name').head(1)

        return top_products.sort_values(by='Total Amount', ascending=False)

    except Exception as e:
        logging.error(f"Error finding top Car Make by region: {e}")
        return pd.DataFrame()

def calculate_quarterly_sales_trends(df):
    try:
        logging.info("Calculating quarterly sales trends for each Car Make.")

              
        df = df[df['Order Date'].notna()]

        # Create a Quarter column
        df['Quarter'] = df['Order Date'].dt.to_period('Q')

        # Group by Quarter and Car Make, then sum sales
        quarterly_trends = df.groupby(['Quarter', 'Car Make'])['Total Amount'].sum().reset_index()

        return quarterly_trends.sort_values(['Quarter', 'Total Amount'], ascending=[True, False])

    except Exception as e:
        logging.error(f"Error calculating quarterly sales trends: {e}")
        return pd.DataFrame()


# Execution starts here
file_path = "C:\\Users\\ashok\\Downloads\\Python Test\\Sales_Data_.xlsx"
sales_df, product_df, region_df = load_data(file_path)

sales_df = clean_sales_headers(sales_df)
sales_df_cleaned = drop_empty_rows(sales_df)
product_df_cleaned = drop_empty_rows(product_df)
region_df_cleaned = drop_empty_rows(region_df)

sales_df_cleaned = split_product_column(sales_df_cleaned)
sales_df_cleaned = convert_date_and_amount(sales_df_cleaned)

important_columns = ['City', 'Region Code', 'No.of Cars', 'Price per car', 'Total Amount', 'Order Date', 'Month', 'Year', 'Product', 'Sales Person']
sales_df_cleaned = flag_inconsistent_rows(sales_df_cleaned, important_columns)
sales_df_cleaned = filter_valid_amount_rows(sales_df_cleaned)
sales_df_cleaned = clean_city_column(sales_df_cleaned)
sales_df_cleaned = merge_region_and_product(sales_df_cleaned, region_df_cleaned, product_df_cleaned)

#sales_df_cleaned= handle_duplicates_by_date(sales_df_cleaned,sales_df_cleaned['Order Date'],subset_columns=['City', 'Car Make', 'Car Model'])

# Display outputs
pd.options.display.float_format = '{:,.2f}'.format
print("\nCountry-wise Sales:")
print(calculate_country_sales(sales_df_cleaned))

print("\nProduct-wise Sales:")
print(calculate_product_sales(sales_df_cleaned))

print("\nRows with Invalid Dates:")
print(get_invalid_dates(sales_df_cleaned))

print("\nAfter Removing duplicates based on order date and keeping the latest:")
print(handle_duplicates_by_date(sales_df_cleaned,date_column='Order Date',subset_columns=['City', 'Car Make', 'Car Model']))

product_contribution_df = calculate_product_sales_contribution(sales_df_cleaned)
print("\n product Sales Contibution:",product_contribution_df)

top_car_make_per_region = get_top_car_make_by_region(sales_df_cleaned)
print(top_car_make_per_region)

quarterly_sales = calculate_quarterly_sales_trends(sales_df_cleaned)
print(quarterly_sales)





