import io, re

# ---------- index.html ----------
P = "public/index.html"
s = io.open(P, encoding="utf-8").read()

old_mode = '''              <button type="button" class="room-mode-btn" data-mode="capacity" aria-pressed="false">按人数</button>
            </div>
            <div class="room-split-row">
              <input type="number" id="eventValue" class="room-num" min="1" max="40" value="2" aria-label="房数或人数">
              <button type="button" id="eventSplit" class="primary">自动分房</button>
              <label class="room-same-gender" title="只对公开性别的人生效"><input type="checkbox" id="eventSameGender"> 同性别</label>
            </div>'''
new_mode = '''              <button type="button" class="room-mode-btn" data-mode="capacity" aria-pressed="false">按人数</button>
              <button type="button" class="room-mode-btn" data-mode="sizes" aria-pressed="false">自定义</button>
            </div>
            <div class="room-split-row">
              <input type="number" id="eventValue" class="room-num" min="1" max="40" value="2" aria-label="房数或人数">
              <input type="text" id="eventSizes" class="room-num room-num-wide" placeholder="8,8,6" aria-label="每间人数（逗号分隔）" hidden>
              <button type="button" id="eventSplit" class="primary">自动分房</button>
              <label class="room-same-gender" title="只对公开性别的人生效"><input type="checkbox" id="eventSameGender"> 同性别</label>
              <label class="room-same-gender" title="报名人数变化时自动重新分房"><input type="checkbox" id="eventAutoSplit" checked> 实时分房</label>
              <button type="button" id="eventShare" class="btn-ghost">分享图片</button>
            </div>
            <p id="eventShareHint" class="muted tiny"></p>
            <canvas id="eventShareCanvas" width="1080" height="1500" hidden></canvas>'''
assert old_mode in s
s = s.replace(old_mode, new_mode, 1)
io.open(P, "w", encoding="utf-8").write(s)
print("index ok")

# ---------- extra.css ----------
P = "public/extra.css"
s = io.open(P, encoding="utf-8").read()
s += """

/* v216 活动分房：自定义人数 / 手动调房 / 分享 */
.room-num-wide{ width:118px; }
.event-room.picking{ outline:2px dashed rgba(232,80,143,.55); outline-offset:2px; cursor:pointer; }
.event-mem{ cursor:pointer; border:0; }
.event-mem.on{ box-shadow:0 0 0 2px rgba(232,80,143,.55) inset; }
.event-room-meta{ margin-top:6px; }
html[data-theme="dark"] .event-room.picking{ outline-color:rgba(255,150,190,.55); }
"""
io.open(P, "w", encoding="utf-8").write(s)
print("css ok")

# ---------- app.js ----------
P = "public/app.js"
s = io.open(P, encoding="utf-8").read()

old_state = "  let eventMode = 'rooms';"
new_state = """  let eventMode = 'rooms';
  let eventRoomsState = [];
  let eventPick = null;
  let eventBusy = false;
  function eventParams() {
    const cap = $('eventValue') ? parseInt($('eventValue').value || '0', 10) : 0;
    let sizes = null;
    if ($('eventSizes') && $('eventSizes').value.trim()) {
      sizes = $('eventSizes').value.split(/[,，\\s]+/).map((x) => parseInt(x, 10)).filter((x) => x >= 1);
    }
    return { mode: eventMode, value: cap, sizes, same: !!($('eventSameGender') && $('eventSameGender').checked) };
  }
  function saveEventParams() {
    try { localStorage.setItem('jpm.eventParams', JSON.stringify(eventParams())); } catch (e) {}
  }
  function restoreEventParams() {
    try {
      const p = JSON.parse(localStorage.getItem('jpm.eventParams') || 'null');
      if (!p) return;
      setEventMode(p.mode || 'rooms', true);
      if ($('eventValue') && p.value) $('eventValue').value = p.value;
      if ($('eventSizes') && p.sizes && p.sizes.length) $('eventSizes').value = p.sizes.join(',');
      if ($('eventSameGender')) $('eventSameGender').checked = !!p.same;
    } catch (e) {}
  }"""
assert old_state in s
s = s.replace(old_state, new_state, 1)

# renderDetail 末尾：按实时分房自动执行
old_tail = '''    if ((p.rooms || []).length) renderRooms(p.rooms);
    else if ($('eventRooms')) $('eventRooms').innerHTML = '';
  }'''
new_tail = '''    if ((p.rooms || []).length) {
      eventRoomsState = p.rooms;
      renderRooms(p.rooms);
    } else if ($('eventRooms')) $('eventRooms').innerHTML = '';
    const auto = $('eventAutoSplit') && $('eventAutoSplit').checked;
    if (auto && matchedCount > 1) setTimeout(() => { doSplit(true); }, 300);
  }'''
assert old_tail in s
s = s.replace(old_tail, new_tail, 1)

# renderRooms：可点选成员、可点房调人、显示最高最低与成员分
old_render = '''  function renderRooms(rooms) {
    const box = $('eventRooms');
    if (!box) return;
    if (!rooms.length) { box.innerHTML = '<p class="muted tiny">还没有分房结果。</p>'; return; }
    box.innerHTML = rooms.map((r, i) => {
      const members = (r.members || []).map((m) => '<span class="event-badge off">' + escapeHtml(m.name || m.qq) + '</span>').join('');
      const common = (r.common || []).map((c) => escapeHtml(c.text)).join('、');
      return '<div class="event-room"><h4>包房 ' + (i + 1) + ' <span class="muted tiny">' + (r.members || []).length + ' 人</span></h4>'
        + '<div class="event-badges" style="margin:0 0 6px">' + members + '</div>'
        + '<div class="room-scoreline">平均 ' + (r.avg == null ? '—' : r.avg) + ' · 最低 ' + (r.min == null ? '—' : r.min) + '</div>'
        + (common ? '<div class="room-scoreline">共同：' + common + '</div>' : '')
        + '</div>';
    }).join('');
  }'''
new_render = '''  function renderRooms(rooms) {
    const box = $('eventRooms');
    if (!box) return;
    eventRoomsState = rooms || [];
    if (!rooms.length) { box.innerHTML = '<p class="muted tiny">还没有分房结果。</p>'; return; }
    box.innerHTML = rooms.map((r, i) => {
      const members = (r.members || []).map((m) => {
        const on = eventPick && String(eventPick) === String(m.qq);
        return '<button type="button" class="event-badge off event-mem' + (on ? ' on' : '') + '" data-qq="' + escapeHtml(m.qq) + '">'
          + escapeHtml(m.name || m.qq)
          + (m.avg == null ? '' : ' <b style="font-weight:800">' + m.avg + '</b>')
          + '</button>';
      }).join('');
      const common = (r.common || []).map((c) => escapeHtml(c.text)).join('、');
      return '<div class="event-room" data-room="' + i + '"><h4>包房 ' + (i + 1) + ' <span class="muted tiny">' + (r.members || []).length + ' 人</span></h4>'
        + '<div class="event-badges" style="margin:0 0 6px">' + members + '</div>'
        + '<div class="room-scoreline event-room-meta">平均 ' + (r.avg == null ? '—' : r.avg)
        + ' · 最高 ' + (r.memberMax == null ? '—' : r.memberMax)
        + ' · 最低 ' + (r.memberMin == null ? '—' : r.memberMin) + '</div>'
        + (common ? '<div class="room-scoreline">共同：' + common + '</div>' : '')
        + '</div>';
    }).join('');
  }

  function eventRoomsPayload() {
    return eventRoomsState.map((r) => (r.members || []).map((m) => m.qq));
  }

  async function eventRecalc() {
    if (!eventRoomsState.length) return;
    try {
      const res = await jpost('/api/qgroup/rooms', { rooms: eventRoomsPayload() });
      eventRoomsState = res.rooms || [];
      renderRooms(eventRoomsState);
    } catch (e) {
      if ($('eventSplitHint')) $('eventSplitHint').textContent = e.message || '重算失败';
    }
  }

  async function eventMove(qq, target) {
    if (!qq) return;
    const rooms = eventRoomsPayload();
    let from = -1, to = -1;
    rooms.forEach((arr, i) => { if (arr.includes(qq)) from = i; });
    if (target === 'new') {
      rooms.push([qq]);
    } else {
      to = Number(target);
      if (to === from) return;
      rooms[to] = (rooms[to] || []).concat([qq]);
    }
    if (from >= 0) rooms[from] = rooms[from].filter((x) => x !== qq);
    const cleaned = rooms.filter((arr) => arr.length);
    eventPick = null;
    eventRoomsState = cleaned.map((arr) => ({ members: arr.map((q) => ({ qq: q, name: (window.__eventNames || {})[q] || q })) }));
    renderRooms(eventRoomsState);
    await eventRecalc();
  }'''
assert old_render in s
s = s.replace(old_render, new_render, 1)

# doSplit：支持 sizes + 自动模式 + 记忆参数
old_split = '''  async function doSplit() {
    if (!currentId) return;
    const hint = $('eventSplitHint');
    const val = parseInt(($('eventValue') && $('eventValue').value) || '0', 10);
    if (!val || val < 1) { if (hint) hint.textContent = eventMode === 'capacity' ? '先填每房几个人' : '先填要分几间房'; return; }
    try {
      if (hint) hint.textContent = '分房中…';
      const res = await jpost('/api/qgroup/split', { event_id: currentId, mode: eventMode, value: val, same_gender: !!($('eventSameGender') && $('eventSameGender').checked) });
      renderRooms(res.rooms || []);
      if (hint) hint.textContent = '已按' + (eventMode === 'capacity' ? '每房 ' + val + ' 人' : val + ' 间房') + '分好。';
    } catch (e) {
      if (hint) hint.textContent = e.message || '分房失败';
    }
  }'''
new_split = '''  async function doSplit(auto) {
    if (!currentId || eventBusy) return;
    const hint = $('eventSplitHint');
    const p = eventParams();
    if (p.mode === 'sizes') {
      if (!p.sizes || p.sizes.length < 2) { if (hint && !auto) hint.textContent = '先填每间人数，用逗号分隔（例如 8,8,6）'; return; }
    } else if (!p.value || p.value < 1) {
      if (hint && !auto) hint.textContent = p.mode === 'capacity' ? '先填每房几个人' : '先填要分几间房';
      return;
    }
    try {
      eventBusy = true;
      if (hint) hint.textContent = '分房中…';
      const body = { event_id: currentId, same_gender: p.same };
      if (p.mode === 'sizes') body.sizes = p.sizes;
      else { body.mode = p.mode; body.value = p.value; }
      const res = await jpost('/api/qgroup/split', body);
      eventRoomsState = res.rooms || [];
      renderRooms(eventRoomsState);
      saveEventParams();
      if (hint) {
        const how = p.mode === 'sizes' ? '自定义人数 ' + p.sizes.join('/') : (p.mode === 'capacity' ? '每房 ' + p.value + ' 人' : p.value + ' 间房');
        hint.textContent = '已按' + how + '分好' + (auto ? '（报名变化时自动重分）' : '') + '。';
      }
    } catch (e) {
      if (hint) hint.textContent = e.message || '分房失败';
    } finally {
      eventBusy = false;
    }
  }'''
assert old_split in s
s = s.replace(old_split, new_split, 1)

# setEventMode：支持 sizes，切换输入框
old_mode_fn = '''  function setEventMode(mode) {
    eventMode = mode === 'capacity' ? 'capacity' : 'rooms';
    document.querySelectorAll('#eventMode .room-mode-btn').forEach((btn) => {
      const on = btn.dataset.mode === eventMode;
      btn.classList.toggle('on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if ($('eventValue')) $('eventValue').value = eventMode === 'capacity' ? '4' : '2';
  }'''
new_mode_fn = '''  function setEventMode(mode, silent) {
    eventMode = mode === 'capacity' ? 'capacity' : (mode === 'sizes' ? 'sizes' : 'rooms');
    document.querySelectorAll('#eventMode .room-mode-btn').forEach((btn) => {
      const on = btn.dataset.mode === eventMode;
      btn.classList.toggle('on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if ($('eventValue')) {
      $('eventValue').hidden = eventMode === 'sizes';
      if (!silent) $('eventValue').value = eventMode === 'capacity' ? '4' : '2';
    }
    if ($('eventSizes')) $('eventSizes').hidden = eventMode !== 'sizes';
  }'''
assert old_mode_fn in s
s = s.replace(old_mode_fn, new_mode_fn, 1)

# 事件绑定：点击房/成员/实时分房/分享
old_bind = '''  if ($('eventSplit')) $('eventSplit').addEventListener('click', doSplit);
  if ($('eventMode')) $('eventMode').addEventListener('click', (e) => { const btn = e.target.closest('.room-mode-btn'); if (btn) setEventMode(btn.dataset.mode); });'''
new_bind = '''  if ($('eventSplit')) $('eventSplit').addEventListener('click', () => doSplit(false));
  if ($('eventMode')) $('eventMode').addEventListener('click', (e) => { const btn = e.target.closest('.room-mode-btn'); if (btn) setEventMode(btn.dataset.mode); });
  if ($('eventRooms')) {
    $('eventRooms').addEventListener('click', (e) => {
      const mem = e.target.closest('.event-mem');
      if (mem) {
        eventPick = (eventPick && String(eventPick) === String(mem.dataset.qq)) ? null : mem.dataset.qq;
        renderRooms(eventRoomsState);
        return;
      }
      const room = e.target.closest('.event-room');
      if (room && eventPick) {
        eventMove(eventPick, room.dataset.room);
      }
    });
  }
  if ($('eventShare')) $('eventShare').addEventListener('click', eventShareImage);'''
assert old_bind in s
s = s.replace(old_bind, new_bind, 1)

io.open(P, "w", encoding="utf-8").write(s)
print("app.js ok")
