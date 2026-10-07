from tools.wiki_scrapper import (
    get_augment_mod_names, 
    get_bond_mod_names,
    get_mod_offers_current,
    get_mod_offers_statistics
    )
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def bond_mods_collect_pipeline():
    logging.info("="*15)
    logging.info("Collecting Bond Mods data")
    logging.info("="*15)
    bond_mod_names = get_bond_mod_names()
    bond_mod_offers_current = get_mod_offers_current(bond_mod_names)
    logging.info(f"Current Offers size: {bond_mod_offers_current.size}")
    bond_mod_offers_statistics = get_mod_offers_statistics(bond_mod_names)
    logging.info(f"Statistics Offers size: {bond_mod_offers_statistics.size}")
    bond_mod_offers_current.to_csv("../data/raw/bond_mod_offers_current.csv", index=False, sep=';')
    bond_mod_offers_statistics.to_csv("../data/raw/bond_mod_offers_statistics.csv", index=False, sep=';')
    return

def augment_mods_collect_pipeline():
    logging.info("="*15)
    logging.info("Collecting Augment Mods data")
    logging.info("="*15)
    augment_mod_names = get_augment_mod_names()
    augment_mod_offers_current = get_mod_offers_current(augment_mod_names)
    logging.info(f"Current Offers size: {augment_mod_offers_current.size}")
    augment_mod_offers_statistics = get_mod_offers_statistics(augment_mod_names)
    logging.info(f"Statistics Offers size: {augment_mod_offers_statistics.size}")
    augment_mod_offers_current.to_csv("../data/raw/augment_mod_offers_current.csv", index=False, sep=';')
    augment_mod_offers_statistics.to_csv("../data/raw/augment_mod_offers_statistics.csv", index=False, sep=';')
    return