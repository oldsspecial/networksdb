#!/usr/bin/env python3
"""
Script to insert CSV data into Trino Iceberg table.
Usage: python insert_into_trino.py
"""

import csv
from trino.dbapi import connect
from trino.exceptions import TrinoUserError


def main():
    # Trino connection settings from parsers/trino.yaml
    conn = connect(
        host='localhost',
        port=8080,
        user='trino',
        catalog='iceberg',
        schema='testdb',
        http_scheme='http'
    )

    cur = conn.cursor()

    # Create table if it doesn't exist
    print("Creating table iceberg.testdb.50k_public...")
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS iceberg.testdb."50k_public" (
                ipv4_address VARCHAR,
                domain VARCHAR
            )
            WITH (format = 'PARQUET')
        """)
        print("Table created successfully.")
    except TrinoUserError as e:
        print(f"Error creating table: {e}")
        conn.close()
        return

    # Read CSV and insert in batches
    csv_file = 'data/50k_public.csv'
    batch_size = 10000

    print(f"Reading CSV file: {csv_file}")

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []
        total_inserted = 0

        for row in reader:
            # Escape single quotes in the data
            ipv4 = row['ipv4_address'].replace("'", "''")
            domain = row['domain'].replace("'", "''")
            batch.append(f"('{ipv4}', '{domain}')")

            if len(batch) >= batch_size:
                # Insert batch
                values = ',\n'.join(batch)
                insert_sql = f'INSERT INTO iceberg.testdb."50k_public" VALUES {values}'

                try:
                    cur.execute(insert_sql)
                    total_inserted += len(batch)
                    print(f"Inserted {total_inserted} rows...")
                    batch = []
                except TrinoUserError as e:
                    print(f"Error inserting batch: {e}")
                    conn.close()
                    return

        # Insert remaining rows
        if batch:
            values = ',\n'.join(batch)
            insert_sql = f'INSERT INTO iceberg.testdb."50k_public" VALUES {values}'

            try:
                cur.execute(insert_sql)
                total_inserted += len(batch)
                print(f"Inserted {total_inserted} rows...")
            except TrinoUserError as e:
                print(f"Error inserting final batch: {e}")
                conn.close()
                return

    # Verify the count
    print("\nVerifying insert...")
    cur.execute('SELECT COUNT(*) FROM iceberg.testdb."50k_public"')
    count = cur.fetchone()[0]
    print(f"Total rows in table: {count}")

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
