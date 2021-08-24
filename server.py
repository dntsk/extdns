#!/usr/bin/env python

import time
import docker
import os
import requests
from loguru import logger
from modules import cf

sleep_timeout = os.getenv('SLEEP_TIMEOUT', 300)

use_ssh_client = False
docker_host = os.getenv('DOCKER_HOST', None)
if docker_host and docker_host.startswith("ssh://"):
    use_ssh_client = True

client = docker.from_env(use_ssh_client=use_ssh_client)

while True:
    ip = os.getenv('EXTERNAL_IP', None)
    if ip is None:
        ip = requests.get(url='https://ifconfig.me/ip').text

    records_list = {}

    for c in client.containers.list():
        for label, domain in c.labels.items():
            if label.startswith('extdns.'):
                module = label.split('.')[1]
                if module == 'cf':
                    if 'cf' in records_list:
                        records_list['cf'].append(domain)
                    else:
                        records_list['cf'] = []
                        records_list['cf'].append(domain)

    logger.info(f'INFO: extracted domains from docker labels: {records_list}')
    cf.update(records_list, ip)
    time.sleep(sleep_timeout)
