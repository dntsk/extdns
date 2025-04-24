# ExtDNS for docker-compose

![License](https://img.shields.io/github/license/dntsk/extdns)

ExtDNS synchronizes labeled records in docker-compose with DNS providers.

Inspired by [External DNS](https://github.com/kubernetes-sigs/external-dns), ExtDNS makes resources discoverable via public DNS. It retrieves a list of records from Docker's labels and creates it in public DNS.

- ExtDNS uses the `/var/run/docker.sock` to query DNS records defined in container labels and then creates these records in public DNS.
- Supports custom DNS IP address in labels, such as private IP address.
- Provides an option to automatically detect public IP and use it as DNS record.
- Automatically updates DNS records when IP address changes.
- Automatically removes DNS records when containers are deleted.
- Checks for changes every 300 seconds by default.

## Source code

The sources is placed in [GitHub repository](https://github.com/dntsk/extdns).

If you find this project useful for you, please consider giving us a ⭐.

## Supported DNS services

The following table clarifies the current status of the providers according to the aforementioned stability levels:

| Provider       | Status | Maintainers |
| -------------- | ------ | ----------- |
| CloudFlare DNS | Beta   |             |

## Running ExtDNS

To run your ExtDNS you just need to spinup container with needed environment variables and set labels to your docker container.

Use `docker-compose.yml` as an example.

## Docker Label

| Label                                  | Description                                                                        |
| -------------------------------------- | ---------------------------------------------------------------------------------- |
| extdns.cf.nginx.fqdn=www.example.com   | Fully Qualified Domain Name                                                        |
| extdns.cf.nginx.ip=192.168.1.11        | Custom IP address                                                                  |
| extdns.cf.nginx.auto_ip=false          | Enable auto-detect public IP, **note** custom IP address need to be set to false   |
| extdns.cf.nginx.cloudflare_proxy=false | Enable Cloudflare DNS proxy, **note** private IP addresses need to be set to false |

## Environment variables

| Environment variable | Default value          | Description                                                                                                                                                                  |
| -------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CF_TOKEN             |                        | CloudFlare token. How to obtain it [read here](https://developers.cloudflare.com/api/tokens/create). It needs `Zone.Zone`, `Zone.DNS` permissions to read and update records |
| DNS_TTL              | 600                    | TTL in seconds for newly created and updated DNS records                                                                                                                     |
| DNS_UPDATE_INTERVAL  | 300                    | Sleep time between check and update records                                                                                                                                  |
| PUBLIC_IP_QUERY_URL  | https://ifconfig.me/ip | Public IP query URL records                                                                                                                                                  |

## Contribute

If you want to report a bug or request a new feature. Free feel to open a new issue.

English proofreading is needed too, because my grammar is not that great sadly. Feel free to correct my grammar in this Readme or source code.
