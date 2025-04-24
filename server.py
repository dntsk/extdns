#!/usr/bin/env python

import time
import docker
import os
import json
import requests
from loguru import logger
from modules import cf

# Configuration
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
DNS_RECORDS_FILE = os.path.join(DATA_DIR, "dns_records.json")

# Environment variables
DNS_UPDATE_INTERVAL = int(os.getenv('DNS_UPDATE_INTERVAL', 300))  # DNS and public IP check interval (seconds)
PUBLIC_IP_QUERY_URL = os.getenv('PUBLIC_IP_QUERY_URL', 'https://ifconfig.me/ip')

# Status variables
current_public_ip = None

# Docker client
docker_client = docker.from_env()

def fetch_public_ip():
    """Get current public IP address"""
    global current_public_ip
    
    try:
        response = requests.get(PUBLIC_IP_QUERY_URL, timeout=10)
        if response.status_code == 200:
            current_public_ip = response.text.strip()
            logger.info(f'Public IP retrieved: {current_public_ip}')
    except Exception as e:
        logger.error(f'Failed to get public IP: {e}')
        if current_public_ip is None:
            current_public_ip = "0.0.0.0"
    
    return current_public_ip

def load_dns_records():
    """Load DNS records from file"""
    if os.path.exists(DNS_RECORDS_FILE):
        try:
            with open(DNS_RECORDS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f'Failed to load DNS records file: {e}')
    return {}

def save_dns_records(dns_records):
    """Save DNS records to file"""
    try:
        with open(DNS_RECORDS_FILE, 'w') as f:
            json.dump(dns_records, f, indent=2)
    except Exception as e:
        logger.error(f'Failed to save DNS records file: {e}')

def get_running_containers():
    """Get currently running containers"""
    try:
        containers = docker_client.containers.list()
        return {c.id: {'name': c.name, 'labels': c.labels} for c in containers}
    except Exception as e:
        logger.error(f'Failed to get container list: {e}')
        return {}

def scan_container_dns_labels(running_containers, public_ip, saved_records):
    """Scan container labels for DNS record information"""
    dns_updates = {'cf': []}
    has_record_changes = False
    
    # Iterate through all running containers
    for container_id, container_info in running_containers.items():
        container_labels = container_info['labels']
        container_name = container_info['name']
        
        for label_name, domain_name in container_labels.items():
            # Only process DNS FQDN labels
            if not (label_name.startswith('extdns.cf.') and label_name.endswith('.fqdn')):
                continue
                
            parts = label_name.split('.')
            service_name = parts[2]  # Service identifier, can be custom (e.g., 'nginx', 'web', etc.)
            
            # Determine IP address
            ip_label = f'extdns.cf.{service_name}.ip'
            auto_ip_label = f'extdns.cf.{service_name}.auto_ip'
            
            # Prioritize specified IP, then use automatic IP
            if ip_label in container_labels:
                target_ip = container_labels[ip_label]
                logger.debug(f'Using specified IP: {target_ip} for {domain_name}')
            elif auto_ip_label in container_labels and container_labels[auto_ip_label].lower() in ('true', 'yes', '1', 'on'):
                target_ip = public_ip
                logger.debug(f'Using public IP: {target_ip} for {domain_name}')
            else:
                logger.warning(f'Skipping {domain_name}: No IP address specified and auto IP not enabled')
                continue
            
            # Set Cloudflare proxy status
            enable_proxy = False
            cloudflare_proxy_label = f'extdns.cf.{service_name}.cloudflare_proxy'
            if cloudflare_proxy_label in container_labels:
                proxy_value = container_labels[cloudflare_proxy_label].lower()
                enable_proxy = proxy_value in ('true', 'yes', '1', 'on')
            
            # Check if the record needs updating
            needs_update = True
            if 'domains' in saved_records and domain_name in saved_records['domains']:
                old_record = saved_records['domains'][domain_name]
                if (old_record.get('ip') == target_ip and 
                    old_record.get('proxied') == enable_proxy and 
                    old_record.get('container_id') == container_id):
                    needs_update = False
            
            if needs_update:
                has_record_changes = True
                logger.info(f'DNS record changed: {domain_name} -> {target_ip}, Cloudflare proxy={enable_proxy}')
            
            # Update record information
            if 'domains' not in saved_records:
                saved_records['domains'] = {}
            
            saved_records['domains'][domain_name] = {
                'container_id': container_id,
                'container_name': container_name,
                'ip': target_ip,
                'proxied': enable_proxy,
                'auto_ip': ip_label not in container_labels,
                'last_updated': int(time.time())
            }
            
            dns_updates['cf'].append({
                'domain': domain_name,
                'ip': target_ip,
                'proxied': enable_proxy
            })
    
    return dns_updates, has_record_changes

def find_dns_records_to_delete(running_containers, saved_records):
    """Find DNS records that need to be deleted"""
    records_to_delete = []
    
    if 'domains' in saved_records:
        for domain_name, record_info in list(saved_records['domains'].items()):
            container_id = record_info.get('container_id')
            container_name = record_info.get('container_name', container_id)
            
            if not container_id or container_id not in running_containers:
                logger.info(f'Container {container_name} does not exist or is not running, will delete domain {domain_name}')
                records_to_delete.append(domain_name)
                del saved_records['domains'][domain_name]
    
    return records_to_delete

def main_loop():
    """Main loop"""
    # Initialize public IP
    public_ip = fetch_public_ip()
    logger.info(f'Initial public IP: {public_ip}')
    
    while True:
        # Update public IP
        public_ip = fetch_public_ip()
        
        # Load existing DNS records
        saved_records = load_dns_records()
        
        # Check for IP changes
        if 'public_ip' in saved_records and saved_records['public_ip'] != public_ip:
            logger.info(f'Public IP has changed: {saved_records["public_ip"]} -> {public_ip}')
        
        # Update stored public IP
        saved_records['public_ip'] = public_ip
        
        # Get running containers
        running_containers = get_running_containers()
        
        # Find records to delete
        dns_records_to_delete = find_dns_records_to_delete(running_containers, saved_records)
        
        # Delete records
        if dns_records_to_delete:
            logger.info(f'Deleting {len(dns_records_to_delete)} DNS records: {", ".join(dns_records_to_delete)}')
            cf.delete_dns_records(dns_records_to_delete)
        
        # Scan DNS records
        dns_updates, has_record_changes = scan_container_dns_labels(
            running_containers, public_ip, saved_records
        )
        
        # Save records
        save_dns_records(saved_records)
        
        # Update DNS records
        if dns_updates['cf']:
            if has_record_changes:
                logger.info(f'Updating {len(dns_updates["cf"])} DNS records')
                cf.update_dns_records(dns_updates)
            else:
                logger.info(f'Skipping {len(dns_updates["cf"])} unchanged DNS records')
        else:
            logger.info('No DNS records to process')
        
        # Wait for next check
        logger.info(f'Waiting {DNS_UPDATE_INTERVAL} seconds for next check')
        time.sleep(DNS_UPDATE_INTERVAL)

if __name__ == "__main__":
    main_loop()
