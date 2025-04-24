# import CloudFlare
from cloudflare import Cloudflare, APIError
import os
from loguru import logger


def update_dns_records(dns_updates):
    """Update DNS records in Cloudflare"""
    if 'cf' not in dns_updates or not dns_updates['cf']:
        logger.info('No DNS records to update')
        return
        
    dns_ttl = int(os.getenv('DNS_TTL', 600))
    cf_client = _get_cloudflare_client()
    if not cf_client:
        return
        
    stats = {'created': 0, 'updated': 0, 'unchanged': 0, 'ip_changed': 0}

    try:
        # Get all zones
        cf_zones = cf_client.zones.list().result
        logger.info('Retrieving Cloudflare zone list')

        for zone in cf_zones:
            zone_id = zone.id
            zone_name = zone.name
            
            # Get all records for this zone
            zone_records = cf_client.dns.records.list(zone_id=zone_id).result
            logger.info(f'Retrieving DNS records for zone {zone_name}')

            # Process each record that needs updating
            for dns_record in dns_updates['cf']:
                domain_name = dns_record['domain']
                target_ip = dns_record['ip']
                enable_proxy = dns_record.get('proxied', False)
                
                # Check if domain belongs to current zone
                if not domain_name.endswith(zone_name):
                    continue
                    
                # Check if record already exists
                record_exists = False
                for cf_record in zone_records:
                    if domain_name.strip() == cf_record.name.strip() and cf_record.type == 'A':
                        record_exists = True
                        needs_update = False
                        
                        # Check if IP needs updating
                        if target_ip != cf_record.content:
                            logger.info(f'IP address change detected: {domain_name} from {cf_record.content} to {target_ip}')
                            needs_update = True
                            stats['ip_changed'] += 1
                            
                        # Check if Cloudflare proxy status needs updating  
                        if enable_proxy != cf_record.proxied:
                            logger.info(f'Cloudflare proxy status change detected: {domain_name} from {cf_record.proxied} to {enable_proxy}')
                            needs_update = True
                        
                        # Update record if needed
                        if needs_update:
                            try:
                                cf_client.dns.records.update(
                                    zone_id=zone_id, 
                                    dns_record_id=cf_record.id,
                                    type='A',
                                    name=domain_name,
                                    content=target_ip,
                                    ttl=dns_ttl,
                                    proxied=enable_proxy
                                )
                                logger.info(f'Successfully updated DNS record: {domain_name} -> {target_ip}, Cloudflare proxy={enable_proxy}')
                                stats['updated'] += 1
                            except APIError as e:
                                logger.error(f'Failed to update DNS record {domain_name}: {e}')
                        else:
                            stats['unchanged'] += 1
                        break

                # Create new record if it doesn't exist
                if not record_exists:
                    try:
                        cf_client.dns.records.create(
                            zone_id=zone_id,
                            type='A',
                            name=domain_name,
                            content=target_ip,
                            ttl=dns_ttl,
                            proxied=enable_proxy
                        )
                        logger.info(f'Successfully created DNS record: {domain_name} -> {target_ip}, Cloudflare proxy={enable_proxy}')
                        stats['created'] += 1
                    except APIError as e:
                        logger.error(f'Failed to create DNS record {domain_name}: {e}')
        
        # Log operation summary
        if stats['created'] > 0 or stats['updated'] > 0 or stats['unchanged'] > 0:
            logger.info(f'DNS record operation summary: Created {stats["created"]}, Updated {stats["updated"]} (IP changes: {stats["ip_changed"]}), Unchanged {stats["unchanged"]}')

    except APIError as e:
        logger.error(f'Cloudflare API error: {e}')
    except Exception as e:
        logger.error(f'Error processing DNS records: {e}')


def delete_dns_records(domains_to_delete):
    """Delete DNS records from Cloudflare"""
    if not domains_to_delete:
        return
    
    cf_client = _get_cloudflare_client()
    if not cf_client:
        return
    
    deleted_count = 0
    failed_count = 0
    
    try:
        # Get all zones
        cf_zones = cf_client.zones.list().result
        
        for domain_name in domains_to_delete:
            logger.info(f'Attempting to delete DNS record: {domain_name}')
            domain_deleted = False
            
            # Find zone for this domain
            for zone in cf_zones:
                zone_name = zone.name
                if not domain_name.endswith(zone_name):
                    continue
                
                zone_id = zone.id
                
                # Get all records for this zone
                try:
                    zone_records = cf_client.dns.records.list(zone_id=zone_id).result
                    
                    # Find matching records
                    for record in zone_records:
                        if record.name == domain_name and record.type == 'A':
                            # Delete record
                            try:
                                cf_client.dns.records.delete(zone_id=zone_id, dns_record_id=record.id)
                                logger.info(f'Successfully deleted DNS record: {domain_name}')
                                domain_deleted = True
                                deleted_count += 1
                            except APIError as e:
                                logger.error(f'Failed to delete DNS record {domain_name}: {e}')
                                failed_count += 1
                except APIError as e:
                    logger.error(f'Failed to query DNS records for {domain_name}: {e}')
                    failed_count += 1
            
            if not domain_deleted:
                logger.warning(f'DNS record not found for deletion: {domain_name}')
                
        logger.info(f'DNS record deletion summary: Successfully deleted {deleted_count}, Failed to delete {failed_count}')
                
    except APIError as e:
        logger.error(f'Cloudflare API deletion error: {e}')
    except Exception as e:
        logger.error(f'Error during DNS record deletion: {e}')


def _get_cloudflare_client():
    """Get Cloudflare API client instance"""
    cf_token = os.getenv('CF_TOKEN')
    if not cf_token:
        logger.error('Cloudflare API Token not found in environment variables')
        return None
        
    return Cloudflare(api_token=cf_token)
