
from ipaddress import ip_address

from ziptie_schema.transforms.markers import classifier, normalizer, validator, auto_labels


@classifier
def classify_ip(props: dict) -> str:
    ip = ip_address(props['address'])
    if ip.is_private:
        return 'PrivateIPAddress'
    else:
        return 'PublicIPAddress'

@validator
def validate_domain(domain: str) -> bool:
    if domain.count(".") == 0:
        return False
    return True

@validator
def validate_email_address(address: str) -> bool:
    if address.find("@") != -1 and address.count(".") > 0:
        return True
    return False 

@normalizer
def normalize_ip(value: str) -> str:
    """Normalize IP address."""
    return value.lower()
    
# enrichers.py
@auto_labels
def enrich_domain_labels(data: dict) -> list[str]:
    fqdn = data.get('fqdn', '').lower()
    labels = []
    if fqdn.startswith('mx.'):
        labels.append('MailServer')
    if fqdn.startswith('www.'):
        labels.append('WebServer')
    return labels