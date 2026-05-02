import json
import os
import glob
from datetime import datetime
import logging
from context_store import store
from models import ContextPayload, ContextScope

logger = logging.getLogger(__name__)

def load_dataset(dataset_dir: str = "./dataset"):
    if not os.path.exists(dataset_dir):
        logger.warning(f"Dataset directory not found: {dataset_dir}")
        return

    # Load categories
    categories_dir = os.path.join(dataset_dir, "categories")
    if os.path.exists(categories_dir):
        for filepath in glob.glob(os.path.join(categories_dir, "*.json")):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Use filename without extension as context_id if it's missing or list
                    context_id = os.path.basename(filepath).replace(".json", "")
                    if isinstance(data, dict):
                        # Some categories might have the slug inside
                        context_id = data.get("slug", context_id)
                    
                    payload = ContextPayload(
                        scope=ContextScope.category,
                        context_id=context_id,
                        version=1,
                        payload=data,
                        delivered_at=datetime.utcnow()
                    )
                    store.store_context(payload)
            except Exception as e:
                logger.error(f"Error loading category {filepath}: {e}")

    # Load merchants
    merchants_file = os.path.join(dataset_dir, "merchants_seed.json")
    if os.path.exists(merchants_file):
        try:
            with open(merchants_file, "r", encoding="utf-8") as f:
                merchants = json.load(f)
                for merchant in merchants:
                    store.store_context(ContextPayload(
                        scope=ContextScope.merchant,
                        context_id=merchant.get("merchant_id", "unknown"),
                        version=1,
                        payload=merchant,
                        delivered_at=datetime.utcnow()
                    ))
        except Exception as e:
            logger.error(f"Error loading merchants: {e}")

    # Load customers
    customers_file = os.path.join(dataset_dir, "customers_seed.json")
    if os.path.exists(customers_file):
        try:
            with open(customers_file, "r", encoding="utf-8") as f:
                customers = json.load(f)
                for customer in customers:
                    store.store_context(ContextPayload(
                        scope=ContextScope.customer,
                        context_id=customer.get("customer_id", "unknown"),
                        version=1,
                        payload=customer,
                        delivered_at=datetime.utcnow()
                    ))
        except Exception as e:
            logger.error(f"Error loading customers: {e}")

    # Load triggers
    triggers_file = os.path.join(dataset_dir, "triggers_seed.json")
    if os.path.exists(triggers_file):
        try:
            with open(triggers_file, "r", encoding="utf-8") as f:
                triggers = json.load(f)
                for trigger in triggers:
                    store.store_context(ContextPayload(
                        scope=ContextScope.trigger,
                        context_id=trigger.get("trigger_id", "unknown"),
                        version=1,
                        payload=trigger,
                        delivered_at=datetime.utcnow()
                    ))
        except Exception as e:
            logger.error(f"Error loading triggers: {e}")

    logger.info("Dataset loaded successfully.")
    logger.info(f"Counts: {store.get_counts()}")

