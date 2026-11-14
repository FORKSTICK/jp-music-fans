# 多群 / 多实例部署

一个实例 = 一份 `data.json` + 一个端口 + 一个公网入口。想让别的群也用，不要复制用户数据，复制「程序」就行。

## 一、同一台电脑再开一个群

1. 复制一份目录（只复制程序，不复制 data.json）：

   ```powershell
   robocopy D:\DeepSeekHarness\default-workspace\jp-music-fans D:\jp-music-fans-2 /E /XD node_modules .git backups tools
   ```

2. 用另一个端口、另一个数据文件启动：

   ```powershell
   cd D:\jp-music-fans-2
   $env:JPM_PORT = '8789'
   $env:JPM_DATA = 'D:\jp-music-fans-2\data.json'
   C:\Users\Pkochan\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe server.py
   ```

   或者用脚本（带固定域名、开机自启同理）：

   ```powershell
   powershell -File .\start-local.ps1 -Port 8789 -Data D:\jp-music-fans-2\data.json
   ```

   注意：`tools\ngrok.yml` 里的 authtoken 可以共用，但 `--domain` 必须是 ngrok 上你预留的另一个固定域名（免费账号通常只能留一个），所以第二个群建议先不加 `-Domain`，改用临时地址，或升级 ngrok / 换 Cloudflare 命名隧道。

## 二、一台电脑一个群（推荐）

- 第二个群直接放另一台电脑或云服务器上，照 `README-deploy.md` 上传 `app_standalone.py` 或本目录的 `server.py` + `public/`。
- 数据互不影响，各用各的 `data.json`。

## 三、需要隔离的东西

| 内容 | 是否共享 | 说明 |
| --- | --- | --- |
| `data.json` | 不共享 | 每实例一份；用 `JPM_DATA` 指定 |
| 端口 | 不共享 | `JPM_PORT`，默认 8788 |
| 管理员密码 | 不共享 | 每实例自己的 `settings.adminPasswordHash` |
| `tools/ngrok.yml` | 可共享 | authtoken 相同；domain 每个群要不同 |
| 备份 `backups/` | 不共享 | 每实例自己的历史快照 |

## 四、迁移/备份

- 备份 = 复制 `data.json` 和 `backups/`；
- 换电脑 = 带上这两样 + `public/` + `server.py`，端口不变即可；
- 后台「导出全部数据」也能拿到完整 JSON。
