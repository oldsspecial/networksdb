#!/usr/bin/env python3
"""Debug what columns are in the DataFrame before Iceberg writing."""

import os
os.environ['ZIPTIE_FIXTURE_DATA'] = '/Users/user/git/ziptie-group/ziptie-schema/src/ziptie_schema/fixtures/data'

import sys
sys.path.insert(0, '/Users/user/git/ziptie-group/ziptie-parsing/src')

# Import necessary modules
from ziptie_parsing.stages.data_types import Entities, DataAdapter
from ziptie_schema.fixtures import get_sample_entities

# Get sample entities
entities = get_sample_entities()

# Convert to DataFrame
df = DataAdapter.entities_to_dataframe(entities)

print("DataFrame columns:")
print(df.columns)

print("\nDataFrame schema:")
print(df.schema)

print("\nSample node dict (first node):")
if entities.nodes:
    node = entities.nodes[0]
    if hasattr(node, 'to_dict'):
        node_dict = node.to_dict(separate_dynamic_properties=True)
        print(node_dict)
