import io, re, sys

P = "server.py"
s = io.open(P, encoding="utf-8").read()

# ---------- 1) room_analysis: 每人综合分 + 房间成员最高/最低 ----------
old_members = '''    return {
        "members": [{"qq": q, "name": names[q], "count": len(sels[q])} for q in qqs],'''
new_members = '''    def _mavg(q):
        arr = per.get(q) or []
        if not arr:
            return 100 if len(qqs) == 1 else 0
        return int(round(sum(arr) / len(arr)))

    mem = [{"qq": q, "name": names[q], "count": len(sels[q]), "avg": _mavg(q)} for q in qqs]
    mavgs = [m["avg"] for m in mem] or [0]
    return {
        "members": mem,
        "memberMax": max(mavgs),
        "memberMin": min(mavgs),'''
assert old_members in s
s = s.replace(old_members, new_members, 1)

# ---------- 2) room_split: sizes 参数 ----------
old_sig = 'def room_split(qqs, rooms=None, capacity=None, counts=None, same_gender=False):'
new_sig = 'def room_split(qqs, rooms=None, capacity=None, counts=None, same_gender=False, sizes=None):'
assert old_sig in s
s = s.replace(old_sig, new_sig, 1)

old_mode = '''    if capacity:
        capacity = max(2, capacity)
        room_n = max(2, (n + capacity - 1) // capacity)
    elif rooms:'''
new_mode = '''    size_list = []
    if isinstance(sizes, list) and sizes:
        for x in sizes:
            try:
                v = int(x)
            except (TypeError, ValueError):
                continue
            if v >= 1:
                size_list.append(v)
        size_list = size_list[:40]
        if len(size_list) < 2:
            return {"error": "自定义人数至少需要 2 间房"}
        if sum(size_list) < n:
            return {"error": "自定义人数总和小于参与人数（%d 人）" % n}
        capacity = max(size_list)
        room_n = len(size_list)
        size_list = size_list[:room_n]
    elif capacity:
        capacity = max(2, capacity)
        room_n = max(2, (n + capacity - 1) // capacity)
    elif rooms:'''
assert old_mode in s
s = s.replace(old_mode, new_mode, 1)

# 贪心分配：优先按 size_list 的空位
old_greedy = '''        for gi, g in enumerate(groups):
            if len(g) >= capacity:
                continue'''
new_greedy = '''        for gi, g in enumerate(groups):
            cap_i = size_list[gi] if size_list else capacity
            if len(g) >= cap_i:
                continue'''
assert old_greedy in s
s = s.replace(old_greedy, new_greedy, 1)

# 局部调整：同样按各房上限
old_move = '''                for gj, g2 in enumerate(groups):
                    if gj == gi or not g2 or len(g2) >= capacity:
                        continue'''
new_move = '''                for gj, g2 in enumerate(groups):
                    cap_j = size_list[gj] if size_list else capacity
                    if gj == gi or not g2 or len(g2) >= cap_j:
                        continue'''
assert old_move in s
s = s.replace(old_move, new_move, 1)

# 输出补 members 的 avg / memberMax / memberMin
old_out = '''    out = []
    for g in groups:
        if len(g) > 1:
            a = room_analysis(g, counts)
        else:
            a = {"avg": 0, "min": 0, "worst": None, "common": []}
        out.append({
            "members": [{"qq": q, "name": names[q], "count": len(sels[q])} for q in g],
            "avg": a.get("avg", 0),'''
new_out = '''    out = []
    for g in groups:
        a = room_analysis(g, counts)
        out.append({
            "members": a.get("members") or [{"qq": q, "name": names[q], "count": len(sels[q])} for q in g],
            "memberMax": a.get("memberMax", 0),
            "memberMin": a.get("memberMin", 0),
            "avg": a.get("avg", 0),'''
assert old_out in s
s = s.replace(old_out, new_out, 1)

# 尾部返回补 sizes
old_ret = '    return {"rooms": out, "capacity": capacity, "roomCount": room_n}'
new_ret = '    return {"rooms": out, "capacity": capacity, "roomCount": room_n, "sizes": (size_list or None)}'
assert old_ret in s
s = s.replace(old_ret, new_ret, 1)

# ---------- 3) 两个 API 透传 sizes ----------
old_q = '''        same_gender = bool(body.get("same_gender"))
        if mode == "capacity":
            res = room_split(qqs, capacity=val, same_gender=same_gender)
        else:
            res = room_split(qqs, rooms=val, same_gender=same_gender)'''
new_q = '''        same_gender = bool(body.get("same_gender"))
        sizes = body.get("sizes")
        if isinstance(sizes, list) and sizes:
            res = room_split(qqs, sizes=sizes, same_gender=same_gender)
        elif mode == "capacity":
            res = room_split(qqs, capacity=val, same_gender=same_gender)
        else:
            res = room_split(qqs, rooms=val, same_gender=same_gender)'''
assert old_q in s
s = s.replace(old_q, new_q, 1)

# 房间输出统一带成员分与最高/最低（qgroup split / rooms / recalc）
old_room_out = '''        rooms = [{
            "qqs": r.get("qqs") or [],
            "members": r.get("members", []),
            "avg": r.get("avg"), "min": r.get("min"),
            "worst": r.get("worst"), "common": (r.get("common") or [])[:4],
        } for r in res.get("rooms", [])]'''
new_room_out = '''        rooms = [{
            "qqs": r.get("qqs") or [],
            "members": r.get("members", []),
            "avg": r.get("avg"), "min": r.get("min"),
            "memberMax": r.get("memberMax"), "memberMin": r.get("memberMin"),
            "worst": r.get("worst"), "common": (r.get("common") or [])[:4],
        } for r in res.get("rooms", [])]'''
assert old_room_out in s
s = s.replace(old_room_out, new_room_out, 1)

# api_qgroup_split 的 rooms 里 r 没有 qqs —— room_split 输出的房间不含 qqs，补上
old_r_fill = '''            "members": a.get("members") or [{"qq": q, "name": names[q], "count": len(sels[q])} for q in g],'''
new_r_fill = '''            "qqs": g,
            "members": a.get("members") or [{"qq": q, "name": names[q], "count": len(sels[q])} for q in g],'''
assert old_r_fill in s
s = s.replace(old_r_fill, new_r_fill, 1)

# ---------- 4) recalc / rooms 接口带成员分 ----------
for fn_old, fn_new in [
    ('''                "members": [{"qq": q, "name": room_name(q)} for q in clean],''',
     '''                "members": a.get("members") or [{"qq": q, "name": room_name(q)} for q in clean],'''),
]:
    s = s.replace(fn_old, fn_new)

s = s.replace('''                "avg": a["avg"], "min": a["min"], "worst": a["worst"],
                "loner": a["loner"], "common": a["common"],''',
              '''                "avg": a["avg"], "min": a["min"], "worst": a["worst"],
                "memberMax": a.get("memberMax"), "memberMin": a.get("memberMin"),
                "loner": a["loner"], "common": a["common"],''')
s = s.replace('''                "avg": a["avg"], "min": a["min"], "worst": a["worst"],
                "loner": a["loner"], "common": (a["common"] or [])[:4],''',
              '''                "avg": a["avg"], "min": a["min"], "worst": a["worst"],
                "memberMax": a.get("memberMax"), "memberMin": a.get("memberMin"),
                "loner": a["loner"], "common": (a["common"] or [])[:4],''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched room sizes + member scores")
