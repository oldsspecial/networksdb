#!/usr/bin/env python3
"""Verify Iceberg table schemas match canonical format."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

catalog_config = {
    "type": "hive",
    "uri": os.getenv("HIVE_METASTORE_URI"),
    "s3.endpoint": os.getenv("MINIO_ENDPOINT"),
    "s3.access-key-id": os.getenv("MINIO_ACCESS_KEY"),
    "s3.secret-access-key": os.getenv("MINIO_SECRET_KEY"),
    "s3.path-style-access": "true",
}

try:
    from pyiceberg.catalog import load_catalog
    
    catalog = load_catalog(name="verify_schema", **catalog_config)
    
    print("=" * 80)
    print("NODES TABLE SCHEMA")
    print("=" * 80)
    nodes_table = catalog.load_table("network.nodes")
    print(f"\nNamespace: network")
    print(f"Table: nodes")
    print(f"Partition spec: {nodes_table.spec()}")
    print(f"\nColumns:")
    for field in nodes_table.schema().fields:
        print(f"  - {field.name}: {field.field_type}")
    
    print("\n" + "=" * 80)
    print("RELATIONSHIPS TABLE SCHEMA")
    print("=" * 80)
    rels_table = catalog.load_table("network.relationships")
    print(f"\nNamespace: network")
    print(f"Table: relationships")
    print(f"Partition spec: {rels_table.spec()}")
    print(f"\nColumns:")
    for field in rels_table.schema().fields:
        print(f"  - {field.name}: {field.field_type}")
    
    # Check canonical format compliance
    print("\n" + "=" * 80)
    print("CANONICAL FORMAT COMPLIANCE CHECK")
    print("=" * 80)
    
    required_node_fields = ["node_id", "schema_version", "primary_label", "labels", 
                           "identifying_properties", "properties", "dynamic_properties"]
    required_rel_fields = ["rel_id", "schema_version", "rel_type", "start_node", "end_node",
                          "identifying_properties", "properties", "dynamic_properties"]
    
    forbidden_node_fields = ["rel_id", "rel_type", "start_node", "end_node"]
    forbidden_rel_fields = ["node_id", "primary_label", "labels"]
    
    nodes_fields = [f.name for f in nodes_table.schema().fields]
    rels_fields = [f.name for f in rels_table.schema().fields]
    
    print("\n✓ NODES TABLE:")
    for field in required_node_fields:
        if field in nodes_fields:
            print(f"  ✓ Has required field: {field}")
        else:
            print(f"  ✗ MISSING required field: {field}")
    
    for field in forbidden_node_fields:
        if field in nodes_fields:
            print(f"  ✗ ERROR: Has forbidden relationship field: {field}")
        else:
            print(f"  ✓ Correctly excludes: {field}")
    
    print("\n✓ RELATIONSHIPS TABLE:")
    for field in required_rel_fields:
        if field in rels_fields:
            print(f"  ✓ Has required field: {field}")
        else:
            print(f"  ✗ MISSING required field: {field}")
    
    for field in forbidden_rel_fields:
        if field in rels_fields:
            print(f"  ✗ ERROR: Has forbidden node field: {field}")
        else:
            print(f"  ✓ Correctly excludes: {field}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
