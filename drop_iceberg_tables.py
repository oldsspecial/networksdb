#!/usr/bin/env python3
"""Drop existing Iceberg tables to allow recreation with correct schema."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get catalog configuration from environment
catalog_config = {
    "type": "hive",
    "uri": os.getenv("HIVE_METASTORE_URI"),
    "s3.endpoint": os.getenv("MINIO_ENDPOINT"),
    "s3.access-key-id": os.getenv("MINIO_ACCESS_KEY"),
    "s3.secret-access-key": os.getenv("MINIO_SECRET_KEY"),
    "s3.path-style-access": "true",
}

print("Dropping Iceberg tables...")
print(f"Catalog config: {catalog_config}")

try:
    from pyiceberg.catalog import load_catalog
    
    catalog = load_catalog(name="drop_tables", **catalog_config)
    
    # Drop nodes table
    try:
        catalog.drop_table("network.nodes")
        print("✓ Dropped table: network.nodes")
    except Exception as e:
        print(f"✗ Could not drop network.nodes: {e}")
    
    # Drop relationships table
    try:
        catalog.drop_table("network.relationships")
        print("✓ Dropped table: network.relationships")
    except Exception as e:
        print(f"✗ Could not drop network.relationships: {e}")
    
    print("\nTables dropped successfully!")
    print("Run the pipeline again to recreate with correct schema.")
    
except ImportError:
    print("ERROR: pyiceberg not installed. Install with: pip install pyiceberg")
except Exception as e:
    print(f"ERROR: {e}")
