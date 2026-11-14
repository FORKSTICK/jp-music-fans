import io, os

BASE = os.path.dirname(os.path.abspath(__file__)) + os.sep + '..'
BASE = os.path.normpath(BASE)

# ---------- index.html ----------
p = os.path.join(BASE, 'public', 'index.html')
s = open(p, encoding='utf-8').read()

page_html = '''    <div class="page" id="page-event" data-page="event">
      <section class="card" id="eventListCard">
        <h2>群聚活动</h2>
        <p class="muted tiny">数据来自「群聚看板」公开接口；报名截止后可一键按成分分房。</p>
        <div class="event-toolbar">
          <select id="eventLifecycle" aria-label="筛选活动状态">
            <option value="">全部活动</option>
            <option value="scheduled">未开始</option>
            <option value="ongoing">进行中</option>
            <option value="ended">已结束</option>
          </select>
          <button type="button" id="eventRefresh" class="btn-ghost">刷新</button>
        </div>
        <p id="eventError" class="error" hidden></p>
        <div id="eventList" class="event-list"></div>
        <p id="eventEmpty" class="muted tiny" hidden>还没有活动。</p>
      </section>
      <section class="card" id="eventDetailCard" hidden>
        <div class="event-detail-head">
          <h2 id="eventTitle">活动</h2>
          <button type="button" id="eventBack" class="btn-ghost">返回列表</button>
        </div>
        <p id="eventMeta" class="muted tiny"></p>
        <div id="eventBadges" class="event-badges"></div>
        <div class="event-grid">
          <div>
            <h3 class="event-sub">报名名单 <span id="eventPartCount" class="muted tiny"></span></h3>
            <ul id="eventParticipants" class="event-parts"></ul>
          </div>
          <div>
            <h3 class="event-sub">分房</h3>
            <div class="room-mode" id="eventMode">
              <button type="button" class="room-mode-btn on" data-mode="rooms" aria-pressed="true">按房数</button>
              <button type="button" class="room-mode-btn" data-mode="capacity" aria-pressed="false">按人数</button>
            </div>
            <div class="room-split-row">
              <input type="number" id="eventValue" class="room-num" min="1" max="40" value="2" aria-label="房数或人数">
              <button type="button" id="eventSplit" class="primary">自动分房</button>
            </div>
            <p id="eventSplitHint" class="muted tiny"></p>
            <div id="eventRooms" class="event-rooms"></div>
          </div>
        </div>
      </section>
    </div>

'''
anchor = '    <div class="page" id="page-trend" data-page="trend">'
if 'id="page-event"' not in s:
    assert anchor in s, 'trend page anchor missing'
    s = s.replace(anchor, page_html + anchor, 1)

tab_anchor = '      <button type="button" class="tab" data-page="trend"><span class="tab-ico">📈</span><span class="tab-txt">动态</span></button>'
tab_new = tab_anchor + '\n      <button type="button" class="tab" data-page="event"><span class="tab-ico">📅</span><span class="tab-txt">活动</span></button>'
if 'data-page="event"' not in s:
    assert tab_anchor in s, 'trend tab anchor missing'
    s = s.replace(tab_anchor, tab_new, 1)
open(p, 'w', encoding='utf-8').write(s)

# ---------- extra.css ----------
p = os.path.join(BASE, 'public', 'extra.css')
s = open(p, encoding='utf-8').read()
if '/* ===== 群聚活动 ===== */' not in s:
    css = '''

/* ===== 群聚活动 ===== */
.tabbar{ grid-template-columns:repeat(8, minmax(0,1fr)); }
.event-toolbar{ display:flex; align-items:center; gap:8px; margin:6px 0 10px; }
.event-toolbar select{ width:auto; height:34px; margin:0; padding:0 10px; font-size:13px; border-radius:10px; }
.event-toolbar .btn-ghost{ height:34px; }
.event-list{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }
@media (max-width:760px){ .event-list{ grid-template-columns:1fr; } }
.event-item{ text-align:left; font-family:inherit; border:1px solid rgba(214,182,206,.55); border-radius:14px; padding:12px 14px; background:rgba(255,255,255,.5); cursor:pointer; transition:transform .15s, box-shadow .15s; }
.event-item:hover{ transform:translateY(-1px); box-shadow:0 8px 18px rgba(120,70,110,.12); }
.event-item h3{ margin:0 0 4px; font-size:15px; }
.event-when{ font-size:12px; color:#6b6273; }
.event-badges{ display:flex; flex-wrap:wrap; gap:6px; margin:6px 0 10px; }
.event-badge{ font-size:11px; font-weight:700; padding:3px 9px; border-radius:999px; background:rgba(255,233,243,.9); color:#b0467a; }
.event-badge.off{ background:rgba(230,228,236,.85); color:#6b6478; }
.event-badge.closed{ background:rgba(255,239,214,.95); color:#a66a12; }
.event-detail-head{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.event-detail-head h2{ margin:0; }
.event-detail-head .btn-ghost{ margin-left:auto; }
.event-sub{ margin:14px 0 6px; font-size:14px; }
.event-grid{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }
@media (max-width:820px){ .event-grid{ grid-template-columns:1fr; } }
.event-parts{ list-style:none; margin:4px 0 0; padding:0; display:flex; flex-direction:column; gap:6px; }
.event-part{ display:flex; align-items:center; justify-content:space-between; gap:8px; font-size:13px; padding:7px 10px; border-radius:10px; background:rgba(255,255,255,.5); border:1px solid rgba(226,204,220,.5); }
.event-part.unmatched{ color:#8a8295; background:rgba(244,242,248,.6); }
.event-part .tag{ margin-left:6px; font-size:11px; font-weight:700; padding:1px 7px; border-radius:999px; background:rgba(232,80,143,.12); color:#b0467a; }
.event-rooms{ display:grid; gap:10px; margin-top:8px; }
.event-room{ border:1px solid rgba(214,182,206,.55); border-radius:14px; padding:10px 12px; background:rgba(255,255,255,.5); }
.event-room h4{ margin:0 0 4px; font-size:14px; }
.room-scoreline{ font-size:12px; color:#6b6273; }
.room-split-row .primary{ width:auto; margin:0; height:34px; padding:0 18px; }
html[data-theme="dark"] .event-item,
html[data-theme="dark"] .event-part,
html[data-theme="dark"] .event-room{ background:rgba(38,30,46,.55); border-color:rgba(90,74,104,.6); }
html[data-theme="dark"] .event-when,
html[data-theme="dark"] .room-scoreline{ color:#bfb4cd; }
html[data-theme="dark"] .event-badge.off{ background:rgba(70,60,82,.7); color:#cfc4da; }
'''
    s += css
open(p, 'w', encoding='utf-8').write(s)

# ---------- app.js ----------
p = os.path.join(BASE, 'public', 'app.js')
s = open(p, encoding='utf-8').read()

old = "        else if (key === 'trend') { loadTrend(); }"
new = old + "\n        else if (key === 'event') { if (window.__loadEventList) window.__loadEventList(); }"
if "key === 'event'" not in s:
    assert old in s, 'lazy anchor missing'
    s = s.replace(old, new, 1)

module = '''

/* ===== 群聚活动（看板公开 API） ===== */
(() => {
  const $ = (id) => document.getElementById(id);
  let events = [];
  let currentId = '';
  let eventMode = 'rooms';

  const escapeHtml = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function fmtRange(ev) {
    const f = (iso) => {
      if (!iso) return '';
      const d = new Date(iso);
      if (isNaN(d.getTime())) return '';
      return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    };
    const a = f(ev.starts_at), b = f(ev.ends_at);
    return a ? (b ? a + ' → ' + b : a) : '时间待定';
  }

  function badgeOf(ev) {
    if (ev.lifecycle === 'cancelled' || ev.status === 'cancelled') return ['已取消', 'off'];
    if (ev.registration_open) return ['报名中', ''];
    if (ev.lifecycle === 'ended' || ev.status === 'finished' || ev.phase === 'ended') return ['已结束', 'off'];
    return ['已截止', 'closed'];
  }

  async function jget(url) {
    const res = await fetch(url, { headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || ('请求失败 ' + res.status));
    return data;
  }

  async function jpost(url, body) {
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || ('请求失败 ' + res.status));
    return data;
  }

  async function loadEventList() {
    const err = $('eventError');
    if (err) err.hidden = true;
    const lc = ($('eventLifecycle') && $('eventLifecycle').value) || '';
    try {
      const data = await jget('/api/qgroup/events?limit=50' + (lc ? '&lifecycle=' + encodeURIComponent(lc) : ''));
      events = data.events || [];
      renderEventList();
    } catch (e) {
      events = [];
      renderEventList();
      if (err) { err.textContent = e.message || '活动加载失败'; err.hidden = false; }
    }
  }

  function renderEventList() {
    const box = $('eventList');
    if (!box) return;
    box.innerHTML = events.map((ev) => {
      const b = badgeOf(ev);
      const counts = ev.counts || {};
      return '<button type="button" class="event-item" data-id="' + escapeHtml(ev.id) + '">'
        + '<h3>' + escapeHtml(ev.title || '未命名活动') + '</h3>'
        + '<div class="event-when">' + escapeHtml(fmtRange(ev)) + (ev.location ? ' · ' + escapeHtml(ev.location) : '') + '</div>'
        + '<div class="event-badges" style="margin:8px 0 0">'
        + '<span class="event-badge ' + b[1] + '">' + b[0] + '</span>'
        + '<span class="event-badge off">正式 ' + (counts.confirmed || 0) + ' 人</span>'
        + (counts.waiting ? '<span class="event-badge off">候补 ' + counts.waiting + '</span>' : '')
        + '</div></button>';
    }).join('');
    const empty = $('eventEmpty');
    if (empty) empty.hidden = events.length > 0;
    box.querySelectorAll('.event-item').forEach((btn) => btn.addEventListener('click', () => openEvent(btn.dataset.id)));
  }

  async function openEvent(id) {
    currentId = id;
    let payload;
    try {
      payload = await jget('/api/qgroup/event?id=' + encodeURIComponent(id));
    } catch (e) {
      alert(e.message || '活动详情加载失败');
      return;
    }
    renderDetail(payload);
    if ($('eventListCard')) $('eventListCard').hidden = true;
    if ($('eventDetailCard')) $('eventDetailCard').hidden = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function renderDetail(p) {
    const ev = p.event || {};
    const b = badgeOf(ev);
    if ($('eventTitle')) $('eventTitle').textContent = ev.title || '活动';
    if ($('eventMeta')) $('eventMeta').textContent = [fmtRange(ev), ev.location || ''].filter(Boolean).join(' · ');
    const counts = ev.counts || {};
    const badges = ['<span class="event-badge ' + b[1] + '">' + b[0] + '</span>'];
    badges.push('<span class="event-badge off">正式 ' + (counts.confirmed || 0) + '</span>');
    if (counts.waiting) badges.push('<span class="event-badge off">候补 ' + counts.waiting + '</span>');
    if (p.rooms_source) badges.push('<span class="event-badge off">看板' + (p.rooms_source === 'actual' ? '实际分房' : '预分房') + '</span>');
    if ((p.matched_qqs || []).length) badges.push('<span class="event-badge">可匹配 ' + p.matched_qqs.length + '</span>');
    if ($('eventBadges')) $('eventBadges').innerHTML = badges.join('');

    const parts = p.participants || [];
    if ($('eventPartCount')) $('eventPartCount').textContent = '共 ' + parts.length + ' 人';
    if ($('eventParticipants')) {
      $('eventParticipants').innerHTML = parts.map((x) => {
        const st = x.status === 'confirmed' ? '正式' : (x.status === 'waiting' ? '候补' : '待确认');
        const conf = x.confirmation_state === 'accepted' ? '已确认' : (x.confirmation_state === 'declined' ? '已拒绝' : '待确认');
        if (x.matched) {
          return '<li class="event-part"><span>' + escapeHtml(x.name || '') + '<span class="tag">' + escapeHtml(x.member_name) + ' · ' + x.count + ' 个词条</span></span><span>' + st + ' · ' + conf + '</span></li>';
        }
        return '<li class="event-part unmatched"><span>' + escapeHtml(x.name || '') + '<span class="tag" style="background:rgba(150,130,160,.16);color:#6b6478">未绑定看板 ID</span></span><span>' + st + '</span></li>';
      }).join('') || '<li class="muted tiny">暂无报名</li>';
    }

    const matchedCount = (p.matched_qqs || []).length;
    if ($('eventSplitHint')) {
      $('eventSplitHint').textContent = matchedCount > 1
        ? '已匹配 ' + matchedCount + ' 位本站群友，可自动分房；未绑定的 ' + (parts.length - matchedCount) + ' 人不会参与。'
        : '还没有可匹配的报名者：先在后台给群友填「看板 ID」。';
    }
    if ((p.rooms || []).length) renderRooms(p.rooms);
    else if ($('eventRooms')) $('eventRooms').innerHTML = '';
  }

  function renderRooms(rooms) {
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
  }

  async function doSplit() {
    if (!currentId) return;
    const hint = $('eventSplitHint');
    const val = parseInt(($('eventValue') && $('eventValue').value) || '0', 10);
    if (!val || val < 1) { if (hint) hint.textContent = eventMode === 'capacity' ? '先填每房几个人' : '先填要分几间房'; return; }
    try {
      if (hint) hint.textContent = '分房中…';
      const res = await jpost('/api/qgroup/split', { event_id: currentId, mode: eventMode, value: val });
      renderRooms(res.rooms || []);
      if (hint) hint.textContent = '已按' + (eventMode === 'capacity' ? '每房 ' + val + ' 人' : val + ' 间房') + '分好。';
    } catch (e) {
      if (hint) hint.textContent = e.message || '分房失败';
    }
  }

  function setEventMode(mode) {
    eventMode = mode === 'capacity' ? 'capacity' : 'rooms';
    document.querySelectorAll('#eventMode .room-mode-btn').forEach((btn) => {
      const on = btn.dataset.mode === eventMode;
      btn.classList.toggle('on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if ($('eventValue')) $('eventValue').value = eventMode === 'capacity' ? '4' : '2';
  }

  if ($('eventRefresh')) $('eventRefresh').addEventListener('click', loadEventList);
  if ($('eventLifecycle')) $('eventLifecycle').addEventListener('change', loadEventList);
  if ($('eventBack')) $('eventBack').addEventListener('click', () => {
    if ($('eventListCard')) $('eventListCard').hidden = false;
    if ($('eventDetailCard')) $('eventDetailCard').hidden = true;
    window.scrollTo({ top: 0 });
  });
  if ($('eventSplit')) $('eventSplit').addEventListener('click', doSplit);
  if ($('eventMode')) $('eventMode').addEventListener('click', (e) => { const btn = e.target.closest('.room-mode-btn'); if (btn) setEventMode(btn.dataset.mode); });
  window.__loadEventList = loadEventList;
})();
'''
if '群聚活动（看板公开 API）' not in s:
    s = s.rstrip() + module + '\n'
open(p, 'w', encoding='utf-8').write(s)

print('event patch ok')
