"""
Diagnostic: inspect existing CosmosDB containers and records.

Usage:
    source env_vars.sh
    python HttpTriggerInference/inference_pipeline_src/tests/test_cosmos_inspect.py
"""
import os
import json
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

host = os.environ.get("COSMOS_HOST")
key = os.environ.get("COSMOS_KEY")
db_id = os.environ.get("COSMOS_DB_ID")

if not all([host, key, db_id]):
    print("ERROR: Missing CosmosDB env vars")
    exit(1)

print(f"Connecting to: {host}")
print(f"Database: {db_id}")
print()

client = cosmos_client.CosmosClient(host, key)

try:
    db = client.get_database_client(db_id)
    db.read()  # verify access
except Exception as e:
    print(f"Cannot access database '{db_id}': {e}")
    exit(1)

print("=== Containers in database ===")
containers = list(db.list_containers())
for c in containers:
    container_id = c["id"]
    partition_key = c.get("partitionKey", {}).get("paths", [])
    print(f"  {container_id} (partition key: {partition_key})")

print()

# For each container, count items and show a sample
for c in containers:
    container_id = c["id"]
    print(f"=== {container_id} ===")
    try:
        container = db.get_container_client(container_id)
        # Count
        count_query = "SELECT VALUE COUNT(1) FROM c"
        count = list(container.query_items(count_query, enable_cross_partition_query=True))[0]
        print(f"  Total items: {count}")

        if count > 0:
            # Get one sample
            sample_query = "SELECT TOP 1 * FROM c"
            samples = list(container.query_items(sample_query, enable_cross_partition_query=True))
            if samples:
                sample = samples[0]
                print(f"  Sample record keys: {list(sample.keys())}")
                # Show partition key value if present
                for k in ['partitionKey', 'PartitionKey']:
                    if k in sample:
                        print(f"  Sample '{k}' value: {sample[k]}")
                print(f"  Sample (truncated):")
                print(json.dumps(sample, indent=2, default=str)[:800])
    except Exception as e:
        print(f"  Error reading container: {e}")
    print()
