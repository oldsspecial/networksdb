#!/usr/bin/env python3
"""Quick test script to verify data types in JSONL file."""

import json
import sys
from pathlib import Path

# Read first entity from JSONL file
jsonl_path = Path("network_nodes.jsonl")

if not jsonl_path.exists():
    print(f"Error: {jsonl_path} not found")
    sys.exit(1)

with open(jsonl_path, "r") as f:
    first_line = f.readline()
    entity = json.loads(first_line)

    print("=== Entity from JSONL ===")
    print(f"Type of entity: {type(entity)}")
    print(f"\nKeys: {list(entity.keys())}")

    for key, value in entity.items():
        print(f"\n{key}:")
        print(f"  Type: {type(value)}")
        print(f"  Value: {value}")

        # Check if it's actually a string when it should be a dict/list
        if key in ['identifying_properties', 'properties', 'dynamic_properties']:
            if isinstance(value, str):
                print(f"  ⚠️  WARNING: Expected dict, got string!")
            elif isinstance(value, dict):
                print(f"  ✓ Correct type (dict)")
        elif key == 'labels':
            if isinstance(value, str):
                print(f"  ⚠️  WARNING: Expected list, got string!")
            elif isinstance(value, list):
                print(f"  ✓ Correct type (list)")
