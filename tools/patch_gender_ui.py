import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
s = open(os.path.join(BASE, 'public', 'index.html'), encoding='utf-8').read(start := 0) if False else open(os.path.join(BASE, 'public', 'index.html'), encoding='utf-8').read()


def rep(old, new):
    global s
    assert old in s, 'html missing: ' + old[:60]
    s = s.replace(old, new, 1)


gender_card = '''    <section class="card" id="genderCard" hidden>
      <div class="board-head">
        <h2>性别（可选）</h2>
        <span class="muted tiny">注册时不填，这里随时可以改</span>
      </div>
      <p class="muted tiny">公开后：匹配卡会显示你的性别，分房时也能按同性别优先分组。不公开就只有你自己能看到。</p>
      <div class="gender-row">
        <label class="gender-opt"><input type="radio" name="genderPick" value=""> 保密</label>
        <label class="gender-opt"><input type="radio" name="genderPick" value="female"> 女</label>
        <label class="gender-opt"><input type="radio" name="genderPick" value="male"> 男</label>
      </div>
      <label class="gender-public"><input type="checkbox" id="genderPublic"> 公开性别（用于匹配显示与同性别分房）</label>
      <div class="row">
        <button type="button" id="genderSave" class="btn-ghost">保存性别设置</button>
        <span id="genderHint" class="muted tiny"></span>
      </div>
    </section>
'''

anchor = '''    </section>
    </div>

    <div class="page" id="page-matches" data-page="matches">'''
rep(anchor, '    </section>\n' + gender_card + '    </div>\n\n    <div class="page" id="page-matches" data-page="matches">')

# room split row checkbox
rep('''        <span class="room-split-label">自动分房</span>''',
    '''        <span class="room-split-label">自动分房</span>
        <label class="room-same-gender" title="只对公开性别的人生效"><input type="checkbox" id="roomSameGender"> 同性别</label>''')

# event split row checkbox
rep('''              <button type="button" id="eventSplit" class="primary">自动分房</button>''',
    '''              <button type="button" id="eventSplit" class="primary">自动分房</button>
              <label class="room-same-gender" title="只对公开性别的人生效"><input type="checkbox" id="eventSameGender"> 同性别</label>''')

open(os.path.join(BASE, 'public', 'index.html'), 'w', encoding='utf-8').write(s)
print('index patched')

# ---------- app.js ----------
p = os.path.join(BASE, 'public', 'app.js')
a = open(p, encoding='utf-8').read()


def arep(old, new):
    global a
    assert old in a, 'js missing: ' + old[:60]
    a = a.replace(old, new, 1)


arep('''      name.className = 'match-name';
      name.textContent = m.name;''',
     '''      name.className = 'match-name';
      name.textContent = m.name;
      if (m.gender) {
        const gt = document.createElement('span');
        gt.className = 'gender-tag ' + m.gender;
        gt.textContent = m.gender === 'female' ? '女' : '男';
        gt.title = 'TA 公开的性别';
        name.appendChild(gt);
      }''')

arep('''        nm.className = 'match-name';
        nm.textContent = m.name;''',
     '''        nm.className = 'match-name';
        nm.textContent = m.name;
        if (m.gender) {
          const gt = document.createElement('span');
          gt.className = 'gender-tag ' + m.gender;
          gt.textContent = m.gender === 'female' ? '女' : '男';
          nm.appendChild(gt);
        }''')

arep("""    $('memberModalSub').textContent = 'QQ ' + match.qq;""",
     """    $('memberModalSub').textContent = 'QQ ' + match.qq + (match.gender ? ' · ' + (match.gender === 'female' ? '女' : '男') : '');""")

arep("""      const d = await postJSON('/api/room/split', Object.assign({ qqs: [...picked.keys()] }, isRoomCount ? { rooms: value } : { capacity: value }));""",
     """      const sameGender = !!($('roomSameGender') && $('roomSameGender').checked);
      const d = await postJSON('/api/room/split', Object.assign({ qqs: [...picked.keys()], same_gender: sameGender }, isRoomCount ? { rooms: value } : { capacity: value }));""")

arep("""      const res = await jpost('/api/qgroup/split', { event_id: currentId, mode: eventMode, value: val });""",
     """      const res = await jpost('/api/qgroup/split', { event_id: currentId, mode: eventMode, value: val, same_gender: !!($('eventSameGender') && $('eventSameGender').checked) });""")

gender_js = '''
/* 性别设置（可选，注册时不填；仅本人可改） */
(() => {
  function gMe() {
    try {
      const id = (typeof identity !== 'undefined' && identity) || JSON.parse(localStorage.getItem('jpm.identity') || 'null');
      return (id && id.qq) || '';
    } catch (e) { return ''; }
  }

  function paintGender(m) {
    const gender = (m && m.gender) || '';
    document.querySelectorAll('input[name="genderPick"]').forEach((r) => { r.checked = (r.value || '') === gender; });
    if ($('genderPublic')) {
      $('genderPublic').checked = !!(m && m.genderPublic);
      $('genderPublic').disabled = !gender;
    }
    if ($('genderHint')) {
      $('genderHint').textContent = gender
        ? '当前：' + (gender === 'female' ? '女' : '男') + (m && m.genderPublic ? '（已公开）' : '（仅自己可见）')
        : '还没有设置，可以不填';
    }
  }

  async function loadGender() {
    const card = $('genderCard');
    if (!card) return;
    const me = gMe();
    if (!me) { card.hidden = true; return; }
    card.hidden = false;
    try {
      const d = await jget('/api/me?qq=' + encodeURIComponent(me));
      paintGender((d && d.member) || {});
    } catch (e) { /* 静默 */ }
  }

  async function saveGender() {
    const me = gMe();
    if (!me) return;
    let gender = '';
    document.querySelectorAll('input[name="genderPick"]').forEach((r) => { if (r.checked) gender = r.value; });
    const pub = !!($('genderPublic') && $('genderPublic').checked) && !!gender;
    try {
      await apiPost('/api/gender', { qq: me, gender, genderPublic: pub });
      toast(gender ? '性别设置已保存' : '已设为保密', 'ok');
      paintGender({ gender, genderPublic: pub });
      if (pub) toast('已公开：匹配卡会显示性别，分房可按同性别优先', 'ok');
      if (window.__genderChanged) window.__genderChanged();
    } catch (e) {
      toast(e.message || '保存失败', 'err');
    }
  }

  if ($('genderSave')) $('genderSave').addEventListener('click', saveGender);
  document.querySelectorAll('input[name="genderPick"]').forEach((r) => {
    r.addEventListener('change', () => {
      if ($('genderPublic')) $('genderPublic').disabled = !r.value;
    });
  });
  if ($('genderPublic')) {
    $('genderPublic').addEventListener('change', (e) => {
      if (e.target.checked) toast('记得点「保存性别设置」', 'ok');
    });
  }
  document.addEventListener('click', (e) => {
    const tab = e.target && e.target.closest ? e.target.closest('#tabBar .tab[data-page="mine"]') : null;
    if (tab) setTimeout(loadGender, 350);
  }, true);
  setTimeout(loadGender, 2600);
  window.__loadGender = loadGender;
})();
'''
a = a.rstrip() + '\n' + gender_js
open(p, 'w', encoding='utf-8').write(a)
print('app patched')

# ---------- extra.css ----------
cp = os.path.join(BASE, 'public', 'extra.css')
c = open(cp, encoding='utf-8').read()
c += '''
/* v213 性别（可选、仅本人设置） */
.gender-row{ display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 8px; }
.gender-opt{ display:inline-flex; align-items:center; gap:6px; height:32px; padding:0 12px; border-radius:999px;
  background:rgba(255,255,255,.62); border:1px solid rgba(214,182,206,.55); font-size:13px; font-weight:600; cursor:pointer; }
.gender-opt:has(input:checked){ background:rgba(255,233,243,.9); border-color:rgba(232,80,143,.55); color:#b0315f; }
html[data-theme="dark"] .gender-opt{ background:rgba(38,30,48,.62); border-color:rgba(120,96,140,.5); }
html[data-theme="dark"] .gender-opt:has(input:checked){ background:rgba(70,32,54,.9); border-color:rgba(255,140,190,.5); color:#ffc2d8; }
.gender-public{ display:inline-flex; align-items:center; gap:7px; font-size:12.5px; color:#5a5267; cursor:pointer; }
html[data-theme="dark"] .gender-public{ color:#c3b9d2; }
.gender-tag{ display:inline-flex; align-items:center; justify-content:center; min-width:18px; height:17px;
  margin-left:6px; padding:0 5px; border-radius:999px; font-size:10.5px; font-weight:700; vertical-align:middle;
  background:rgba(255,150,196,.22); color:#b0315f; border:1px solid rgba(232,80,143,.35); }
.gender-tag.male{ background:rgba(130,170,255,.2); color:#33518f; border-color:rgba(90,130,220,.35); }
html[data-theme="dark"] .gender-tag{ background:rgba(255,120,180,.2); color:#ffc2d8; }
html[data-theme="dark"] .gender-tag.male{ background:rgba(110,150,255,.22); color:#c3d6ff; }
.room-same-gender{ display:inline-flex; align-items:center; gap:6px; height:34px; padding:0 10px; border-radius:999px;
  background:rgba(255,255,255,.6); border:1px solid rgba(214,182,206,.55); font-size:12px; font-weight:600; color:#6b5b77; cursor:pointer; }
.room-same-gender:has(input:checked){ background:rgba(255,233,243,.9); border-color:rgba(232,80,143,.5); color:#b0315f; }
html[data-theme="dark"] .room-same-gender{ background:rgba(38,30,48,.62); border-color:rgba(120,96,140,.5); color:#c3b9d2; }
html[data-theme="dark"] .room-same-gender:has(input:checked){ background:rgba(70,32,54,.9); border-color:rgba(255,140,190,.5); color:#ffc2d8; }
'''
open(cp, 'w', encoding='utf-8').write(c)
print('css patched')
