#%%
import pandas as pd
import logging

def show_dataframe_report(df: pd.DataFrame):
    logging.info(f"dataframe size {df.size}")
    logging.info(f"dataframe columns {df.columns}")
    logging.info(f"dataframe null counts {df.isna().sum()}")
    logging.info(f"dataframe null counts {df.describe()}")

def get_distinct_values(df: pd.DataFrame, column_name):
    logging.info(f"distinct values from: {df[column_name].value_counts()}")
    
def transform_orders_current(df: pd.DataFrame, output_name: str):
    show_dataframe_report(df)
    for col_name in ['type', 'rank']:
        get_distinct_values(df, col_name)
    
    df = df[
        [
            'mod_name',
            'user', 
            'type',
            'platinum',
            'rank',
            'perTrade',
            'createdAt',
            'updatedAt'
        ]
    ]
    
    df.to_csv(f'../data/{output_name}.csv', sep=';', index=False)
    
def order_current_processing():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    df_bond_orders_current = pd.read_csv('../data/bond_mod_offers_current.csv', sep=';')
    df_augment_orders_current = pd.read_csv('../data/augment_mod_offers_current.csv', sep=';')

    for df_name, df in {
        'augment_mod_offers_current':df_augment_orders_current, 
        'bond_mod_offers_current':df_bond_orders_current
        }.items():
        transform_orders_current(df, df_name )
        
def order_statistics_processing():
    ...

#%%
if __name__ == '__main__':
    order_current_processing()
    order_statistics_processing()
