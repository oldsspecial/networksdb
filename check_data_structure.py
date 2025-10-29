#!/usr/bin/env python3
"""Check the structure of data coming from parsing."""

import sys
sys.path.insert(0, '/Users/user/git/ziptie-group/ziptie-parsing/src')
sys.path.insert(0, '/Users/user/git/ziptie-group/networksdb')

import polars as pl
from networksdb.nodes import IPAddress, SubnetAddress, Domain
from networksdb.relationships import Contains, Connected

# Create sample entities
node1 = IPAddress(ip_address="192.168.1.1")
node2 = Domain(domain="example.com")

# Convert to dict with separate_dynamic_properties=True
node1_dict = node1.to_dict(separate_dynamic_properties=True)
node2_dict = node2.to_dict(separate_dynamic_properties=True)

print("Node 1 dict keys:")
print(list(node1_dict.keys()))

print("\nNode 1 dict:")
for key, value in node1_dict.items():
    print(f"  {key}: {value} ({type(value).__name__})")

print("\n" + "="*80)
print("\nNode 2 dict keys:")
print(list(node2_dict.keys()))

print("\nNode 2 dict:")
for key, value in node2_dict.items():
    print(f"  {key}: {value} ({type(value).__name__})")
