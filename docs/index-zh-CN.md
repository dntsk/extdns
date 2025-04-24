# ExtDNS

![License](https://img.shields.io/github/license/dntsk/extdns)

此项目受 [External DNS](https://github.com/kubernetes-sigs/external-dns) 的启发，ExtDNS 可以自动将 Docker 容器的 Label 中定义的 DNS 记录，同步到 DNS 提供商。

- ExtDNS 使用 `/var/run/docker.sock` 接口，查询容器的 Label 中定义的 DNS 记录。然后在公共 DNS 中创建记录。
- 支持在 Label 中自定义 DNS IP 地址，例如私有 IP 地址。
- 或者启用自动查询公共 IP 地址功能。
- 当 Label 中的 DNS 记录，或者公共 IP 地址发生变化时，ExtDNS 会自动更新 DNS 记录。
- 当容器被删除时，ExtDNS 会自动删除 DNS 记录。
- 默认每 300 秒检查一次。

## 源代码

源代码位于 [GitHub 仓库](https://github.com/dntsk/extdns) 中。

如果您发现这个项目对您有用，请考虑给我们一个 ⭐。

## 支持的 DNS 服务

当前支持的 DNS 提供商，以及可用性状态：

| 提供商         | 状态 | 维护者 |
| -------------- | ---- | ------ |
| CloudFlare DNS | Beta |        |

## 运行 ExtDNS

要运行 ExtDNS，您只需要设置所需的环境变量，并启动容器，然后为其他需要同步到 DNS 的 Docker 容器设置标签。

参考 `docker-compose.yml` 文件作为示例。

## Docker Label

| Label 名称                             | 描述                                                            |
| -------------------------------------- | --------------------------------------------------------------- |
| extdns.cf.nginx.fqdn=www.example.com   | 完全限定域名                                                    |
| extdns.cf.nginx.ip=192.168.1.11        | 自定义 IP 地址                                                  |
| extdns.cf.nginx.auto_ip=false          | 启用自动检测公共 IP，**注意** 自定义 IP 地址需要设置为 false    |
| extdns.cf.nginx.cloudflare_proxy=false | 启用 Cloudflare DNS 代理, **注意** 私有 IP 地址需要设置为 false |

## Docker 环境变量

| 环境变量            | 默认值                 | 描述                                                                                                                                            |
| ------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| CF_TOKEN            |                        | CloudFlare 令牌。如何获取它[请点击这里](https://developers.cloudflare.com/api/tokens/create)。它需要`Zone.Zone`、`Zone.DNS`权限来读取和更新记录 |
| DNS_TTL             | 600                    | 新创建和更新的 DNS 记录的 TTL（秒）                                                                                                             |
| DNS_UPDATE_INTERVAL | 300                    | 检查和更新记录之间的睡眠时间                                                                                                                    |
| PUBLIC_IP_QUERY_URL | https://ifconfig.me/ip | 公共 IP 查询 URL                                                                                                                                |

## 贡献

如果您想报告 bug 或请求新功能，请随时创建新的 issue 或 pull request。

需要英语校对，请随时在此 Readme 或源代码中纠正英语语法。
