"""
CosmosDB writer for inference results and errors.

Writes to two containers in the smartalert database:
- ModelInference: successful inference results (patient, features, scores)
- Model_APIErrors: failed inference attempts (patient, error details)

Both containers use partition key path /PartitionKey. The CosmosDB client is
initialized lazily from environment variables (COSMOS_HOST, COSMOS_KEY,
COSMOS_DB_ID) so importing this module doesn't require credentials.
"""
import datetime
import logging
import os
import traceback
import uuid
from typing import Any, Dict, Optional

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as cosmos_exceptions
from azure.cosmos.partition_key import PartitionKey

logger = logging.getLogger(__name__)

# Container names and their partition key values
INFERENCE_CONTAINER = "Model_Inference"
ERROR_CONTAINER = "Model_APIErrors"
PARTITION_KEY_PATH = "/PartitionKey"

# Module-level cache for CosmosDB clients
_client = None
_db = None
_containers: Dict[str, Any] = {}


def _get_container(container_id: str):
    """Get (or create) a CosmosDB container client. Cached by container_id."""
    global _client, _db

    if container_id in _containers:
        return _containers[container_id]

    if _client is None:
        host = os.environ.get("COSMOS_HOST")
        key = os.environ.get("COSMOS_KEY")
        db_id = os.environ.get("COSMOS_DB_ID")
        if not all([host, key, db_id]):
            raise RuntimeError(
                "Missing COSMOS_HOST / COSMOS_KEY / COSMOS_DB_ID environment variables"
            )
        _client = cosmos_client.CosmosClient(host, key)
        try:
            _db = _client.create_database(id=db_id)
        except cosmos_exceptions.CosmosResourceExistsError:
            _db = _client.get_database_client(db_id)

    try:
        container = _db.create_container(
            id=container_id,
            partition_key=PartitionKey(path=PARTITION_KEY_PATH),
        )
        logger.info(f"Created CosmosDB container '{container_id}'")
    except cosmos_exceptions.CosmosResourceExistsError:
        container = _db.get_container_client(container_id)

    _containers[container_id] = container
    return container


def _record_id() -> str:
    """Generate a unique record ID (timestamp + UUID)."""
    ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    return f"{ts}_{uuid.uuid4().hex}"


def write_inference_result(
    patient_data: Dict[str, Any],
    scores: Dict[str, Optional[float]],
    features: Dict[str, Any],
    culture_type: str,
    setting: str,
) -> str:
    """Write a successful inference result to the Model_Inference container.

    Returns the record ID that was written.
    """
    now = datetime.datetime.now()
    record = {
        "id": _record_id(),
        "PartitionKey": INFERENCE_CONTAINER,
        "order_date": now.strftime("%Y-%m-%d %H:%M:%S"),
        "inference_date": now.isoformat(),
        "patient": patient_data,
        "culture_type": culture_type,
        "setting": setting,
        "features": features,
        "scores": scores,
    }
    container = _get_container(INFERENCE_CONTAINER)
    container.create_item(body=record)
    logger.info(f"Wrote inference record to {INFERENCE_CONTAINER}: id={record['id']}")
    return record["id"]


def write_inference_error(
    patient_id: str,
    culture_type: str,
    setting: str,
    error: Exception,
) -> str:
    """Write a failed inference attempt to the Model_APIErrors container.

    Returns the record ID that was written.
    """
    now = datetime.datetime.now()
    record = {
        "id": _record_id(),
        "PartitionKey": ERROR_CONTAINER,
        "order_date": now.strftime("%Y-%m-%d %H:%M:%S"),
        "patient_id": patient_id,
        "culture_type": culture_type,
        "setting": setting,
        "error": str(error),
        "traceback": traceback.format_exc(),
    }
    container = _get_container(ERROR_CONTAINER)
    container.create_item(body=record)
    logger.info(f"Wrote error record to {ERROR_CONTAINER}: id={record['id']}")
    return record["id"]
