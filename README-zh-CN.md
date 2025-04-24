# ExtDNS

[English](./README.md) | [简体中文](./README-zh-CN.md)  

![License](https://img.shields.io/github/license/dntsk/extdns)  

此项目受 [External DNS](https://github.com/kubernetes-sigs/external-dns) 的启发，ExtDNS 可以自动将 Docker 容器的 Label 中定义的 DNS 记录，同步到 DNS 提供商。

- ExtDNS 使用 `/var/run/docker.sock` 接口，查询容器的 Label 中定义的 DNS 记录。然后在公共 DNS 中创建记录。
- 支持在 Label 中自定义 DNS IP 地址，例如私有 IP 地址。
- 或者启用自动查询公共 IP 地址功能。
- 当 Label 中的 DNS 记录，或者公共 IP 地址发生变化时，ExtDNS 会自动更新 DNS 记录。
- 当容器被删除时，ExtDNS 会自动删除 DNS 记录。
- 默认每300秒检查一次。
- 当前仅支持 CloudFlare DNS 提供商。

## 文档

所有文档都存放在 [docs](./docs/index-zh-CN.md) 文件夹中。

您也可以在 [官方网站](https://extdns.dntsk.dev) 上查看它。

## 贡献

如果您想报告 bug 或请求新功能，请随时创建新的 issue 或 pull request。

需要英语校对，请随时在此 Readme 或源代码中纠正英语语法。 

## 许可证

此项目使用 [MIT 许可证](./LICENSE)。

如果您发现这个项目对您有用，请考虑给我们一个 ⭐。