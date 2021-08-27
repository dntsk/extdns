# ExtDNS for docker-compose

![License](https://img.shields.io/github/license/dntsk/extdns)

ExtDNS synchronizes labeled records in docker-compose with DNS providers.

Inspired by [External DNS](https://github.com/kubernetes-sigs/external-dns), ExtDNS makes resources discoverable via public DNS. It retrieves a list of records from Docker's labels and creates it in public DNS.

## Source code

The sources is placed in [GitHub repository](https://github.com/dntsk/extdns).

If you find this project useful for you, please consider giving us a ⭐.

## Supported DNS services

The following table clarifies the current status of the providers according to the aforementioned stability levels:

| Provider       | Status | Maintainers |
| -------------- | ------ | ----------- |
| CloudFlare DNS | Beta   |             |

## Running ExternalDNS

To run your ExtDNS you just need to spinup container with needed environment variables and set labels to your docker container.

Use `docker-compose.yml` as an example.

## Environment variables

| Environment variable | Default value | Description |
|----------------------|---------------|-------------|
| CF_TOKEN             |               | CloudFlare token. How to obtain it [read here](https://developers.cloudflare.com/api/tokens/create). It needs `Zone.Zone`, `Zone.DNS` permissions to read and update records
| TTL                  | 60            | TTL in seconds for newly created and updated DNS records
| SLEEP_TIMEOUT        | 300           | Sleep time between check and update records
| EXTERNAL_IP          |               | Use this external IP address in DNS records


## Contribute

If you want to report a bug or request a new feature. Free feel to open a new issue.

If you want to modify Uptime Kuma, this guideline maybe useful for you: https://github.com/dntsk.extdns/blob/master/CONTRIBUTING.md

English proofreading is needed too, because my grammar is not that great sadly. Feel free to correct my grammar in this Readme or source code.
