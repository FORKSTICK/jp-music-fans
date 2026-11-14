import io, re, sys

p = 'server.py'
s = open(p, encoding='utf-8').read()

# 1) imports
old = "import urllib.parse\nimport uuid\n"
new = "import urllib.parse\nimport urllib.request\nimport urllib.error\nimport uuid\n"
if 'import urllib.request' not in s:
    assert old in s, 'imports anchor missing'
    s = s.replace(old, new, 1)

# 2) GET routes
anchor = '            if path == "/api/health":\n                return self.send_json({"ok": True, "time": int(time.time())})\n'
get_routes = anchor + '''            if path == "/api/qgroup/events":
                try:
                    limit = max(1, min(100, int(query.get("limit", ["20"])[0] or 20)))
                    offset = max(0, int(query.get("offset", ["0"])[0] or 0))
                except ValueError:
                    return self.send_json({"error": "分页参数不对"}, 400)
                lifecycle = (query.get("lifecycle", [""])[0] or "").strip()
                res = qgroup_events(limit, offset, lifecycle)
                if res.get("error"):
                    return self.send_json({"error": res["error"]}, res.get("status", 503))
                return self.send_json(res)
            if path == "/api/qgroup/event":
                eid = (query.get("id", [""])[0] or "").strip()
                if not eid:
                    return self.send_json({"error": "缺少活动 id"}, 400)
                payload = qgroup_event_payload(eid)
                if payload.get("error"):
                    return self.send_json({"error": payload["error"]}, payload.get("status", 400))
                return self.send_json(payload)
'''
if '"/api/qgroup/events"' not in s:
    assert anchor in s, 'health anchor missing'
    s = s.replace(anchor, get_routes, 1)

# 3) POST routes
old = '                "/api/room/recalc": self.api_room_recalc,\n'
if '"/api/qgroup/split"' not in s:
    assert old in s, 'post anchor missing'
    s = s.replace(old, old + '                "/api/qgroup/split": self.api_qgroup_split,\n                "/api/qgroup/rooms": self.api_qgroup_rooms,\n', 1)

# 4) class methods
anchor = '        return self.send_json({"rooms": out})\n\n    def api_shout(self, body):'
methods = '''        return self.send_json({"rooms": out})

    def api_qgroup_split(self, body):
        eid = str(body.get("event_id") or "").strip()
        if not eid:
            return self.send_json({"error": "缺少活动 id"}, 400)
        payload = qgroup_event_payload(eid)
        if payload.get("error"):
            return self.send_json({"error": payload["error"]}, payload.get("status", 400))
        qqs = payload.get("matched_qqs") or []
        if len(qqs) < 2:
            return self.send_json({"error": "可匹配的报名者不足 2 人：先在后台给群友填「看板 ID」，或报名者还没在本站登记"}, 400)
        mode = "capacity" if str(body.get("mode") or "") == "capacity" else "rooms"
        try:
            val = int(body.get("value"))
        except (TypeError, ValueError):
            val = None
        if mode == "capacity":
            res = room_split(qqs, capacity=val)
        else:
            res = room_split(qqs, rooms=val)
        if res.get("error"):
            return self.send_json({"error": res["error"]}, 400)
        rooms = [{
            "qqs": r.get("qqs") or [],
            "members": r.get("members", []),
            "avg": r.get("avg"), "min": r.get("min"),
            "worst": r.get("worst"), "common": (r.get("common") or [])[:4],
        } for r in res.get("rooms", [])]
        return self.send_json({"event_id": eid, "mode": mode, "rooms": rooms, "capacity": res.get("capacity")})

    def api_qgroup_rooms(self, body):
        rooms = body.get("rooms") or []
        if not isinstance(rooms, list):
            return self.send_json({"error": "房间格式不对"}, 400)
        members = data["members"]
        counts = entry_counts()
        out = []
        for qqs in rooms:
            if not isinstance(qqs, list):
                continue
            clean = [str(q).strip() for q in qqs]
            clean = [q for q in dict.fromkeys(clean) if q in members][:ROOM_MAX_PICKS]
            a = room_analysis(clean, counts)
            out.append({
                "qqs": clean,
                "members": [{"qq": q, "name": room_name(q)} for q in clean],
                "avg": a["avg"], "min": a["min"], "worst": a["worst"],
                "loner": a["loner"], "common": (a["common"] or [])[:4],
            })
        return self.send_json({"rooms": out})

    def api_shout(self, body):'''
if 'api_qgroup_split' not in s:
    assert anchor in s, 'methods anchor missing'
    s = s.replace(anchor, methods, 1)

# 5) module-level helpers before main()
helpers = '''QGROUP_BASE = os.environ.get("QGROUP_API_BASE", "https://kanban.danndann.cn/api/public/v1")
QGROUP_KEY_FILE = os.path.join(BASE, "private", "qgroup-api-key.txt")
_qgroup_cache = {}
_qgroup_lock = threading.Lock()


def qgroup_key():
    k = (os.environ.get("QGROUP_API_KEY") or "").strip()
    if k:
        return k
    try:
        with open(QGROUP_KEY_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def qgroup_request(path, params=None):
    key = qgroup_key()
    if not key:
        return {"error": "未配置看板 API 密钥", "status": 503}
    url = QGROUP_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key, "Accept": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", "replace") or "{}")
        except Exception:
            body = {}
        return {"error": body.get("error") or ("看板接口返回 %s" % e.code), "status": e.code}
    except Exception as e:
        return {"error": "看板接口连接失败：%s" % e, "status": 503}


def qgroup_events(limit=20, offset=0, lifecycle=""):
    cache_key = ("events", limit, offset, lifecycle)
    now = time.time()
    with _qgroup_lock:
        hit = _qgroup_cache.get(cache_key)
        if hit and now - hit["at"] < 60:
            return hit["data"]
    data = qgroup_request("/events", {"limit": limit, "offset": offset, "lifecycle": lifecycle})
    if not data.get("error"):
        with _qgroup_lock:
            _qgroup_cache[cache_key] = {"at": now, "data": data}
    return data


def board_member_map():
    out = {}
    for qq, m in (data.get("members") or {}).items():
        uid = str(m.get("boardUserId") or "").strip()
        if uid:
            out[uid] = qq
    return out


def board_member(qq):
    m = (data.get("members") or {}).get(qq) or {}
    return {
        "qq": qq,
        "name": m.get("name") or qq,
        "count": len(norm_selection(m.get("selection", []))) if m else 0,
    }


def qgroup_event_payload(event_id):
    d = qgroup_request("/events/" + urllib.parse.quote(event_id))
    if d.get("error"):
        return {"error": d["error"], "status": d.get("status", 400)}
    bmap = board_member_map()
    parts = d.get("participants") or []
    out_parts = []
    matched = []
    for p in parts:
        uid = str(p.get("user_id") or "")
        qq = bmap.get(uid) if uid else None
        mm = board_member(qq) if qq and qq in data["members"] else None
        if mm:
            matched.append(qq)
        out_parts.append({
            "attendee_id": p.get("attendee_id"),
            "user_id": uid or None,
            "name": p.get("name"),
            "status": p.get("status"),
            "confirmation_state": p.get("confirmation_state"),
            "qq": qq or "",
            "member_name": (mm or {}).get("name", ""),
            "count": (mm or {}).get("count", 0),
            "matched": bool(mm),
        })
    room_assign = d.get("room_assignments") or {}
    actual = room_assign.get("actual")
    planned = room_assign.get("planned")
    use = actual if actual is not None else planned
    rooms = []
    for r in (use or {}).get("rooms", []):
        qqs = []
        for mem in r.get("members") or []:
            uid = str(mem.get("user_id") or "")
            qq = bmap.get(uid) if uid else None
            if qq and qq in data["members"]:
                qqs.append(qq)
        qqs = list(dict.fromkeys(qqs))
        ana = room_analysis(qqs) if len(qqs) >= 2 else None
        rooms.append({
            "id": r.get("id"),
            "name": r.get("name") or "未命名",
            "members": [board_member(q) for q in qqs],
            "avg": (ana or {}).get("avg"),
            "min": (ana or {}).get("min"),
            "common": ((ana or {}).get("common") or [])[:4],
        })
    analysis = room_analysis(matched) if len(matched) >= 2 else None
    return {
        "api_version": d.get("api_version", 1),
        "event_id": d.get("event_id") or event_id,
        "revision": d.get("revision"),
        "event": d.get("event") or {},
        "participants": out_parts,
        "matched_qqs": matched,
        "rooms_source": ("actual" if actual is not None else ("planned" if planned is not None else "")),
        "rooms": rooms,
        "analysis": {k: analysis[k] for k in ("avg", "min", "worst", "loner", "common")} if analysis else None,
    }


def main():'''
if 'QGROUP_BASE' not in s:
    assert 'def main():' in s, 'main anchor missing'
    s = s.replace('def main():', helpers, 1)

open(p, 'w', encoding='utf-8').write(s)
print('patched ok')
