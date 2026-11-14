# 群友日本音乐成分表 · 服务器部署说明（单文件版）

你只要上传 **一个文件**：`app_standalone.py`。
HTML/CSS/JS 已经全部打包在这个 Python 文件里，不需要再传 `public/` 目录。

---

## 一、先上传

用宝塔的「文件」管理器 / FTP / scp，把 `app_standalone.py` 传到服务器任意目录，例如：

```
/www/wwwroot/jpmusic/app_standalone.py
```

> 数据（群友登记、词条、选择）会自动保存在同目录的 `data.json` 里；备份或搬家时只拷这个 `data.json` 就行。

## 二、试跑（先确认能跑）

SSH 登录服务器后：

```bash
cd /www/wwwroot/jpmusic
python3 --version                 # 没有就装：apt install -y python3（Ubuntu/Debian）或 yum install -y python3（CentOS）
JPM_PORT=8788 python3 app_standalone.py
```

看到 `群友日本音乐成分表 running: http://0.0.0.0:8788` 就说明跑起来了。
浏览器打开 `http://服务器公网IP:8788` 检查一下页面能不能打开（能打开再继续）。
按 Ctrl+C 可以停掉。

## 三、让它常驻 + 用 80 端口（两种方式任选一种）

### 方式 A：宝塔「网站」+ 反向代理（推荐，最省事）

1. 宝塔 → 网站 → 添加站点，域名填你的域名或服务器 IP，PHP 选「纯静态」。
2. 找到刚才的站点 → 设置 → 「反向代理」→ 添加：
   - 代理名称：`jpmusic`
   - 目标 URL：`http://127.0.0.1:8788`
   - 发送域名：`$host`
3. 宝塔「网站」→ 找到站点目录，把 `app_standalone.py` 传进站点根目录，然后在宝塔的「计划任务」里加一个「Shell 脚本」每分钟检查（或直接用下面的 systemd）：

```bash
#!/bin/bash
pgrep -f "app_standalone.py" >/dev/null || (cd /www/wwwroot/jpmusic && JPM_PORT=8788 nohup python3 app_standalone.py > app.log 2>&1 &)
```

### 方式 B：systemd 常驻（干净，开机自启）

新建 `/etc/systemd/system/jpmusic.service`：

```ini
[Unit]
Description=Japanese music fans site
After=network.target

[Service]
WorkingDirectory=/www/wwwroot/jpmusic
Environment=JPM_PORT=8788
ExecStart=/usr/bin/python3 app_standalone.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

然后：

```bash
systemctl daemon-reload
systemctl enable --now jpmusic
systemctl status jpmusic          # 看是否 running
```

之后用宝塔把站点的 80 反代到 `127.0.0.1:8788`（同方式 A 第 2 步），
或者你愿意直接把服务跑在 80 端口也行（需要 root，且确保 80 没被 nginx 占用）：

```bash
JPM_PORT=80 python3 app_standalone.py
```

## 四、腾讯云控制台：放行端口

腾讯云控制台 → 云服务器 / 轻量应用服务器 → 防火墙（安全组）→ 添加规则：
- 用 80 端口：放行 TCP 80（和 443，如果之后配 SSL）
- 直接 IP:8788：放行 TCP 8788

> 宝塔面板里也可能有「安全」页要单独放行一次。

## 五、改代码/更新

以后要更新：把新的 `app_standalone.py` 覆盖上去，`systemctl restart jpmusic`（或杀掉进程重新起）即可，`data.json` 不会丢。

## 六、常见问题

- **打不开页面**：先 `curl http://127.0.0.1:8788/api/health` 在服务器上本地测；本地通、外网不通 → 99% 是安全组/防火墙没放行。
- **python3 版本**：需要 3.7+（腾讯云默认镜像一般都满足）。
- **数据放哪**：`app_standalone.py` 同目录的 `data.json`；想换位置用 `JPM_DATA=/data/jpmusic.json`。
- **只想查看数据**：`cat data.json`，里面是明文 JSON（QQ、名字、词条、选择），不对外暴露。
