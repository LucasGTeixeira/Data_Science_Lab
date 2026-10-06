#%%
import pandas as pd
import logging

def show_dataframe_report(df: pd.DataFrame):
    logging.info(f"dataframe size {df.shape}")
    logging.info(f"dataframe columns {df.columns}")
    logging.info(f"dataframe null counts {df.isna().sum()}")
    logging.info(f"dataframe null counts {df.describe()}")

def get_distinct_values(df: pd.DataFrame, column_name):
    logging.info(f"distinct values from: {df[column_name].value_counts()}")
    
def transform_orders_current(df: pd.DataFrame, output_name: str):
    logging.info(f"transforming {output_name}")
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
    
def transform_orders_statistics(df: pd.DataFrame, output_name: str):
    logging.info('============================================')
    logging.info('============================================')
    logging.info(f"transforming {output_name}")
    show_dataframe_report(df)
    for col_name in ['period', 'mod_rank', 'order_type', 'mode']:
        get_distinct_values(df, col_name)
    df = df[
        [
            'datetime',      # Data/hora da estatística
            'volume',        # Quantidade de unidades negociadas/ofertadas no período
            'min_price',     # Menor preço observado no período
            'max_price',     # Maior preço observado no período
            'open_price',    # Preço da primeira negociação/observação do período
            'closed_price',  # Preço da última negociação/observação do período
            'avg_price',     # Preço médio observado no período
            'wa_price',      # Preço médio ponderado pelo volume (VWAP)
            'median',        # Mediana dos preços observados no período
            'donch_top',     # Limite superior do Canal de Donchian
            'donch_bot',     # Limite inferior do Canal de Donchian
            'mod_rank',      # Rank/nível do mod
            'moving_avg',    # Média móvel do preço
            'period',        # Janela temporal utilizada para gerar a estatística
            'mode',          # Tipo de estatística: closed = negociações encerradas; live = ordens abertas
            'mod_name',      # Identificador/nome do mod
            'order_type'     # Tipo de ordem: buy = compra; sell = venda; null = quando closed
        ]
    ]
    df = df.to_csv(f'../data/{output_name}.csv', sep=';', index=False)

def order_current_processing():
    df_bond_orders_current = pd.read_csv('../data/bond_mod_offers_current.csv', sep=';')
    df_augment_orders_current = pd.read_csv('../data/augment_mod_offers_current.csv', sep=';')

    for df_name, df in {
        'augment_mod_offers_current':df_augment_orders_current, 
        'bond_mod_offers_current':df_bond_orders_current
    }.items():
        transform_orders_current(df, df_name )
        
def order_statistics_processing():
    df_bond_orders_statistics = pd.read_csv('../data/bond_mod_offers_statistics.csv', sep=';')
    df_augment_orders_statistics = pd.read_csv('../data/augment_mod_offers_statistics.csv', sep=';')
    
    for df_name, df in{
        'augment_mod_offers_statistics':df_augment_orders_statistics,
        'bond_mod_offers_statistics': df_bond_orders_statistics
    }.items(): 
        transform_orders_statistics(df, df_name)

#%%
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    order_current_processing()
    order_statistics_processing()
