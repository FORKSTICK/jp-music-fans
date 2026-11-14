# -*- coding: utf-8 -*-
import io, re

def rd(p):
    return io.open(p, encoding='utf-8').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)

# ---------- server.py: fix over-escaped regex ----------
p = 'server.py'
s = rd(p)
s = s.replace('re.sub(r"\\\\s+", " ", str(body.get("genderCustom"', 're.sub(r"\\s+", " ", str(body.get("genderCustom"')
s = s.replace('re.search(r"[\\\\x00-\\\\x1f\\\\x7f<>]", gender)', 're.search(r"[\\x00-\\x1f\\x7f<>]", gender)')
wr(p, s)
print('server escapes ok')

# ---------- index.html ----------
p = 'public/index.html'
s = rd(p)
if '只对和你相似度前三的群友可见' in s:
    s = s.replace('只对和你相似度前三的群友可见', '只对和你最像的那位群友可见', 1)
s = s.replace('<span class="tab-txt">已选</span>', '<span class="tab-txt">成分栏</span>', 1)

old = '''        <label class="gender-opt"><input type="radio" name="genderPick" value="male"> 男</label>
      </div>'''
new = '''        <label class="gender-opt"><input type="radio" name="genderPick" value="male"> 男</label>
        <label class="gender-opt"><input type="radio" name="genderPick" value="custom"> 自定义</label>
      </div>
      <div class="row gender-custom-row">
        <input type="text" id="genderCustom" class="gender-custom" maxlength="12" placeholder="写你希望的称呼（最多 12 字）" hidden>
      </div>'''
if old in s:
    s = s.replace(old, new, 1)

def sw(mid, text, title):
    return ('<label class="room-same-gender" title="%s"><input type="checkbox" id="%s">'
            '<span class="rm-switch" aria-hidden="true"><span class="rm-knob"></span></span>'
            '<span class="rm-text">%s</span></label>') % (title, mid, text)

for mid, text, title in [
    ('roomSameGender', '同性别', '只对公开性别的人生效'),
    ('eventSameGender', '同性别', '只对公开性别的人生效'),
    ('eventAutoSplit', '实时分房', '报名人数变化时自动重新分房'),
]:
    pat = re.compile(r'<label class="room-same-gender" title="[^"]*"><input type="checkbox" id="%s"[^>]*>\s*%s</label>' % (mid, text))
    s2, n = pat.subn(sw(mid, text, title), s, count=1)
    assert n == 1, mid
    s = s2
wr(p, s)
print('index ok')

# ---------- extra.css ----------
p = 'public/extra.css'
s = rd(p)
old_start = '.room-same-gender{ display:inline-flex; align-items:center; gap:6px; height:34px;'
i = s.find(old_start)
if i >= 0:
    j = s.find('html[data-theme="dark"] .room-same-gender:has(input:checked){', i)
    j = s.find('}', j) + 1
    new_css = '''.room-same-gender{ display:inline-flex; align-items:center; gap:8px; height:30px; padding:0 12px; border-radius:999px;
  background:rgba(255,255,255,.6); border:1px solid rgba(214,182,206,.55); font-size:12px; font-weight:700; color:#6b5b77; cursor:pointer; user-select:none; }
.room-same-gender:hover{ border-color:rgba(232,80,143,.45); }
.room-same-gender input{ position:absolute; width:1px; height:1px; opacity:0; margin:0; pointer-events:none; }
.room-same-gender input:checked + .rm-switch{ background:linear-gradient(135deg,#ff7ab0,#c48bff); }
.room-same-gender input:checked + .rm-switch .rm-knob{ transform:translateX(14px); }
.room-same-gender input:focus-visible + .rm-switch{ box-shadow:0 0 0 3px rgba(232,80,143,.3); }
.room-same-gender:has(input:checked){ background:rgba(255,233,243,.9); border-color:rgba(232,80,143,.5); color:#b0315f; }
html[data-theme="dark"] .room-same-gender{ background:rgba(38,30,48,.62); border-color:rgba(120,96,140,.5); color:#c3b9d2; }
html[data-theme="dark"] .room-same-gender:has(input:checked){ background:rgba(70,32,54,.9); border-color:rgba(255,140,190,.5); color:#ffc2d8; }
.gender-custom{ height:34px; min-width:220px; padding:0 12px; border-radius:999px; border:1px solid rgba(214,182,206,.6);
  background:rgba(255,255,255,.72); font-size:13px; color:#3c3247; }
html[data-theme="dark"] .gender-custom{ background:rgba(42,32,52,.72); border-color:rgba(120,96,140,.55); color:#f2eef8; }
.gender-custom-row{ margin:8px 0 2px; }'''
    s = s[:i] + new_css + s[j:]
wr(p, s)
print('css ok')

# ---------- app.js ----------
p = 'public/app.js'
s = rd(p)
old_tag = """        gt.className = 'gender-tag ' + m.gender;
        gt.textContent = m.gender === 'female' ? '女' : '男';"""
new_tag = """        gt.className = 'gender-tag ' + (m.gender === 'female' || m.gender === 'male' ? m.gender : 'custom');
        gt.textContent = m.gender === 'female' ? '女' : (m.gender === 'male' ? '男' : m.gender);"""
if s.count(old_tag) == 2:
    s = s.replace(old_tag, new_tag)

old_modal = "$('memberModalSub').textContent = 'QQ ' + match.qq + (match.gender ? ' · ' + (match.gender === 'female' ? '女' : '男') : '');"
new_modal = "$('memberModalSub').textContent = 'QQ ' + match.qq + (match.gender ? ' · ' + (match.gender === 'female' ? '女' : (match.gender === 'male' ? '男' : match.gender)) : '');"
if old_modal in s:
    s = s.replace(old_modal, new_modal, 1)

old_paint = """  function paintGender(m) {
    const gender = (m && m.gender) || '';
    document.querySelectorAll('input[name="genderPick"]').forEach((r) => { r.checked = (r.value || '') === gender; });"""
if old_paint in s:
    new_paint = """  function genderText(g) {
    if (!g) return '';
    if (g === 'female') return '女';
    if (g === 'male') return '男';
    return g;
  }

  function paintGender(m) {
    const gender = (m && m.gender) || '';
    const custom = gender && gender !== 'female' && gender !== 'male';
    const pick = gender === 'female' || gender === 'male' ? gender : (custom ? 'custom' : '');
    document.querySelectorAll('input[name="genderPick"]').forEach((r) => { r.checked = (r.value || '') === pick; });
    if (gEl('genderCustom')) {
      gEl('genderCustom').value = custom ? gender : '';
      gEl('genderCustom').hidden = pick !== 'custom';
    }"""
    s = s.replace(old_paint, new_paint, 1)
    s = s.replace("""        ? '当前：' + (gender === 'female' ? '女' : '男') + (m && m.genderPublic ? '（已公开）' : '（仅自己可见）')""",
                  """        ? '当前：' + genderText(gender) + (m && m.genderPublic ? '（已公开）' : '（仅自己可见）')""", 1)

old_save = """    let gender = '';
    document.querySelectorAll('input[name="genderPick"]').forEach((r) => { if (r.checked) gender = r.value; });
    const pub = !!(gEl('genderPublic') && gEl('genderPublic').checked) && !!gender;
    try {
      await gpost('/api/gender', { qq: me, gender, genderPublic: pub });"""
if old_save in s:
    new_save = """    let pick = '';
    document.querySelectorAll('input[name="genderPick"]').forEach((r) => { if (r.checked) pick = r.value; });
    const customText = (gEl('genderCustom') && gEl('genderCustom').value || '').trim().slice(0, 12);
    if (pick === 'custom' && !customText) { gToast('先写一个自定义性别名称', 'err'); return; }
    const gender = pick === 'custom' ? customText : pick;
    const pub = !!(gEl('genderPublic') && gEl('genderPublic').checked) && !!gender;
    try {
      await gpost('/api/gender', { qq: me, gender: pick === 'custom' ? 'custom' : gender, genderCustom: customText, genderPublic: pub });"""
    s = s.replace(old_save, new_save, 1)
wr(p, s)
print('app ok')
