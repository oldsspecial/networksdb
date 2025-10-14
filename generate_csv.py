#!/usr/bin/env python3
"""
Generate CSV data with IPv4 addresses and domain names.
Supports public, private, or mixed IP address generation with realistic domain names.
"""

import argparse
import csv
import random
import sys
from typing import List, Tuple


class NetworkDataGenerator:
    def __init__(self, ip_type: str = "public", duplication_percent: float = 20.0):
        self.ip_type = ip_type
        self.duplication_percent = duplication_percent

        # Base domains from various industries
        self.base_domains = [
            'example.com', 'testsite.org', 'mycompany.net', 'webapp.io',
            'cloudservice.com', 'dataplatform.co', 'techsolution.net',
            'webhost.org', 'apiservice.com', 'microservice.io',
            'acmecorp.com', 'globalsys.net', 'innovate.co', 'nextgen.io',
            'smarttech.com', 'digitalwave.org', 'cybersolutions.net', 'webdynamic.com',
            'cloudbase.io', 'techforge.org', 'datahub.co', 'netcore.com',
            'systemspro.net', 'webscale.io', 'devops.org', 'infrastructure.co',
            'enterprise.com', 'business.net', 'corporate.org', 'startup.io',
            'platform.co', 'framework.com', 'architecture.net', 'services.org',
            'solutions.io', 'technology.co', 'software.com', 'applications.net',
            'systems.org', 'network.io', 'security.co', 'analytics.com',
            'monitoring.net', 'performance.org', 'optimization.io', 'automation.co',
            'integration.com', 'deployment.net', 'operations.org', 'maintenance.io',
            'database.co', 'storage.com', 'computing.net', 'processing.org',
            'algorithms.io', 'machine-learning.co', 'artificial-intelligence.com', 'neural.net',
            'quantum.org', 'blockchain.io', 'cryptocurrency.co', 'fintech.com',
            'healthtech.net', 'biotech.org', 'medtech.io', 'pharma.co',
            'ecommerce.com', 'retail.net', 'marketplace.org', 'commerce.io',
            'logistics.co', 'supply-chain.com', 'transport.net', 'shipping.org',
            'energy.io', 'renewable.co', 'solar.com', 'wind.net',
            'manufacturing.org', 'automotive.io', 'aerospace.co', 'defense.com',
            'education.net', 'research.org', 'university.io', 'academy.co',
            'government.com', 'public.net', 'municipal.org', 'federal.io',
            'entertainment.co', 'media.com', 'streaming.net', 'gaming.org',
            'social.io', 'community.co', 'forum.com', 'network.net',
            'communication.org', 'messaging.io', 'chat.co', 'voice.com',
            'video.net', 'audio.org', 'podcast.io', 'broadcast.co'
        ]

        # Common subdomains for realistic variety
        self.subdomains = [
            '', 'www', 'api', 'cdn', 'mail', 'ftp', 'db', 'admin', 'secure',
            'app', 'mobile', 'web', 'portal', 'dashboard', 'console', 'panel',
            'blog', 'news', 'docs', 'help', 'support', 'shop', 'store',
            'dev', 'test', 'staging', 'prod', 'beta', 'alpha', 'demo',
            'static', 'assets', 'images', 'files', 'download', 'upload',
            'auth', 'login', 'account', 'profile', 'user', 'users',
            'search', 'index', 'catalog', 'directory', 'listing',
            'monitor', 'metrics', 'stats', 'analytics', 'tracking',
            'cache', 'proxy', 'gateway', 'router', 'load-balancer',
            'backup', 'archive', 'sync', 'mirror', 'replica'
        ]

        # Secondary subdomains for multi-level domains
        self.secondary_subdomains = [
            'east', 'west', 'north', 'south', 'central', 'eu', 'us', 'asia',
            'prod', 'dev', 'test', 'staging', 'internal', 'external',
            'primary', 'secondary', 'backup', 'mirror', 'edge',
            'node1', 'node2', 'cluster1', 'cluster2', 'shard1', 'shard2'
        ]

    def generate_public_ip(self) -> str:
        """Generate a valid public IPv4 address."""
        while True:
            # Generate random IP
            octets = [random.randint(1, 255) for _ in range(4)]
            ip = f"{octets[0]}.{octets[1]}.{octets[2]}.{octets[3]}"

            # Exclude private and reserved ranges
            if (octets[0] == 10 or
                (octets[0] == 172 and 16 <= octets[1] <= 31) or
                (octets[0] == 192 and octets[1] == 168) or
                octets[0] == 127 or octets[0] == 169 or octets[0] >= 224):
                continue

            return ip

    def generate_private_ip(self) -> str:
        """Generate a private IPv4 address."""
        ip_class = random.choice(['10', '172', '192'])

        if ip_class == '10':
            # 10.0.0.0/8
            return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        elif ip_class == '172':
            # 172.16.0.0/12
            return f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        else:
            # 192.168.0.0/16
            return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"

    def generate_ip(self) -> str:
        """Generate an IP address based on the configured type."""
        if self.ip_type == "public":
            return self.generate_public_ip()
        elif self.ip_type == "private":
            return self.generate_private_ip()
        elif self.ip_type == "mixed":
            # 70% public, 30% private for realistic mix
            if random.random() < 0.7:
                return self.generate_public_ip()
            else:
                return self.generate_private_ip()
        else:
            raise ValueError(f"Invalid ip_type: {self.ip_type}")

    def generate_domain(self) -> str:
        """Generate a realistic domain name with optional subdomains."""
        base_domain = random.choice(self.base_domains)

        # 40% chance of having a subdomain
        if random.random() < 0.4:
            subdomain = random.choice(self.subdomains)
            if subdomain:  # Skip empty string
                # 15% chance of having a secondary subdomain
                if random.random() < 0.15:
                    secondary = random.choice(self.secondary_subdomains)
                    return f"{subdomain}.{secondary}.{base_domain}"
                else:
                    return f"{subdomain}.{base_domain}"

        return base_domain

    def generate_data(self, num_rows: int) -> List[Tuple[str, str]]:
        """Generate network data rows with controlled duplication."""
        if self.duplication_percent < 0 or self.duplication_percent > 100:
            raise ValueError("Duplication percentage must be between 0 and 100")

        # Calculate how many unique rows we need
        unique_percent = 100 - self.duplication_percent
        unique_rows_needed = max(1, int(num_rows * unique_percent / 100))

        # Generate unique rows
        unique_data = []
        for i in range(unique_rows_needed):
            if i > 0 and i % 10000 == 0:
                print(f"Generated {i:,} unique rows...", file=sys.stderr)

            ip = self.generate_ip()
            domain = self.generate_domain()
            unique_data.append((ip, domain))

        # Create the final dataset with duplicates
        data = unique_data.copy()

        # Add duplicates if needed
        duplicates_needed = num_rows - unique_rows_needed
        if duplicates_needed > 0:
            for i in range(duplicates_needed):
                if i > 0 and i % 10000 == 0:
                    print(f"Added {i:,} duplicates...", file=sys.stderr)

                # Select a random row from unique data to duplicate
                duplicate_row = random.choice(unique_data)
                data.append(duplicate_row)

        # Shuffle the data to distribute duplicates randomly
        random.shuffle(data)

        return data

    def write_csv(self, data: List[Tuple[str, str]], output_file: str):
        """Write data to CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ipv4_address', 'domain'])
            writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(
        description="Generate CSV with IPv4 addresses and domain names"
    )
    parser.add_argument(
        "rows",
        type=int,
        help="Number of rows to generate"
    )
    parser.add_argument(
        "-o", "--output",
        default="network_data.csv",
        help="Output CSV filename (default: network_data.csv)"
    )
    parser.add_argument(
        "--ip-type",
        choices=["public", "private", "mixed"],
        default="public",
        help="Type of IP addresses to generate (default: public)"
    )
    parser.add_argument(
        "--duplication",
        type=float,
        default=20.0,
        help="Percentage of duplicate rows (0-100, default: 20)"
    )

    args = parser.parse_args()

    if args.rows <= 0:
        print("Error: Number of rows must be positive", file=sys.stderr)
        sys.exit(1)

    if args.duplication < 0 or args.duplication > 100:
        print("Error: Duplication percentage must be between 0 and 100", file=sys.stderr)
        sys.exit(1)

    print(f"Generating {args.rows:,} rows with {args.ip_type} IP addresses and {args.duplication}% duplication...", file=sys.stderr)

    generator = NetworkDataGenerator(args.ip_type, args.duplication)
    data = generator.generate_data(args.rows)
    generator.write_csv(data, args.output)

    print(f"Successfully generated {len(data):,} rows to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()