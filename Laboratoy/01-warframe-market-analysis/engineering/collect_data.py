import sys
sys.path.insert(0, '..')
from tools.wiki_scrapper import (
    get_augment_mod_names, 
    get_bond_mod_names,
    get_mod_offers_current,
    get_mod_offers_statistics
    )
import logging

def bond_mods_collect_pipeline():
    logging.info("Collecting Bond Mods data")
    bond_mod_names = get_bond_mod_names()
    bond_mod_offers_current = get_mod_offers_current(bond_mod_names)
    logging.info(f"Current Offers size: {bond_mod_offers_current.size}")
    bond_mod_offers_statistics = get_mod_offers_statistics(bond_mod_names)
    logging.info(f"Statistics Offers size: {bond_mod_offers_statistics.size}")
    bond_mod_offers_current.to_csv("../data/bond_mod_offers_current.csv", index=False, sep=';')
    bond_mod_offers_statistics.to_csv("../data/bond_mod_offers_statistics.csv", index=False, sep=';')
    return

def augment_mods_collect_pipeline():
    logging.info("Collecting Augment Mods data")
    augment_mod_names = get_augment_mod_names()
    augment_mod_offers_current = get_mod_offers_current(augment_mod_names)
    logging.info(f"Current Offers size: {augment_mod_offers_current.size}")
    augment_mod_offers_statistics = get_mod_offers_statistics(augment_mod_names)
    logging.info(f"Statistics Offers size: {augment_mod_offers_statistics.size}")
    augment_mod_offers_current.to_csv("../data/augment_mod_offers_current.csv", index=False, sep=';')
    augment_mod_offers_statistics.to_csv("../data/augment_mod_offers_statistics.csv", index=False, sep=';')
    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Starting Data Collection")
    bond_mods_collect_pipeline()
    augment_mods_collect_pipeline()