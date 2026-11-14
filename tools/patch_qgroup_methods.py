import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = os.path.join(BASE, 'server.py')
s = open(p, encoding='utf-8').read()

methods = '''    def api_qgroup_split(self, body):
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

'''

if 'def api_qgroup_split' not in s:
    anchor = '    def api_shout(self, body):'
    assert anchor in s, 'api_shout anchor missing'
    s = s.replace(anchor, methods + anchor, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('methods inserted')
else:
    print('methods already present')
