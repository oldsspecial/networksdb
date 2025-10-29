#!/usr/bin/env python3
"""Check what's in the Parquet test data."""

import polars as pl

# Read the test data
df = pl.read_parquet('/Users/user/git/ziptie-group/networksdb/data/network_data.parquet')

print("Parquet DataFrame shape:", df.shape)
print("\nColumns:", df.columns)
print("\nSchema:")
print(df.schema)
print("\nFirst row:")
print(df.head(1))
