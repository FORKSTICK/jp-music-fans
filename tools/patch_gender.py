import os, re

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = os.path.join(BASE, 'server.py')
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert old in s, 'missing: ' + old[:70]
    s = s.replace(old, new, count)


# 1) load defaults
rep('''        m.setdefault("boardUserId", "")''',
    '''        m.setdefault("boardUserId", "")
        m.setdefault("gender", "")
        m.setdefault("genderPublic", False)''')

# 2) member_payload fields
rep('''        "note": str(m.get("note") or ""),
    }''',
    '''        "note": str(m.get("note") or ""),
        "gender": str(m.get("gender") or ""),
        "genderPublic": bool(m.get("genderPublic")),
    }''')

# 3) /api/members include public gender
rep('''                            "name": m.get("name") or qq,
                            "count": len(norm_selection(m.get("selection", []))),''',
    '''                            "name": m.get("name") or qq,
                            "count": len(norm_selection(m.get("selection", []))),
                            "gender": (str(m.get("gender") or "") if m.get("genderPublic") else ""),''')

# 4) compute_matches gender
rep('''                "qq": other["qq"],
                "name": other["name"],''',
    '''                "qq": other["qq"],
                "name": other["name"],
                "gender": (str(other.get("gender") or "") if other.get("genderPublic") else ""),''')

# 5) api_join new member defaults
rep('''                "createdAt": int(time.time()), "pinHash": hash_pin(pin), "lastJoinAt": int(time.time()),
                "boardUserId": "",''',
    '''                "createdAt": int(time.time()), "pinHash": hash_pin(pin), "lastJoinAt": int(time.time()),
                "boardUserId": "", "gender": "", "genderPublic": False,''')

# 6) room_split signature + gender preference
rep('''def room_split(qqs, rooms=None, capacity=None, counts=None):''',
    '''def room_split(qqs, rooms=None, capacity=None, counts=None, same_gender=False):''')

rep('''    total = {q: sum(sc(q, o) for o in qqs if o != q) for q in qqs}
    order = sorted(qqs, key=lambda q: (-total[q], q))
    groups = [[] for _ in range(room_n)]
    for i in range(room_n):
        groups[i].append(order.pop(0))''',
    '''    genders = {}
    if same_gender:
        for q in qqs:
            mm = members[q]
            g = str(mm.get("gender") or "")
            genders[q] = g if (mm.get("genderPublic") and g in ("female", "male")) else ""
    GENDER_BONUS = 200

    total = {q: sum(sc(q, o) for o in qqs if o != q) for q in qqs}
    order = sorted(qqs, key=lambda q: (-total[q], q))
    groups = [[] for _ in range(room_n)]
    seed_genders = set()
    for i in range(room_n):
        if same_gender and i > 0 and order:
            order.sort(key=lambda q: (genders.get(q, "") in seed_genders, -total[q], q))
        pick = order.pop(0)
        groups[i].append(pick)
        if same_gender and genders.get(pick):
            seed_genders.add(genders[pick])''')

rep('''            avg = sum(sc(q, o) for o in g) / len(g)
            key = (avg, -len(g))''',
    '''            avg = sum(sc(q, o) for o in g) / len(g)
            if same_gender and genders.get(q) and all(genders.get(o) == genders[q] for o in g):
                avg += GENDER_BONUS
            key = (avg, -len(g))''')

rep('''                base = sum(sc(q, o) for o in g if o != q) / max(1, len(g) - 1)''',
    '''                base = sum(sc(q, o) for o in g if o != q) / max(1, len(g) - 1)
                if same_gender and genders.get(q) and all(genders.get(o) == genders[q] for o in g if o != q):
                    base += GENDER_BONUS''')

rep('''                    cand = sum(sc(q, o) for o in g2) / len(g2)''',
    '''                    cand = sum(sc(q, o) for o in g2) / len(g2)
                    if same_gender and genders.get(q) and all(genders.get(o) == genders[q] for o in g2):
                        cand += GENDER_BONUS''')

# 7) pass same_gender from room split endpoint
rep('''        res = room_split(qqs, rooms=body.get("rooms"), capacity=body.get("capacity"))''',
    '''        res = room_split(qqs, rooms=body.get("rooms"), capacity=body.get("capacity"),
                         same_gender=bool(body.get("same_gender")))''')

# 8) qgroup split passes same_gender
rep('''        if mode == "capacity":
            res = room_split(qqs, capacity=val)
        else:
            res = room_split(qqs, rooms=val)''',
    '''        same_gender = bool(body.get("same_gender"))
        if mode == "capacity":
            res = room_split(qqs, capacity=val, same_gender=same_gender)
        else:
            res = room_split(qqs, rooms=val, same_gender=same_gender)''')

# 9) gender endpoint + route
if 'def api_gender' not in s:
    rep('''    def api_note(self, body):''',
        '''    def api_gender(self, body):
        qq = str(body.get("qq", "")).strip()
        m = data["members"].get(qq)
        if not m:
            return self.send_json({"error": "未注册"}, 401)
        gender = str(body.get("gender", "") or "").strip().lower()
        if gender not in ("", "female", "male"):
            return self.send_json({"error": "性别参数不对"}, 400)
        public = bool(body.get("genderPublic", False))
        with _lock:
            m["gender"] = gender
            m["genderPublic"] = bool(public and gender)
            save()
        return self.send_json({"ok": True, "gender": m["gender"], "genderPublic": m["genderPublic"]})

    def api_note(self, body):''')

    rep('''                "/api/note": self.api_note,''',
        '''                "/api/note": self.api_note,
                "/api/gender": self.api_gender,''')

open(p, 'w', encoding='utf-8').write(s)
print('server patched')
