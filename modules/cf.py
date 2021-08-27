import CloudFlare
import os
from loguru import logger


def update(docker_records_list, ip):
    ttl = os.getenv('TTL', 60)

    zones = _get_zones()
    logger.info('INFO: got list of all zones')

    for zone in zones:
        zone_id = zone['id']
        controlled_records = []
        control_record_id = None
        old_records = None
        perform_actions = False
        records = _get_dns_records(zone_id)
        logger.info(f'INFO: got list of all records for {zone["name"]}')

        for record in docker_records_list['cf']:
            data = {'name': record, 'type': 'A', 'content': ip, 'ttl': ttl, 'proxied': True}
            if record.endswith(zone['name']):
                perform_actions = True
                found = False
                for cf_record in records:
                    if record.strip() == cf_record['name'].strip() and cf_record['type'] == 'A':
                        found = True
                        old_ip_address = cf_record['content']
                        controlled_records.append(record)

                        if ip != old_ip_address:
                            try:
                                cf.zones.dns_records.put(zone_id, cf_record['id'], data=data)
                                logger.info(f'UPDATED: {record} with IP address {ip}')
                            except CloudFlare.exceptions.CloudFlareAPIError as e:
                                logger.info(f'UNCHANGED: {record} already exists with IP address {ip}')
                        else:
                            logger.info(f'UNCHANGED: {record} already has IP address {ip}')

                    if cf_record['name'].strip() == f'_extdns.{zone["name"]}'.strip():
                        old_records = cf_record['content'].split(',')
                        control_record_id = cf_record['id']

                if not found:
                    cf.zones.dns_records.post(zone_id, data=data)
                    logger.info(f'CREATED: {record} with IP address {ip}')

        if perform_actions:
            _set_extdns_record(zone_id, control_record_id, controlled_records)
            _cleanup(zone_id, old_records, controlled_records, records)


def _set_extdns_record(zone_id, control_record_id, controlled_records):
    instance_id = os.getenv('INSTANCE_ID', 0)

    extdns_record = ','.join(controlled_records)
    data = {'name': f'_extdns_{instance_id}', 'type': 'TXT', 'content': f'{extdns_record}'}

    if control_record_id:
        if len(controlled_records) > 0:
            logger.info(f'CONTROL: control record found. Updating one with list of records: {extdns_record}')
        cf.zones.dns_records.put(zone_id, control_record_id, data=data)
    else:
        if len(controlled_records) > 0:
            logger.info(f'CONTROL: control record not found ({control_record_id}). Creating one with list of '
                        f'records: {extdns_record}')
        cf.zones.dns_records.post(zone_id, data=data)


def _cleanup(zone_id, old_records, controlled_records, records):
    if old_records:
        cleanup_records = list(set(old_records) - set(controlled_records))
        if len(cleanup_records) > 0:
            logger.info(f'CLEANUP: records to delete: {cleanup_records}')
            for r in records:
                if r['name'].strip() in cleanup_records:
                    cf.zones.dns_records.delete(zone_id, r['id'])
                    logger.info(f'CLEANUP: record {r["name"]} ({r["id"]}) was removed')


def _cf_connect():
    cf_token = os.getenv('CF_TOKEN', None)
    if cf_token is None:
        exit('No CloudFlare credentials found!')
    return CloudFlare.CloudFlare(token=cf_token)


def _get_dns_records(zone_id):
    try:
        return cf.zones.dns_records.get(zone_id, params={'per_page': 100})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones/dns_records.get %d %s - api call failed' % (e, e))


def _get_zones():
    try:
        return cf.zones.get()
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones.get %d %s - api call failed' % (e, e))
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))


cf = _cf_connect()
