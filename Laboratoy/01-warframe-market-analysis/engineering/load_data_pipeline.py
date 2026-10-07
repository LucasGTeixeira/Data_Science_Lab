from tools.collect_data import (
    bond_mods_collect_pipeline,
    augment_mods_collect_pipeline
)
from tools.transformations import (
    order_current_processing,
    order_statistics_processing
)
import logging

def collect_pipeline():
    bond_mods_collect_pipeline()
    augment_mods_collect_pipeline()

def transform_pipeline():
    order_current_processing()
    order_statistics_processing()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    collect_pipeline()
    transform_pipeline()