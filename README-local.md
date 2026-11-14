# 日本音乐成分表 · 本地部署说明

网站跑在这台电脑上（Windows），公网访问靠 cloudflared 快速隧道。不需要云服务器。

## 现在的情况

- 本机服务：http://127.0.0.1:8788 （Python 标准库，无第三方依赖）
- 公网地址：https://removable-subjective-cruz-yeast.trycloudflare.com
- 数据文件：本目录 `data.json`（每次写入都是「先写临时文件再替换」，不会写坏）
- 数据内容：群友的 QQ、名字、创建的词条、每个人选的词条

## 目录

| 文件 | 作用 |
| --- | --- |
| `server.py` | 本机服务（接口 + 静态页面） |
| `public/` | 网页（index.html / app.js / style.css） |
| `data.json` | 全部数据，备份直接复制这个文件 |
| `start-local.ps1` | 启动脚本：启动服务 + 隧道，并打印新的公网地址 |
| `tools/cloudflared.exe` | 隧道程序 |
| `app_standalone.py` | 单文件版（页面内嵌，供部署到服务器用） |
| `jp-music-fans-server.zip` | 单文件版打包（上传服务器用） |
| `build_single.py` | 改完页面后重新生成单文件版 |

## 开机自启

已在「启动」文件夹放了快捷方式：

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\jpm-music-fans.lnk
```

登录 Windows 后会静默执行 `start-local.ps1`，服务与隧道自动起来。

## 重启后公网地址会变

cloudflared 的免费快速隧道每次启动都会生成一个**新的随机地址**。所以：

1. 电脑重启 / 隧道断开后，需要重新取一次地址；
2. 取地址的方法：运行 `start-local.ps1`（会打印 `PUBLIC_URL=...`），或者看 `tunnel.err.log` / `tunnel.log` 里的 `https://xxxx.trycloudflare.com`；
3. 拿到新地址后发到群里替换旧链接即可。

想让地址固定，需要把域名托管到 Cloudflare 再用 named tunnel，那一步要域名和 `cloudflared tunnel login`。

## 停止

关掉对应的 python / cloudflared 进程即可，或者在 PowerShell 里：

```powershell
Get-NetTCPConnection -LocalPort 8788 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
```

## 备份 / 恢复

- 备份：复制 `data.json`（建议每天或每周一次）。
- 恢复：停服务 → 用备份覆盖 `data.json` → 重新启动。
