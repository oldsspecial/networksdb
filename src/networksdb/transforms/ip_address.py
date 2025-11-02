from functools import lru_cache
from ipaddress import ip_address
from ziptie_schema.transforms.markers import classifier, normalizer, validator, auto_labels

@lru_cache(maxsize=128)
def ip_info(s: str) -> dict:
    ip = ip_address(s)
    return {
        "normalized_address" : str(ip),
        "is_private": ip.is_private,
        "is_loopback": ip.is_loopback,
        "version": ip.version
    }

@classifier
def classify_ip(props: dict)-> str:
    ip = ip_info(props['address'])
    if ip['is_private']:
        return 'PrivateIPAddress'
    else:
        return 'PublicIPAddress'
    
@normalizer
def normalize_ip(value: str):
    ip = ip_info(value)
    return ip['normalized_address'].lower()

@auto_labels
def auto_label(ip_data: dict)->list[str]:
    labels = []
    ip = ip_info(ip_data)
    if ip['version'] == 4:
        labels.append('IPv4Address')
    elif ip['version'] == 6:
        labels.append('IPv6Addres')
    else:
        raise ValueError("Unknown ipaddress version")
    return labels
